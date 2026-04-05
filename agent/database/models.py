from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), default="US")
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    audits: Mapped[list["WebsiteAudit"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    outreach_records: Mapped[list["OutreachRecord"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Business(id={self.id}, name='{self.name}', status='{self.status}')>"


class WebsiteAudit(Base):
    __tablename__ = "website_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    has_ssl: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_mobile_friendly: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    page_speed_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seo_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    has_meta_description: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_proper_title: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_h1: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_alt_tags: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_sitemap: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_robots_txt: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_analytics: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_social_links: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_contact_form: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_chat_widget: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_structured_data: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_favicon: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_open_graph: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_responsive_design: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    load_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    issues: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    overall_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    audited_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    business: Mapped["Business"] = relationship(back_populates="audits")

    def __repr__(self) -> str:
        return f"<WebsiteAudit(id={self.id}, business_id={self.business_id}, score={self.overall_score})>"


class OutreachRecord(Base):
    __tablename__ = "outreach_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    email_sent: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    email_subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email_body_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    last_follow_up_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    business: Mapped["Business"] = relationship(back_populates="outreach_records")

    def __repr__(self) -> str:
        return f"<OutreachRecord(id={self.id}, business_id={self.business_id}, status='{self.status}')>"
