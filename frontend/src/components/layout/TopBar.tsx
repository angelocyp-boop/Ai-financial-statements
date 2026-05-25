'use client';
import { usePathname } from 'next/navigation';

const TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/clients': 'Clients',
  '/settings': 'Settings',
};

export default function TopBar({ title }: { title?: string }) {
  const pathname = usePathname();
  const resolved = title || TITLES[pathname] || 'FinStatement AI';
  return (
    <header className="h-14 border-b border-surface-200 bg-white flex items-center px-6 sticky top-0 z-20">
      <h1 className="text-sm font-semibold text-ink-900">{resolved}</h1>
    </header>
  );
}
