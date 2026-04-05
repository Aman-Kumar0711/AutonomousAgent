import json
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from ..config import DATA_DIR, DB_PATH, EXPORT_DIR
from .models import Base, Business, OutreachRecord, WebsiteAudit


class DatabaseManager:
    def __init__(self, db_path: Path | None = None):
        db_path = db_path or DB_PATH
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_business(self, data: dict) -> Business:
        with self.get_session() as session:
            existing = None
            if data.get("website"):
                existing = (
                    session.query(Business)
                    .filter(Business.website == data["website"])
                    .first()
                )

            if existing:
                for key, value in data.items():
                    if value is not None and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now(timezone.utc)
                session.flush()
                session.refresh(existing)
                return existing

            business = Business(**data)
            session.add(business)
            session.flush()
            session.refresh(business)
            return business

    def get_business(self, business_id: int) -> Business | None:
        with self.get_session() as session:
            biz = session.get(Business, business_id)
            if biz:
                session.expunge(biz)
            return biz

    def get_all_businesses(
        self, status: str | None = None, domain: str | None = None
    ) -> list[Business]:
        with self.get_session() as session:
            query = session.query(Business)
            if status:
                query = query.filter(Business.status == status)
            if domain:
                query = query.filter(Business.domain == domain)
            results = query.order_by(Business.created_at.desc()).all()
            for biz in results:
                session.expunge(biz)
            return results

    def get_businesses_without_audit(self) -> list[Business]:
        with self.get_session() as session:
            subquery = session.query(WebsiteAudit.business_id).distinct()
            results = (
                session.query(Business)
                .filter(
                    Business.id.notin_(subquery),
                    Business.website.isnot(None),
                    Business.website != "",
                )
                .all()
            )
            for biz in results:
                session.expunge(biz)
            return results

    def get_businesses_without_outreach(self) -> list[Business]:
        with self.get_session() as session:
            subquery = session.query(OutreachRecord.business_id).distinct()
            results = (
                session.query(Business)
                .filter(
                    Business.id.notin_(subquery),
                    Business.email.isnot(None),
                    Business.email != "",
                    Business.status.in_(["new", "audited"]),
                )
                .all()
            )
            for biz in results:
                session.expunge(biz)
            return results

    def add_audit(self, business_id: int, audit_data: dict) -> WebsiteAudit:
        with self.get_session() as session:
            audit_data["business_id"] = business_id
            audit = WebsiteAudit(**audit_data)
            session.add(audit)

            business = session.get(Business, business_id)
            if business and business.status == "new":
                business.status = "audited"

            session.flush()
            session.refresh(audit)
            return audit

    def get_audit(self, business_id: int) -> WebsiteAudit | None:
        with self.get_session() as session:
            audit = (
                session.query(WebsiteAudit)
                .filter(WebsiteAudit.business_id == business_id)
                .order_by(WebsiteAudit.audited_at.desc())
                .first()
            )
            if audit:
                session.expunge(audit)
            return audit

    def add_outreach(self, business_id: int, outreach_data: dict) -> OutreachRecord:
        with self.get_session() as session:
            outreach_data["business_id"] = business_id
            outreach = OutreachRecord(**outreach_data)
            session.add(outreach)

            business = session.get(Business, business_id)
            if business:
                business.status = "contacted"

            session.flush()
            session.refresh(outreach)
            return outreach

    def update_outreach_status(self, outreach_id: int, status: str) -> None:
        with self.get_session() as session:
            outreach = session.get(OutreachRecord, outreach_id)
            if outreach:
                outreach.status = status
                if status == "sent":
                    outreach.email_sent = True
                    outreach.email_sent_at = datetime.now(timezone.utc)
                elif status == "followed_up":
                    outreach.follow_up_count += 1
                    outreach.last_follow_up_at = datetime.now(timezone.utc)

    def get_stats(self) -> dict:
        with self.get_session() as session:
            total = session.query(func.count(Business.id)).scalar() or 0
            by_status = dict(
                session.query(Business.status, func.count(Business.id))
                .group_by(Business.status)
                .all()
            )
            audited = session.query(func.count(WebsiteAudit.id)).scalar() or 0
            contacted = (
                session.query(func.count(OutreachRecord.id))
                .filter(OutreachRecord.email_sent.is_(True))
                .scalar()
                or 0
            )
            avg_score = (
                session.query(func.avg(WebsiteAudit.overall_score)).scalar()
            )
            by_domain = dict(
                session.query(Business.domain, func.count(Business.id))
                .filter(Business.domain.isnot(None))
                .group_by(Business.domain)
                .all()
            )
            by_source = dict(
                session.query(Business.source, func.count(Business.id))
                .filter(Business.source.isnot(None))
                .group_by(Business.source)
                .all()
            )

            return {
                "total_businesses": total,
                "by_status": by_status,
                "total_audited": audited,
                "total_contacted": contacted,
                "average_audit_score": round(avg_score, 1) if avg_score else 0,
                "by_domain": by_domain,
                "by_source": by_source,
            }

    def get_businesses_by_domain(self) -> dict[str, list[Business]]:
        with self.get_session() as session:
            businesses = session.query(Business).all()
            grouped: dict[str, list[Business]] = defaultdict(list)
            for biz in businesses:
                session.expunge(biz)
                key = biz.domain or "other"
                grouped[key].append(biz)
            return dict(grouped)

    def export_to_json(self, output_dir: Path | None = None) -> None:
        output_dir = output_dir or EXPORT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        def _serialize_dt(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with self.get_session() as session:
            businesses = session.query(Business).all()
            businesses_data = []
            for biz in businesses:
                audit = (
                    session.query(WebsiteAudit)
                    .filter(WebsiteAudit.business_id == biz.id)
                    .order_by(WebsiteAudit.audited_at.desc())
                    .first()
                )
                outreach = (
                    session.query(OutreachRecord)
                    .filter(OutreachRecord.business_id == biz.id)
                    .order_by(OutreachRecord.created_at.desc())
                    .first()
                )
                entry = {
                    "id": biz.id,
                    "name": biz.name,
                    "domain": biz.domain,
                    "website": biz.website,
                    "email": biz.email,
                    "phone": biz.phone,
                    "address": biz.address,
                    "city": biz.city,
                    "state": biz.state,
                    "rating": biz.rating,
                    "review_count": biz.review_count,
                    "source": biz.source,
                    "category": biz.category,
                    "status": biz.status,
                    "created_at": biz.created_at.isoformat() if biz.created_at else None,
                }
                if audit:
                    entry["audit"] = {
                        "overall_score": audit.overall_score,
                        "seo_score": audit.seo_score,
                        "page_speed_score": audit.page_speed_score,
                        "has_ssl": audit.has_ssl,
                        "is_mobile_friendly": audit.is_mobile_friendly,
                        "issues": audit.issues,
                        "load_time_seconds": audit.load_time_seconds,
                        "audited_at": audit.audited_at.isoformat() if audit.audited_at else None,
                    }
                if outreach:
                    entry["outreach"] = {
                        "status": outreach.status,
                        "email_sent": outreach.email_sent,
                        "email_sent_at": outreach.email_sent_at.isoformat() if outreach.email_sent_at else None,
                        "follow_up_count": outreach.follow_up_count,
                        "template_used": outreach.template_used,
                    }
                businesses_data.append(entry)

            with open(output_dir / "businesses.json", "w") as f:
                json.dump(businesses_data, f, indent=2, default=_serialize_dt)

            stats = self.get_stats()
            with open(output_dir / "stats.json", "w") as f:
                json.dump(stats, f, indent=2, default=_serialize_dt)

            domain_groups = defaultdict(list)
            for biz in businesses_data:
                key = biz.get("domain") or "other"
                domain_groups[key].append(biz)
            with open(output_dir / "by_domain.json", "w") as f:
                json.dump(dict(domain_groups), f, indent=2, default=_serialize_dt)
