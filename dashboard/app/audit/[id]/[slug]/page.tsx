import AuditPageContent from '@/components/AuditPageContent';

export default function AuditPage({ params }: { params: { id: string; slug: string } }) {
  return <AuditPageContent id={params.id} />;
}
