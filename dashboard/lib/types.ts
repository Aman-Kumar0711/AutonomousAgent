export interface Issue {
  issue: string;
  impact: 'high' | 'medium' | 'low';
  category: 'seo' | 'security' | 'performance' | 'ux' | 'marketing' | 'business_tools' | 'accessibility';
  description: string;
  recommendation: string;
  business_impact: string;
}

export interface Audit {
  overall_score: number;
  seo_score: number;
  page_speed_score: number;
  has_ssl: boolean;
  is_mobile_friendly: boolean;
  load_time_seconds: number;
  audited_at: string;
  issues: Issue[];
  has_analytics?: boolean;
  has_contact_form?: boolean;
  has_social_links?: boolean;
  has_sitemap?: boolean;
  has_robots_txt?: boolean;
  has_favicon?: boolean;
}

export interface Outreach {
  status: 'pending' | 'sent' | 'opened' | 'replied' | 'bounced';
  email_sent: boolean;
  email_sent_at: string | null;
  follow_up_count: number;
}

export interface Business {
  id: number;
  name: string;
  domain: string;
  website: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  rating: number;
  review_count: number;
  source: string;
  category: string;
  status: 'new' | 'audited' | 'contacted' | 'replied' | 'converted';
  created_at: string;
  audit: Audit | null;
  outreach: Outreach | null;
}

export interface Stats {
  total_leads: number;
  total_audited: number;
  total_contacted: number;
  total_replied: number;
  total_converted: number;
  average_score: number;
  domains_covered: number;
  issues_found: number;
  emails_sent: number;
  response_rate: number;
}

export interface DomainGroup {
  domain: string;
  count: number;
  avg_score: number;
  businesses: Business[];
}
