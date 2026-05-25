import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'FinStatement AI - IFRS Financial Statement Automation',
  description: 'AI-powered financial statement preparation for accounting firms',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
