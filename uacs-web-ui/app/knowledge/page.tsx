import { Suspense } from 'react';
import { KnowledgeView } from '@/components/knowledge-view';

export default function KnowledgePage() {
  return (
    <div className="container mx-auto px-6 py-8">
      <Suspense fallback={<div>Loading...</div>}>
        <KnowledgeView />
      </Suspense>
    </div>
  );
}
