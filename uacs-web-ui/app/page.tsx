import { Suspense } from 'react';
import { SearchView } from '@/components/search-view';

export default function HomePage() {
  return (
    <div className="container mx-auto px-6 py-8">
      <Suspense fallback={<div>Loading...</div>}>
        <SearchView />
      </Suspense>
    </div>
  );
}