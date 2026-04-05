import { Business, Stats, DomainGroup } from './types';

const BASE_PATH = process.env.NODE_ENV === 'production' ? '' : '';

export async function getBusinesses(): Promise<Business[]> {
  try {
    const res = await fetch(`${BASE_PATH}/data/businesses.json`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function getBusiness(id: number): Promise<Business | null> {
  const businesses = await getBusinesses();
  return businesses.find((b) => b.id === id) || null;
}

export async function getStats(): Promise<Stats> {
  try {
    const res = await fetch(`${BASE_PATH}/data/stats.json`);
    if (!res.ok) return getDefaultStats();
    return await res.json();
  } catch {
    return getDefaultStats();
  }
}

export async function getBusinessesByDomain(): Promise<DomainGroup[]> {
  try {
    const res = await fetch(`${BASE_PATH}/data/by_domain.json`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

function getDefaultStats(): Stats {
  return {
    total_leads: 0,
    total_audited: 0,
    total_contacted: 0,
    total_replied: 0,
    total_converted: 0,
    average_score: 0,
    domains_covered: 0,
    issues_found: 0,
    emails_sent: 0,
    response_rate: 0,
  };
}

export function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function getScoreColor(score: number): string {
  if (score >= 70) return '#22c55e';
  if (score >= 40) return '#eab308';
  return '#ef4444';
}

export function getScoreLabel(score: number): string {
  if (score >= 70) return 'Good';
  if (score >= 40) return 'Needs Work';
  return 'Critical';
}

export function getImpactColor(impact: string): string {
  switch (impact) {
    case 'high': return 'bg-red-100 text-red-700 border-red-200';
    case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    case 'low': return 'bg-slate-100 text-slate-600 border-slate-200';
    default: return 'bg-slate-100 text-slate-600 border-slate-200';
  }
}

export function getCategoryColor(category: string): string {
  switch (category) {
    case 'seo': return 'bg-blue-100 text-blue-700';
    case 'security': return 'bg-red-100 text-red-700';
    case 'performance': return 'bg-orange-100 text-orange-700';
    case 'ux': return 'bg-purple-100 text-purple-700';
    case 'marketing': return 'bg-green-100 text-green-700';
    default: return 'bg-slate-100 text-slate-600';
  }
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
