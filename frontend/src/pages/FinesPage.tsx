/**
 * Fines Page
 * View and pay fines.
 */
import { useState, useEffect } from 'react';
import { finesAPI } from '../api';
import { useAuth } from '../AuthContext';
import toast from 'react-hot-toast';
import { DollarSign, CreditCard, CheckCircle } from 'lucide-react';

export default function FinesPage() {
  const { isLibrarian } = useAuth();
  const [fines, setFines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = isLibrarian ? finesAPI.all : finesAPI.my;
    fetch().then(r => setFines(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [isLibrarian]);

  const handlePay = async (id: number) => {
    try {
      await finesAPI.pay(id);
      toast.success('Fine paid!');
      setFines(fines.map(f => f.id === id ? { ...f, status: 'PAID' } : f));
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to pay fine');
    }
  };

  const totalPending = fines.filter(f => f.status === 'PENDING').reduce((acc, f) => acc + f.amount, 0);

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Fines</h1>
          <p className="text-slate-400 mt-1">View and manage library fines</p>
        </div>
        {totalPending > 0 && (
          <div className="glass-card px-5 py-3 flex items-center gap-3">
            <DollarSign size={20} className="text-amber-400" />
            <div>
              <p className="text-xs text-slate-400">Total Pending</p>
              <p className="text-xl font-bold text-amber-400">${totalPending.toFixed(2)}</p>
            </div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card p-4 animate-pulse"><div className="h-4 bg-white/5 rounded w-1/3" /></div>
          ))}
        </div>
      ) : fines.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <CheckCircle size={48} className="mx-auto text-emerald-500 mb-4" />
          <p className="text-slate-200 text-lg font-medium">No fines!</p>
          <p className="text-slate-400 text-sm mt-1">You're all clear. Keep up the good work!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {fines.map((fine: any) => (
            <div key={fine.id} className="glass-card p-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">${fine.amount.toFixed(2)}</p>
                <p className="text-xs text-slate-400 mt-1">{fine.reason}</p>
                <p className="text-xs text-slate-500 mt-0.5">{new Date(fine.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  fine.status === 'PAID' ? 'bg-emerald-500/15 text-emerald-400' :
                  fine.status === 'WAIVED' ? 'bg-blue-500/15 text-blue-400' :
                  'bg-amber-500/15 text-amber-400'
                }`}>
                  {fine.status}
                </span>
                {fine.status === 'PENDING' && (
                  <button onClick={() => handlePay(fine.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-xs text-white font-medium hover:bg-indigo-500 transition-colors">
                    <CreditCard size={14} /> Pay
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
