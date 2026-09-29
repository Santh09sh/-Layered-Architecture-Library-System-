/**
 * Book Detail Page
 * Full book details with copies, reviews, and related books from entity graph.
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { booksAPI, borrowAPI, reservationsAPI, reviewsAPI, graphAPI } from '../api';
import toast from 'react-hot-toast';
import { Star, BookOpen, MapPin, Copy, ArrowLeft, Send } from 'lucide-react';

export default function BookDetailPage() {
  const { id } = useParams();
  const [book, setBook] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [related, setRelated] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewForm, setReviewForm] = useState({ rating: 5, review_text: '' });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      booksAPI.get(Number(id)),
      reviewsAPI.forBook(Number(id)),
      graphAPI.bookGraph(Number(id)),
    ]).then(([bookRes, reviewRes, graphRes]) => {
      setBook(bookRes.data);
      setReviews(reviewRes.data);
      // Extract related books from graph
      const relatedNodes = graphRes.data.nodes?.filter((n: any) => n.type === 'Book' && n.id !== `book_${id}`) || [];
      setRelated(relatedNodes);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  const handleBorrow = async (copyId: number) => {
    try {
      await borrowAPI.borrow(copyId);
      toast.success('Book borrowed successfully!');
      const res = await booksAPI.get(Number(id));
      setBook(res.data);
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || 'Failed to borrow');
    }
  };

  const handleReserve = async () => {
    try {
      await reservationsAPI.create(Number(id));
      toast.success('Reservation created!');
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || 'Failed to reserve');
    }
  };

  const handleReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await reviewsAPI.create({ book_id: Number(id), ...reviewForm });
      toast.success('Review submitted!');
      const res = await reviewsAPI.forBook(Number(id));
      setReviews(res.data);
      setReviewForm({ rating: 5, review_text: '' });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to submit review');
    }
  };

  if (loading) return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 bg-white/5 rounded w-1/4" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="h-96 bg-white/5 rounded-2xl" />
        <div className="lg:col-span-2 space-y-4">
          <div className="h-8 bg-white/5 rounded w-2/3" />
          <div className="h-4 bg-white/5 rounded w-1/3" />
          <div className="h-32 bg-white/5 rounded" />
        </div>
      </div>
    </div>
  );

  if (!book) return <p className="text-slate-400">Book not found.</p>;

  const availableCopies = book.copies?.filter((c: any) => c.status === 'AVAILABLE') || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      <Link to="/books" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-indigo-300 transition-colors">
        <ArrowLeft size={16} /> Back to catalogue
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cover */}
        <div className="glass-card p-6 flex items-center justify-center">
          <div className="w-full max-w-[280px] aspect-[2/3] rounded-xl bg-gradient-to-br from-indigo-900/50 to-purple-900/50 overflow-hidden flex items-center justify-center">
            {book.cover_image ? (
              <img src={book.cover_image} alt={book.title} className="w-full h-full object-cover" onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }} />
            ) : (
              <BookOpen size={64} className="text-indigo-400/30" />
            )}
          </div>
        </div>

        {/* Details */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-white">{book.title}</h1>
            <p className="text-lg text-slate-400 mt-1">
              by {book.authors?.map((a: any) => a.name).join(', ')}
            </p>
            <div className="flex items-center gap-4 mt-3 flex-wrap">
              <div className="flex items-center gap-1">
                <Star size={18} className="text-amber-400 fill-amber-400" />
                <span className="text-lg font-semibold text-white">{book.average_rating?.toFixed(1)}</span>
                <span className="text-sm text-slate-400">({book.total_ratings} reviews)</span>
              </div>
              {book.category && (
                <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-sm border border-indigo-500/20">
                  {book.category.name}
                </span>
              )}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                availableCopies.length > 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {availableCopies.length > 0 ? `${availableCopies.length} copies available` : 'All copies borrowed'}
              </span>
            </div>
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'ISBN', value: book.isbn },
              { label: 'Publisher', value: book.publisher?.name || 'N/A' },
              { label: 'Year', value: book.publication_year || 'N/A' },
              { label: 'Pages', value: book.pages || 'N/A' },
            ].map((info) => (
              <div key={info.label} className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                <p className="text-xs text-slate-500">{info.label}</p>
                <p className="text-sm font-medium text-slate-200 mt-1">{info.value}</p>
              </div>
            ))}
          </div>

          {/* Description */}
          {book.description && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-2">Description</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{book.description}</p>
            </div>
          )}

          {/* Copies Table */}
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-3">Copies</h3>
            <div className="space-y-2">
              {book.copies?.map((copy: any) => (
                <div key={copy.id} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <div className="flex items-center gap-4">
                    <Copy size={16} className="text-slate-500" />
                    <div>
                      <span className="text-sm text-slate-200">{copy.accession_number}</span>
                      {copy.location && (
                        <span className="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                          <MapPin size={12} /> {copy.location}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      copy.status === 'AVAILABLE' ? 'bg-emerald-500/15 text-emerald-400' :
                      copy.status === 'BORROWED' ? 'bg-amber-500/15 text-amber-400' : 'bg-slate-500/15 text-slate-400'
                    }`}>
                      {copy.status}
                    </span>
                    {copy.status === 'AVAILABLE' && (
                      <button onClick={() => handleBorrow(copy.id)} className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-500 transition-colors">
                        Borrow
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {availableCopies.length === 0 && (
              <button onClick={handleReserve} className="mt-3 px-4 py-2 rounded-xl bg-purple-600 text-white text-sm font-medium hover:bg-purple-500 transition-colors">
                Reserve This Book
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Related Books */}
      {related.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">Related Books</h3>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {related.map((node: any) => {
              const bid = node.id.replace('book_', '');
              return (
                <Link key={node.id} to={`/books/${bid}`} className="glass-card p-4 min-w-[200px] flex-shrink-0 hover:border-indigo-500/30 transition-all">
                  <p className="text-sm font-medium text-slate-200 line-clamp-2">{node.label}</p>
                  <p className="text-xs text-indigo-400 mt-2">{node.properties?.isbn || ''}</p>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Reviews */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Review List */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Reviews ({reviews.length})</h3>
          {reviews.length === 0 ? (
            <p className="text-slate-500 text-sm py-4">No reviews yet. Be the first to review!</p>
          ) : (
            <div className="space-y-4 max-h-80 overflow-y-auto">
              {reviews.map((r: any) => (
                <div key={r.id} className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-200">{r.user_name || 'Anonymous'}</span>
                    <div className="flex items-center gap-1">
                      <Star size={14} className="text-amber-400 fill-amber-400" />
                      <span className="text-sm text-slate-300">{r.rating}</span>
                    </div>
                  </div>
                  {r.review_text && <p className="text-xs text-slate-400 mt-2">{r.review_text}</p>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Write Review */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Write a Review</h3>
          <form onSubmit={handleReview} className="space-y-4">
            <div>
              <label className="text-sm text-slate-400 mb-2 block">Rating</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map(n => (
                  <button key={n} type="button" onClick={() => setReviewForm({ ...reviewForm, rating: n })}>
                    <Star size={24} className={`transition-colors ${n <= reviewForm.rating ? 'text-amber-400 fill-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
              </div>
            </div>
            <textarea
              placeholder="Share your thoughts about this book..."
              value={reviewForm.review_text} onChange={e => setReviewForm({ ...reviewForm, review_text: e.target.value })}
              className="w-full p-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 resize-none h-28"
            />
            <button type="submit" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-500 transition-colors">
              <Send size={16} /> Submit Review
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
