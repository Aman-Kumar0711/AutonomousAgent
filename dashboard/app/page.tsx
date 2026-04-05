'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Users,
  Search,
  Mail,
  TrendingUp,
  ExternalLink,
  ArrowRight,
  BarChart3,
  Globe,
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import StatsCard from '@/components/StatsCard';
import { Business, Stats, DomainGroup } from '@/lib/types';
import { formatDate, getScoreColor, slugify } from '@/lib/data';

export default function DashboardPage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [domains, setDomains] = useState<DomainGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [bizRes, statsRes, domainRes] = await Promise.all([
          fetch('/data/businesses.json'),
          fetch('/data/stats.json'),
          fetch('/data/by_domain.json'),
        ]);

        if (bizRes.ok) setBusinesses(await bizRes.json());
        if (statsRes.ok) setStats(await statsRes.json());
        if (domainRes.ok) setDomains(await domainRes.json());
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <>
        <Navbar />
        <main className="pt-24 px-6 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse">
                <div className="w-12 h-12 bg-slate-200 rounded-xl mb-4" />
                <div className="h-8 bg-slate-200 rounded w-20 mb-2" />
                <div className="h-4 bg-slate-100 rounded w-28" />
              </div>
            ))}
          </div>
        </main>
      </>
    );
  }

  const recentBusinesses = [...businesses]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 8);

  const maxDomainCount = Math.max(...(domains.map(d => d.count) || [1]));

  return (
    <>
      <Navbar />
      <main className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">Overview of your lead generation pipeline</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatsCard icon={Users} label="Total Leads" value={stats?.total_leads ?? businesses.length} color="primary" delay={0} />
          <StatsCard icon={Search} label="Audited" value={stats?.total_audited ?? 0} color="green" delay={1} />
          <StatsCard icon={Mail} label="Contacted" value={stats?.total_contacted ?? 0} color="purple" delay={2} />
          <StatsCard icon={TrendingUp} label="Avg Score" value={stats?.average_score ?? 0} suffix="/100" color="yellow" delay={3} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl border border-slate-200">
              <div className="flex items-center justify-between p-6 border-b border-slate-100">
                <h2 className="text-lg font-semibold text-slate-900">Recent Businesses</h2>
                <Link
                  href="/businesses"
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
                >
                  View all <ArrowRight className="w-4 h-4" />
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-100">
                      <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-3">Business</th>
                      <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-3">Domain</th>
                      <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-3">Score</th>
                      <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-3">Status</th>
                      <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-6 py-3">Date</th>
                      <th className="px-6 py-3" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {recentBusinesses.map((biz) => (
                      <tr key={biz.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-slate-900 text-sm">{biz.name}</p>
                            <p className="text-xs text-slate-400">{biz.city}, {biz.state}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
                            {biz.domain}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {biz.audit ? (
                            <span
                              className="text-sm font-bold"
                              style={{ color: getScoreColor(biz.audit.overall_score) }}
                            >
                              {biz.audit.overall_score}
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={biz.status} />
                        </td>
                        <td className="px-6 py-4 text-xs text-slate-500">
                          {formatDate(biz.created_at)}
                        </td>
                        <td className="px-6 py-4">
                          {biz.audit && (
                            <Link
                              href={`/audit/${biz.id}/${slugify(biz.name)}`}
                              className="text-primary-600 hover:text-primary-700"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Link>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {businesses.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  <Globe className="w-10 h-10 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No businesses yet. Run the agent to start collecting leads.</p>
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-6">Industry Breakdown</h2>
              <div className="space-y-4">
                {domains.slice(0, 8).map((domain) => (
                  <div key={domain.domain}>
                    <div className="flex items-center justify-between text-sm mb-1.5">
                      <span className="font-medium text-slate-700 capitalize">{domain.domain}</span>
                      <span className="text-slate-500">{domain.count} leads</span>
                    </div>
                    <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-700"
                        style={{ width: `${(domain.count / maxDomainCount) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
                {domains.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-4">No data yet</p>
                )}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6 mt-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Stats</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Emails Sent</span>
                  <span className="font-semibold text-slate-900">{stats?.emails_sent ?? 0}</span>
                </div>
                <div className="h-px bg-slate-100" />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Response Rate</span>
                  <span className="font-semibold text-slate-900">{stats?.response_rate ?? 0}%</span>
                </div>
                <div className="h-px bg-slate-100" />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Issues Found</span>
                  <span className="font-semibold text-slate-900">{stats?.issues_found ?? 0}</span>
                </div>
                <div className="h-px bg-slate-100" />
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-500">Domains Covered</span>
                  <span className="font-semibold text-slate-900">{stats?.domains_covered ?? 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    new: 'bg-slate-100 text-slate-600',
    audited: 'bg-blue-100 text-blue-700',
    contacted: 'bg-purple-100 text-purple-700',
    replied: 'bg-green-100 text-green-700',
    converted: 'bg-emerald-100 text-emerald-700',
  };

  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${styles[status] || styles.new}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
