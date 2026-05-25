import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: string | number | null | undefined, currency = 'EUR'): string {
  if (amount === null || amount === undefined) return '-';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '-';
  return new Intl.NumberFormat('en-IE', { style: 'currency', currency, minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(num);
}

export function formatNumber(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined) return '-';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '-';
  return new Intl.NumberFormat('en-IE', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(num);
}

export function formatDate(date: string | null | undefined): string {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function confidenceColor(confidence: string | number | null): string {
  const val = parseFloat(String(confidence || 0));
  if (val >= 0.85) return 'text-success-700 bg-success-50';
  if (val >= 0.6) return 'text-warning-700 bg-warning-50';
  return 'text-danger-700 bg-danger-50';
}

export function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    DRAFT: 'badge-neutral',
    IN_PROGRESS: 'badge-blue',
    REVIEW: 'badge-warning',
    COMPLETE: 'badge-success',
    PROCESSED: 'badge-success',
    PROCESSING: 'badge-blue',
    PENDING: 'badge-neutral',
    ERROR: 'badge-danger',
  };
  return map[status] || 'badge-neutral';
}
