'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Sidebar from '@/components/layout/Sidebar';
import { useAuthStore } from '@/lib/auth';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!isAuthenticated) router.push('/login');
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex">
        <Sidebar />
        <main className="ml-60 flex-1 min-h-screen">
          {children}
        </main>
      </div>
      <Toaster position="top-right" toastOptions={{ style: { fontSize: '14px' } }} />
    </QueryClientProvider>
  );
}
