'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  MagnifyingGlass, 
  ClockCounterClockwise, 
  Brain, 
  TreeStructure 
} from '@phosphor-icons/react';

const navItems = [
  {
    href: '/',
    label: 'Search',
    icon: MagnifyingGlass,
  },
  {
    href: '/timeline',
    label: 'Timeline',
    icon: ClockCounterClockwise,
  },
  {
    href: '/knowledge',
    label: 'Knowledge',
    icon: Brain,
  },
  {
    href: '/sessions',
    label: 'Sessions',
    icon: TreeStructure,
  },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-teal-600 text-white font-bold">
            U
          </div>
          <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
            UACS
          </h1>
        </div>
        
        <div className="ml-8 flex gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100'
                    : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-100'
                )}
              >
                <Icon size={20} weight={isActive ? 'bold' : 'regular'} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
