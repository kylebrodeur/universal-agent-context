import { Suspense } from 'react';
import { SessionsView } from '@/components/sessions-view';

export default function SessionsPage() {
  return (
    <div className="container mx-auto px-6 py-8">
      <Suspense fallback={<div>Loading...</div>}>
        <SessionsView />
      </Suspense>
    </div>
  );
}
