import type { Metadata } from 'next';
import { Figtree } from 'next/font/google';
import './globals.css';
import { Toaster } from '@/components/ui/sonner';
import { Navigation } from '@/components/navigation';

const figtree = Figtree({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'UACS - Universal Agent Context System',
  description: 'Semantic search, knowledge management, and conversation analytics',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={figtree.className}>
        <div className="flex h-screen flex-col">
          <Navigation />
          <main className="flex-1 overflow-auto bg-zinc-50 dark:bg-zinc-950">
            {children}
          </main>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
