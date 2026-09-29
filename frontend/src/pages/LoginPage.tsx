/**
 * Login Page
 * Handles both login and registration with a premium dark UI.
 */
import { useState } from 'react';
import { useAuth } from '../AuthContext';
import toast from 'react-hot-toast';
import { BookOpen, Mail, Lock, User, Hash, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', student_id: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isRegister) {
        await register(form);
        toast.success('Account created successfully!');
      } else {
        await login(form.email, form.password);
        toast.success('Welcome back!');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail?.message || err?.response?.data?.detail || 'Something went wrong';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0a0a0f] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      {/* Left panel - branding */}
      <div className="hidden lg:flex flex-1 items-center justify-center relative">
        <div className="max-w-md text-center px-8">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-indigo-500/20">
            <BookOpen size={36} className="text-white" />
          </div>
          <h1 className="text-5xl font-extrabold mb-4">
            <span className="gradient-text">LibraryOS</span>
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Intelligent Library Management with Entity Graph & AI-powered assistant
          </p>
          <div className="mt-12 grid grid-cols-3 gap-4">
            {[
              { label: 'Books', value: '20+' },
              { label: 'AI Agent', value: '🤖' },
              { label: 'Graph', value: '🕸️' },
            ].map((stat) => (
              <div key={stat.label} className="glass-card p-4 text-center">
                <p className="text-2xl font-bold text-indigo-300">{stat.value}</p>
                <p className="text-xs text-slate-500 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel - form */}
      <div className="flex-1 flex items-center justify-center px-6 relative z-10">
        <div className="w-full max-w-md">
          <div className="glass-card p-8">
            <div className="text-center mb-8">
              <div className="lg:hidden w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mx-auto mb-4">
                <BookOpen size={24} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white">
                {isRegister ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="text-slate-400 text-sm mt-2">
                {isRegister ? 'Join the university library' : 'Sign in to your library account'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegister && (
                <div className="relative">
                  <User size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text" placeholder="Full Name" required
                    value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
              )}

              <div className="relative">
                <Mail size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email" placeholder="Email address" required
                  value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                />
              </div>

              <div className="relative">
                <Lock size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="password" placeholder="Password" required minLength={6}
                  value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                />
              </div>

              {isRegister && (
                <div className="relative">
                  <Hash size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text" placeholder="Student ID (optional)"
                    value={form.student_id} onChange={e => setForm({ ...form, student_id: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
              )}

              <button
                type="submit" disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20"
              >
                {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => setIsRegister(!isRegister)}
                className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
              </button>
            </div>

            {!isRegister && (
              <div className="mt-6 pt-6 border-t border-white/5">
                <p className="text-xs text-slate-500 text-center mb-3">Quick Login</p>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'Admin', email: 'admin@library.edu', pass: 'admin123' },
                    { label: 'Librarian', email: 'sarah@library.edu', pass: 'librarian123' },
                    { label: 'Student', email: 'vishnu@university.edu', pass: 'student123' },
                  ].map((q) => (
                    <button
                      key={q.label}
                      type="button"
                      onClick={() => setForm({ ...form, email: q.email, password: q.pass })}
                      className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300 hover:bg-white/10 hover:border-indigo-500/30 transition-all"
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
