/**
 * Layout Component
 * Main app shell with sidebar navigation and top bar.
 */
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useState, useEffect } from 'react';
import { notificationsAPI } from '../api';
import {
  LayoutDashboard, BookOpen, RotateCcw, DollarSign, Share2, Bot,
  LogOut, Bell, Menu, X, ChevronRight,
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { path: '/books', icon: BookOpen, label: 'Library' },
  { path: '/borrowed', icon: RotateCcw, label: 'Circulation' },
  { path: '/fines', icon: DollarSign, label: 'Fines' },
  { path: '/graph', icon: Share2, label: 'Entity Graph' },
  { path: '/agent', icon: Bot, label: 'LibraryAI' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    notificationsAPI.unreadCount().then(r => setUnreadCount(r.data.count)).catch(() => {});
  }, []);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0a0f]">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300 flex flex-col border-r border-white/5 bg-[#0d0d1a]`}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-white/5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
            L
          </div>
          {sidebarOpen && (
            <div className="animate-fadeIn">
              <h1 className="text-lg font-bold gradient-text">LibraryOS</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest">Intelligent Library</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                ${isActive
                  ? 'bg-indigo-500/15 text-indigo-300 shadow-lg shadow-indigo-500/5'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`
              }
            >
              <item.icon size={20} className="flex-shrink-0" />
              {sidebarOpen && <span className="animate-fadeIn">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-white/5 p-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {user?.name?.charAt(0)}
            </div>
            {sidebarOpen && (
              <div className="animate-fadeIn min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-200 truncate">{user?.name}</p>
                <p className="text-xs text-slate-500">{user?.role}</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 border-b border-white/5 bg-[#0d0d1a]/80 backdrop-blur-xl flex items-center justify-between px-6">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-slate-400 hover:text-slate-200 transition-colors">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center gap-4">
            <button className="relative text-slate-400 hover:text-slate-200 transition-colors">
              <Bell size={20} />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center text-white font-bold">
                  {unreadCount}
                </span>
              )}
            </button>
            <button onClick={handleLogout} className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors text-sm">
              <LogOut size={18} />
              {sidebarOpen && 'Logout'}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
