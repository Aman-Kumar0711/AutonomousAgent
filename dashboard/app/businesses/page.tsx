'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Search,
  SlidersHorizontal,
  ExternalLink,
  Globe,
  Star,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import { Business } from '@/lib/types';
import { formatDate, getScoreColor, slugify } from '@/lib/data';

type SortKey = 'name' | 'score' | 'created_at' | 'rating';
type SortDir = 'asc' | 'desc';

const ITEMS_PER_PAGE = 12;

export default function BusinessesPage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [domainFilter, setDomainFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [page, setPage] = useState(1);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/data/businesses.json');
        if (res.ok) setBusinesses(await res.json());
      } catch (err) {
        console.error('Failed to load businesses:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const domains = useMemo(
    () => Array.from(new Set(businesses.map((b) => b.domain))).sort(),
    [businesses]
  );

  const statuses = useMemo(
    () => Array.from(new Set(businesses.map((b) => b.status))).sort(),
    [businesses]
  );

  const filtered = useMemo(() => {
    let result = [...businesses];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (b) =>
          b.name.toLowerCase().includes(q) ||
          b.city.toLowerCase().includes(q) ||
          b.category.toLowerCase().includes(q) ||
          b.email.toLowerCase().includes(q)
      );
    }

    if (domainFilter !== 'all') {
      result = result.filter((b) => b.domain === domainFilter);
    }

    if (statusFilter !== 'all') {
      result = result.filter((b) => b.status === statusFilter);
    }

    result.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case 'name':
          cmp = a.name.localeCompare(b.name);
          break;
        case 'score':
          cmp = (a.audit?.overall_score ?? -1) - (b.audit?.overall_score ?? -1);
          break;
        case 'created_at':
          cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'rating':
          cmp = a.rating - b.rating;
          break;
      }
      return sortDir === 'desc' ? -cmp : cmp;
    });

    return result;
  }, [businesses, searchQuery, domainFilter, statusFilter, sortKey, sortDir]);

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
  const paginated = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  useEffect(() => {
    setPage(1);
  }, [searchQuery, domainFilter, statusFilter]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  return (
    <>
      <Navbar />
      <main className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Businesses</h1>
          <p className="text-slate-500 mt-1">
            {filtered.length} of {businesses.length} businesses
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 mb-6">
          <div className="p-4 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, city, category, or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div className="flex gap-3">
              <select
                value={domainFilter}
                onChange={(e) => setDomainFilter(e.target.value)}
                className="px-3 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
              >
                <option value="all">All Industries</option>
                {domains.map((d) => (
                  <option key={d} value={d}>
                    {d.charAt(0).toUpperCase() + d.slice(1)}
                  </option>
                ))}
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
              >
                <option value="all">All Statuses</option>
                {statuses.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse">
                <div className="h-5 bg-slate-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-slate-100 rounded w-1/2 mb-6" />
                <div className="h-8 bg-slate-100 rounded w-16" />
              </div>
            ))}
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2 mb-4">
              <SlidersHorizontal className="w-4 h-4 text-slate-400" />
              <span className="text-xs text-slate-500">Sort by:</span>
              {(['name', 'score', 'rating', 'created_at'] as SortKey[]).map((key) => (
                <button
                  key={key}
                  onClick={() => toggleSort(key)}
                  className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1 ${
                    sortKey === key
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-slate-500 hover:bg-slate-100'
                  }`}
                >
                  {key === 'created_at' ? 'Date' : key.charAt(0).toUpperCase() + key.slice(1)}
                  {sortKey === key && <ArrowUpDown className="w-3 h-3" />}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {paginated.map((biz) => (
                <BusinessCard key={biz.id} business={biz} />
              ))}
            </div>

            {filtered.length === 0 && (
              <div className="text-center py-16 text-slate-400">
                <Globe className="w-12 h-12 mx-auto mb-3 opacity-40" />
                <p className="font-medium">No businesses found</p>
                <p className="text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            )}

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter(p => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
                  .map((p, idx, arr) => (
                    <span key={p} className="flex items-center">
                      {idx > 0 && arr[idx - 1] !== p - 1 && (
                        <span className="px-1 text-slate-300">...</span>
                      )}
                      <button
                        onClick={() => setPage(p)}
                        className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                          p === page
                            ? 'bg-primary-600 text-white'
                            : 'text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        {p}
                      </button>
                    </span>
                  ))}
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </>
  );
}

function BusinessCard({ business }: { business: Business }) {
  const score = business.audit?.overall_score;
  const statusStyles: Record<string, string> = {
    new: 'bg-slate-100 text-slate-600',
    audited: 'bg-blue-100 text-blue-700',
    contacted: 'bg-purple-100 text-purple-700',
    replied: 'bg-green-100 text-green-700',
    converted: 'bg-emerald-100 text-emerald-700',
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-lg hover:border-slate-300 transition-all duration-300 group">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 text-base truncate">{business.name}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{business.category}</p>
        </div>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full shrink-0 ml-2 ${statusStyles[business.status] || statusStyles.new}`}>
          {business.status.charAt(0).toUpperCase() + business.status.slice(1)}
        </span>
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-500 mb-4">
        <span>{business.city}, {business.state}</span>
        <span className="text-slate-300">|</span>
        <span className="capitalize">{business.domain}</span>
      </div>

      <div className="flex items-center gap-4 mb-4">
        {score !== undefined && score !== null ? (
          <div className="flex items-center gap-2">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white"
              style={{ backgroundColor: getScoreColor(score) }}
            >
              {score}
            </div>
            <div>
              <p className="text-xs font-medium text-slate-700">Audit Score</p>
              <p className="text-xs text-slate-400">
                {business.audit?.issues.length ?? 0} issues
              </p>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-400">Not audited</div>
        )}

        <div className="flex items-center gap-1 ml-auto">
          <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
          <span className="text-sm font-medium text-slate-700">{business.rating}</span>
          <span className="text-xs text-slate-400">({business.review_count})</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {business.audit && (
          <Link
            href={`/audit/${business.id}/${slugify(business.name)}`}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-primary-50 text-primary-700 text-sm font-medium rounded-lg hover:bg-primary-100 transition-colors"
          >
            View Audit <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        )}
        {business.website && (
          <a
            href={business.website}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 border border-slate-200 rounded-lg text-slate-500 hover:bg-slate-50 transition-colors"
          >
            <Globe className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
}
