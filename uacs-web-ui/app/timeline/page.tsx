import { Suspense } from 'react';
import { TimelineView } from '@/components/timeline-view';

export default function TimelinePage() {
  return (
    <div className="container mx-auto px-6 py-8">
      <Suspense fallback={<div>Loading...</div>}>
        <TimelineView />
      </Suspense>
    </div>
  );
}
