/**
 * Books Page
 * Book catalogue with search, filtering, and card display.
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { booksAPI, categoriesAPI } from '../api';
import { Search, Filter, Star, BookOpen, ChevronDown } from 'lucide-react';

export default function BooksPage() {
  const [books, setBooks] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [availableOnly, setAvailableOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (search) params.q = search;
      if (selectedCategory) params.category_id = selectedCategory;
      if (availableOnly) params.available_only = true;
      const res = await booksAPI.list(params);
      setBooks(res.data);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBooks(); }, [selectedCategory, availableOnly]);
  useEffect(() => { categoriesAPI.list().then(r => setCategories(r.data)).catch(() => {}); }, []);
  useEffect(() => {
    const timeout = setTimeout(fetchBooks, 400);
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Book Catalogue</h1>
          <p className="text-slate-400 mt-1">Browse and discover our collection</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text" placeholder="Search books by title, ISBN, or description..."
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
          />
        </div>
        <select
          value={selectedCategory || ''} onChange={e => setSelectedCategory(e.target.value ? Number(e.target.value) : undefined)}
          className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-slate-300 focus:outline-none focus:border-indigo-500/50 transition-all appearance-none min-w-[200px]"
        >
          <option value="">All Categories</option>
          {categories.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <label className="flex items-center gap-2 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-slate-300 cursor-pointer hover:bg-white/10 transition-all">
          <input type="checkbox" checked={availableOnly} onChange={e => setAvailableOnly(e.target.checked)} className="accent-indigo-500" />
          <span className="text-sm whitespace-nowrap">Available only</span>
        </label>
      </div>

      {/* Book Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="glass-card p-5 animate-pulse">
              <div className="w-full h-48 bg-white/5 rounded-xl mb-4" />
              <div className="h-4 bg-white/5 rounded w-3/4 mb-2" />
              <div className="h-3 bg-white/5 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : books.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <BookOpen size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400 text-lg">No books found</p>
          <p className="text-slate-500 text-sm mt-1">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {books.map((book: any) => (
            <Link key={book.id} to={`/books/${book.id}`} className="glass-card p-5 group block">
              {/* Cover */}
              <div className="w-full h-48 rounded-xl bg-gradient-to-br from-indigo-900/50 to-purple-900/50 mb-4 overflow-hidden flex items-center justify-center relative">
                {book.cover_image ? (
                  <img src={book.cover_image} alt={book.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                ) : null}
                <BookOpen size={40} className="text-indigo-400/30 absolute" />
              </div>

              {/* Info */}
              <h3 className="text-sm font-semibold text-white line-clamp-2 group-hover:text-indigo-300 transition-colors">{book.title}</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                {book.authors?.map((a: any) => a.name).join(', ') || 'Unknown Author'}
              </p>
              {book.category && (
                <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                  {book.category.name}
                </span>
              )}

              {/* Rating & Availability */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Star size={14} className="text-amber-400 fill-amber-400" />
                  <span className="text-sm font-medium text-slate-300">{book.average_rating?.toFixed(1)}</span>
                </div>
                <span className={`text-xs font-medium ${book.available_copies > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {book.available_copies > 0 ? `${book.available_copies} available` : 'Unavailable'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
