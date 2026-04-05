import fs from 'fs';
import path from 'path';
import AuditPageContent from '@/components/AuditPageContent';

interface Business {
  id: number;
  name: string;
  audit: unknown;
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function generateStaticParams() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'businesses.json');
    const data = fs.readFileSync(filePath, 'utf-8');
    const businesses: Business[] = JSON.parse(data);

    return businesses
      .filter((b) => b.audit !== null)
      .map((b) => ({
        id: String(b.id),
        slug: slugify(b.name),
      }));
  } catch {
    return [];
  }
}

export default function AuditPage({ params }: { params: { id: string; slug: string } }) {
  return <AuditPageContent id={params.id} />;
}
