/**
 * Borrowed Books / Circulation Page
 * Shows active borrows, history, and provides return/renew actions.
 */
import { useState, useEffect } from 'react';
import { borrowAPI } from '../api';
import { useAuth } from '../AuthContext';
import toast from 'react-hot-toast';
import { RotateCcw, Clock, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

export default function BorrowedPage() {
  const { isLibrarian } = useAuth();
  const [activeTab, setActiveTab] = useState<'active' | 'history' | 'overdue'>('active');
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      let res;
      if (activeTab === 'active') res = await borrowAPI.myBorrows();
      else if (activeTab === 'history') res = await borrowAPI.history();
      else if (activeTab === 'overdue' && isLibrarian) res = await borrowAPI.overdue();
      else res = await borrowAPI.history();
      setRecords(res.data);
    } catch { } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, [activeTab]);

  const handleReturn = async (id: number) => {
    try {
      const res = await borrowAPI.return(id);
      if (res.data.fine) {
        toast(`Book returned. Fine: $${res.data.fine.amount.toFixed(2)} (${res.data.fine.days_overdue} days overdue)`, { icon: '💰' });
      } else {
        toast.success('Book returned successfully!');
      }
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || 'Failed to return');
    }
  };

  const handleRenew = async (id: number) => {
    try {
      await borrowAPI.renew(id);
      toast.success('Book renewed!');
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || 'Failed to renew');
    }
  };

  const tabs = [
    { id: 'active' as const, label: 'Active Borrows', icon: Clock },
    { id: 'history' as const, label: 'History', icon: RotateCcw },
    ...(isLibrarian ? [{ id: 'overdue' as const, label: 'Overdue', icon: AlertTriangle }] : []),
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-3xl font-bold text-white">Circulation</h1>
        <p className="text-slate-400 mt-1">Manage borrowed books, returns, and renewals</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/20'
                : 'text-slate-400 bg-white/5 border border-white/10 hover:bg-white/10'
            }`}
          >
            <tab.icon size={16} /> {tab.label}
          </button>
        ))}
      </div>

      {/* Records */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="glass-card p-4 animate-pulse">
              <div className="h-4 bg-white/5 rounded w-1/3 mb-2" />
              <div className="h-3 bg-white/5 rounded w-1/4" />
            </div>
          ))}
        </div>
      ) : records.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <RotateCcw size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400 text-lg">No records found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {records.map((record: any) => {
            const isOverdue = record.status === 'OVERDUE' || (record.status === 'ACTIVE' && new Date(record.due_date) < new Date());
            return (
              <div key={record.id} className="glass-card p-5 flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-white">{record.book_title || 'Unknown Book'}</h3>
                  <div className="flex items-center gap-4 mt-1 text-xs text-slate-400">
                    {record.user_name && <span>Borrower: {record.user_name}</span>}
                    <span>Borrowed: {new Date(record.borrowed_at).toLocaleDateString()}</span>
                    <span className={isOverdue ? 'text-red-400 font-medium' : ''}>
                      Due: {new Date(record.due_date).toLocaleDateString()}
                    </span>
                    {record.returned_at && <span>Returned: {new Date(record.returned_at).toLocaleDateString()}</span>}
                    {record.renewal_count > 0 && <span className="text-indigo-400">Renewed {record.renewal_count}x</span>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                    record.status === 'RETURNED' ? 'bg-emerald-500/15 text-emerald-400' :
                    isOverdue ? 'bg-red-500/15 text-red-400' :
                    'bg-amber-500/15 text-amber-400'
                  }`}>
                    {isOverdue && record.status === 'ACTIVE' ? 'OVERDUE' : record.status}
                  </span>
                  {record.status === 'ACTIVE' && (
                    <>
                      <button onClick={() => handleRenew(record.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300 hover:bg-white/10 transition-all">
                        <RefreshCw size={14} /> Renew
                      </button>
                      <button onClick={() => handleReturn(record.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-xs text-white font-medium hover:bg-indigo-500 transition-colors">
                        <CheckCircle size={14} /> Return
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
