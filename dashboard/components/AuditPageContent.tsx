'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Globe,
  MapPin,
  Phone,
  Star,
  Clock,
  Search,
  Zap,
  FileText,
  Rocket,
} from 'lucide-react';
import ScoreGauge from '@/components/ScoreGauge';
import IssueCard from '@/components/IssueCard';
import ChecklistItem from '@/components/ChecklistItem';
import CTASection from '@/components/CTASection';
import { Business } from '@/lib/types';
import { getScoreColor } from '@/lib/data';

export default function AuditPageContent({ id }: { id: string }) {
  const [business, setBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/data/businesses.json');
        if (res.ok) {
          const businesses: Business[] = await res.json();
          const found = businesses.find((b) => b.id === Number(id));
          setBusiness(found || null);
        }
      } catch (err) {
        console.error('Failed to load business:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-sm text-slate-500">Loading your audit report...</p>
        </div>
      </div>
    );
  }

  if (!business || !business.audit) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-slate-400" />
          </div>
          <h1 className="text-xl font-bold text-slate-900 mb-2">Report Not Found</h1>
          <p className="text-slate-500 text-sm">
            This audit report doesn&apos;t exist or hasn&apos;t been generated yet.
          </p>
        </div>
      </div>
    );
  }

  const { audit } = business;
  const scoreColor = getScoreColor(audit.overall_score);

  const checklist = [
    { label: 'SSL Certificate (HTTPS)', passed: audit.has_ssl, description: audit.has_ssl ? 'Your site is secured with SSL' : 'Your site is not secure — visitors see warnings' },
    { label: 'Mobile Friendly', passed: audit.is_mobile_friendly, description: audit.is_mobile_friendly ? 'Works well on all devices' : 'Not optimized for mobile devices' },
    { label: 'Analytics Installed', passed: audit.has_analytics ?? false, description: audit.has_analytics ? 'Tracking visitor behavior' : 'No analytics — you\'re flying blind' },
    { label: 'Contact Form', passed: audit.has_contact_form ?? false, description: audit.has_contact_form ? 'Easy for customers to reach you' : 'Visitors can\'t easily contact you' },
    { label: 'Social Media Links', passed: audit.has_social_links ?? false, description: audit.has_social_links ? 'Connected to social profiles' : 'Missing social media integration' },
    { label: 'XML Sitemap', passed: audit.has_sitemap ?? false, description: audit.has_sitemap ? 'Search engines can find your pages' : 'Search engines may miss your pages' },
    { label: 'Robots.txt', passed: audit.has_robots_txt ?? false, description: audit.has_robots_txt ? 'Proper search engine directives' : 'No search engine guidance file' },
    { label: 'Favicon', passed: audit.has_favicon ?? false, description: audit.has_favicon ? 'Professional browser tab icon' : 'Missing browser tab icon' },
  ];

  const scoreBreakdown = [
    { label: 'SEO', score: audit.seo_score, icon: Search },
    { label: 'Page Speed', score: audit.page_speed_score, icon: Zap },
  ];

  const businessToolIssues = audit.issues.filter((i) => i.category === 'business_tools');
  const technicalIssues = audit.issues.filter((i) => i.category !== 'business_tools');
  const highIssues = technicalIssues.filter((i) => i.impact === 'high').length;
  const medIssues = technicalIssues.filter((i) => i.impact === 'medium').length;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-900">AuditPro</span>
          </div>
          <span className="text-xs text-slate-400">Website Performance Report</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10"
        >
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">
            Website Audit Report
          </h1>
          <p className="text-lg text-slate-500 mb-6">
            Prepared for <span className="font-semibold text-slate-700">{business.name}</span>
          </p>

          <div className="flex flex-wrap items-center gap-4 text-sm text-slate-500">
            {business.website && (
              <a href={business.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 hover:text-primary-600 transition-colors">
                <Globe className="w-4 h-4" /> {business.website.replace(/^https?:\/\//, '')}
              </a>
            )}
            {business.city && (
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4" /> {business.city}, {business.state}
              </span>
            )}
            {business.phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="w-4 h-4" /> {business.phone}
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
              {business.rating} ({business.review_count} reviews)
            </span>
          </div>
        </motion.div>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-10 text-center mb-8"
        >
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">
            Overall Website Health
          </h2>
          <ScoreGauge score={audit.overall_score} size={220} strokeWidth={14} />
          <p className="mt-6 text-slate-500 max-w-md mx-auto text-sm leading-relaxed">
            {audit.overall_score < 40
              ? 'Your website has critical issues that are likely costing you customers. Immediate attention is recommended.'
              : audit.overall_score < 70
              ? 'Your website has several areas that need improvement to compete effectively online.'
              : 'Your website is performing well, but there are still opportunities for improvement.'}
          </p>
        </motion.section>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8"
        >
          <QuickStat label="SEO Score" value={`${audit.seo_score}/100`} color={getScoreColor(audit.seo_score)} icon={Search} />
          <QuickStat label="Page Speed" value={`${audit.page_speed_score}/100`} color={getScoreColor(audit.page_speed_score)} icon={Zap} />
          <QuickStat label="Load Time" value={`${audit.load_time_seconds}s`} color={audit.load_time_seconds <= 3 ? '#22c55e' : '#ef4444'} icon={Clock} />
          <QuickStat label="Issues Found" value={`${audit.issues.length}`} color={audit.issues.length > 5 ? '#ef4444' : '#eab308'} icon={FileText} />
        </motion.div>

        {businessToolIssues.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mb-10"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                <Rocket className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Growth Opportunities</h2>
                <p className="text-sm text-slate-500 mt-0.5">
                  Tools &amp; features that can bring you more customers
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {businessToolIssues.map((issue, idx) => (
                <IssueCard key={`bt-${idx}`} issue={issue} index={idx} />
              ))}
            </div>
          </motion.section>
        )}

        {technicalIssues.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mb-10"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Technical Issues</h2>
                <p className="text-sm text-slate-500 mt-1">
                  {highIssues > 0 && <span className="text-red-600 font-medium">{highIssues} critical</span>}
                  {highIssues > 0 && medIssues > 0 && ' · '}
                  {medIssues > 0 && <span className="text-yellow-600 font-medium">{medIssues} moderate</span>}
                  {(highIssues > 0 || medIssues > 0) && ' · '}
                  {technicalIssues.length - highIssues - medIssues > 0 && (
                    <span className="text-slate-500">{technicalIssues.length - highIssues - medIssues} minor</span>
                  )}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {technicalIssues
                .sort((a, b) => {
                  const order: Record<string, number> = { high: 0, medium: 1, low: 2 };
                  return (order[a.impact] ?? 3) - (order[b.impact] ?? 3);
                })
                .map((issue, idx) => (
                  <IssueCard key={idx} issue={issue} index={idx} />
                ))}
            </div>
          </motion.section>
        )}

        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-10"
        >
          <h2 className="text-xl font-bold text-slate-900 mb-2">What You&apos;re Missing</h2>
          <p className="text-sm text-slate-500 mb-6">
            Essential features every modern website should have
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            {checklist.map((item, idx) => (
              <ChecklistItem
                key={idx}
                label={item.label}
                passed={item.passed}
                description={item.description}
                index={idx}
              />
            ))}
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl border border-slate-200 p-8 mb-10"
        >
          <h2 className="text-xl font-bold text-slate-900 mb-6">Score Breakdown</h2>
          <div className="space-y-6">
            {scoreBreakdown.map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between text-sm mb-2">
                  <div className="flex items-center gap-2">
                    <item.icon className="w-4 h-4 text-slate-400" />
                    <span className="font-medium text-slate-700">{item.label}</span>
                  </div>
                  <span className="font-bold" style={{ color: getScoreColor(item.score) }}>
                    {item.score}/100
                  </span>
                </div>
                <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${item.score}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    className="h-full rounded-full"
                    style={{ backgroundColor: getScoreColor(item.score) }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-xs text-slate-400 mb-10"
        >
          Report generated on {new Date(audit.audited_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </motion.p>
      </main>

      <CTASection businessName={business.name} />

      <footer className="bg-slate-900 text-slate-400 py-8">
        <div className="max-w-4xl mx-auto px-6 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} Aman Kumar. All rights reserved.</p>
          <p className="mt-1 text-slate-500">
            This report was generated automatically. Results may vary.
          </p>
          <p className="mt-2">
            <a href="mailto:amanchahar175@gmail.com" className="text-primary-400 hover:text-primary-300 transition-colors">
              amanchahar175@gmail.com
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

function QuickStat({
  label,
  value,
  color,
  icon: Icon,
}: {
  label: string;
  value: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 text-center">
      <Icon className="w-5 h-5 mx-auto mb-2 text-slate-400" />
      <p className="text-2xl font-bold" style={{ color }}>
        {value}
      </p>
      <p className="text-xs text-slate-500 mt-1">{label}</p>
    </div>
  );
}
