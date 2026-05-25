export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-brand-700 to-brand-500 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">FinStatement AI</h1>
          <p className="text-brand-100 mt-1">IFRS Financial Statement Automation</p>
        </div>
        <div className="card p-8">{children}</div>
      </div>
    </div>
  );
}
