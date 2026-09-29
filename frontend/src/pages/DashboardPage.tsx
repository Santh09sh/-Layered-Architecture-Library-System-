/**
 * Dashboard Page
 * Role-aware dashboard with stats, charts, and quick actions.
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { analyticsAPI, borrowAPI, finesAPI } from '../api';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { BookOpen, Users, AlertTriangle, Clock, DollarSign, TrendingUp, Bot, Share2 } from 'lucide-react';

const COLORS = ['#818cf8', '#a78bfa', '#c084fc', '#e879f9', '#f472b6', '#fb7185', '#f97316', '#facc15'];

export default function DashboardPage() {
  const { user, isLibrarian } = useAuth();
  const [overview, setOverview] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [myBorrows, setMyBorrows] = useState<any[]>([]);
  const [myFines, setMyFines] = useState<any[]>([]);

  useEffect(() => {
    if (isLibrarian) {
      analyticsAPI.overview().then(r => setOverview(r.data)).catch(() => {});
      analyticsAPI.borrowingTrends().then(r => setTrends(r.data.trends || [])).catch(() => {});
      analyticsAPI.popularCategories().then(r => setCategories(r.data.categories || [])).catch(() => {});
    }
    borrowAPI.myBorrows().then(r => setMyBorrows(r.data)).catch(() => {});
    finesAPI.my().then(r => setMyFines(r.data.filter((f: any) => f.status === 'PENDING'))).catch(() => {});
  }, [isLibrarian]);

  const statCards = isLibrarian && overview ? [
    { label: 'Total Books', value: overview.total_books, icon: BookOpen, color: 'from-indigo-500 to-blue-500' },
    { label: 'Active Members', value: overview.active_members, icon: Users, color: 'from-emerald-500 to-teal-500' },
    { label: 'Books Borrowed', value: overview.books_borrowed, icon: TrendingUp, color: 'from-amber-500 to-orange-500' },
    { label: 'Overdue', value: overview.overdue_books, icon: AlertTriangle, color: 'from-red-500 to-pink-500' },
    { label: 'Pending Reservations', value: overview.pending_reservations, icon: Clock, color: 'from-purple-500 to-violet-500' },
    { label: 'Fines Collected', value: `$${overview.total_fines_collected?.toFixed(2)}`, icon: DollarSign, color: 'from-cyan-500 to-blue-500' },
  ] : [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            Welcome back, <span className="gradient-text">{user?.name?.split(' ')[0]}</span>
          </h1>
          <p className="text-slate-400 mt-1">
            {isLibrarian ? 'Library Management Dashboard' : 'Your Library Dashboard'}
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/agent" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-medium hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg shadow-indigo-500/20">
            <Bot size={18} /> Ask LibraryAI
          </Link>
          <Link to="/graph" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/10 transition-all">
            <Share2 size={18} /> Entity Graph
          </Link>
        </div>
      </div>

      {/* Admin/Librarian Stats */}
      {isLibrarian && overview && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {statCards.map((stat) => (
            <div key={stat.label} className="glass-card p-4 group">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                <stat.icon size={20} className="text-white" />
              </div>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Charts Row */}
      {isLibrarian && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Borrowing Trends */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Borrowing Trends</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1e1e3a', border: '1px solid rgba(99,102,241,0.2)', borderRadius: '12px', color: '#e2e8f0' }}
                />
                <Bar dataKey="count" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#818cf8" />
                    <stop offset="100%" stopColor="#6366f1" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Popular Categories */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Popular Categories</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={categories} dataKey="count" nameKey="category" cx="50%" cy="50%" outerRadius={90} innerRadius={50} paddingAngle={3}>
                  {categories.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e1e3a', border: '1px solid rgba(99,102,241,0.2)', borderRadius: '12px', color: '#e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap gap-2 mt-2">
              {categories.slice(0, 6).map((c, i) => (
                <span key={c.category} className="flex items-center gap-1.5 text-xs text-slate-400">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                  {c.category}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Student: My Books & Fines */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Currently Borrowed */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Currently Borrowed</h3>
            <Link to="/borrowed" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">View all →</Link>
          </div>
          {myBorrows.length === 0 ? (
            <p className="text-slate-500 text-sm py-8 text-center">No active borrows. Visit the library to check out a book!</p>
          ) : (
            <div className="space-y-3">
              {myBorrows.slice(0, 5).map((b: any) => (
                <div key={b.id} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <div>
                    <p className="text-sm font-medium text-slate-200">{b.book_title}</p>
                    <p className="text-xs text-slate-500">Due: {new Date(b.due_date).toLocaleDateString()}</p>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                    b.status === 'OVERDUE' ? 'bg-red-500/15 text-red-400' :
                    b.status === 'ACTIVE' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-slate-500/15 text-slate-400'
                  }`}>
                    {b.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Fines */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Pending Fines</h3>
            <Link to="/fines" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Manage →</Link>
          </div>
          {myFines.length === 0 ? (
            <p className="text-slate-500 text-sm py-8 text-center">No pending fines. Keep up the good work! ✨</p>
          ) : (
            <div className="space-y-3">
              {myFines.map((f: any) => (
                <div key={f.id} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <div>
                    <p className="text-sm font-medium text-slate-200">${f.amount.toFixed(2)}</p>
                    <p className="text-xs text-slate-500">{f.reason}</p>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-400 font-medium">Pending</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
