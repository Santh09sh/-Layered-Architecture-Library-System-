/**
 * API Client
 * Centralized HTTP client with JWT auth and error handling.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE = 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --- Auth ---
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  register: (data: { name: string; email: string; password: string; student_id?: string }) =>
    api.post('/api/auth/register', data),
  getProfile: () => api.get('/api/auth/me'),
};

// --- Books ---
export const booksAPI = {
  list: (params?: { q?: string; category_id?: number; available_only?: boolean; skip?: number; limit?: number }) =>
    api.get('/api/books', { params }),
  get: (id: number) => api.get(`/api/books/${id}`),
  create: (data: any) => api.post('/api/books', data),
  update: (id: number, data: any) => api.put(`/api/books/${id}`, data),
  delete: (id: number) => api.delete(`/api/books/${id}`),
};

// --- Authors ---
export const authorsAPI = {
  list: (params?: { q?: string }) => api.get('/api/authors', { params }),
  get: (id: number) => api.get(`/api/authors/${id}`),
  create: (data: any) => api.post('/api/authors', data),
};

// --- Categories ---
export const categoriesAPI = {
  list: () => api.get('/api/categories'),
  create: (data: any) => api.post('/api/categories', data),
};

// --- Publishers ---
export const publishersAPI = {
  list: () => api.get('/api/publishers'),
  create: (data: any) => api.post('/api/publishers', data),
};

// --- Circulation ---
export const borrowAPI = {
  borrow: (book_copy_id: number) => api.post('/api/borrow', { book_copy_id }),
  return: (record_id: number) => api.post(`/api/borrow/${record_id}/return`),
  renew: (record_id: number) => api.post(`/api/borrow/${record_id}/renew`),
  myBorrows: () => api.get('/api/borrow/my'),
  history: () => api.get('/api/borrow/history'),
  all: () => api.get('/api/borrow/all'),
  overdue: () => api.get('/api/borrow/overdue'),
  eligibility: () => api.get('/api/borrow/eligibility'),
};

// --- Reservations ---
export const reservationsAPI = {
  create: (book_id: number) => api.post('/api/reservations', { book_id }),
  my: () => api.get('/api/reservations/my'),
  cancel: (id: number) => api.delete(`/api/reservations/${id}`),
  all: () => api.get('/api/reservations/all'),
};

// --- Fines ---
export const finesAPI = {
  my: () => api.get('/api/fines/my'),
  pay: (id: number) => api.post(`/api/fines/${id}/pay`),
  all: () => api.get('/api/fines/all'),
};

// --- Reviews ---
export const reviewsAPI = {
  create: (data: { book_id: number; rating: number; review_text?: string }) =>
    api.post('/api/reviews', data),
  forBook: (book_id: number) => api.get(`/api/reviews/book/${book_id}`),
};

// --- Notifications ---
export const notificationsAPI = {
  list: () => api.get('/api/notifications'),
  unreadCount: () => api.get('/api/notifications/unread-count'),
  markRead: (id: number) => api.post(`/api/notifications/${id}/read`),
  markAllRead: () => api.post('/api/notifications/read-all'),
};

// --- Graph ---
export const graphAPI = {
  bookGraph: (id: number) => api.get(`/api/graph/book/${id}`),
  userGraph: (id: number) => api.get(`/api/graph/user/${id}`),
  myGraph: () => api.get('/api/graph/me'),
  search: (q: string) => api.get('/api/graph/search', { params: { q } }),
  recommendations: () => api.get('/api/graph/recommendations'),
};

// --- Agent ---
export const agentAPI = {
  chat: (message: string, conversation_history?: any[]) =>
    api.post('/api/agent/chat', { message, conversation_history }),
  tools: () => api.get('/api/agent/tools'),
};

// --- Analytics ---
export const analyticsAPI = {
  overview: () => api.get('/api/analytics/overview'),
  borrowingTrends: () => api.get('/api/analytics/borrowing-trends'),
  popularCategories: () => api.get('/api/analytics/popular-categories'),
  mostBorrowed: () => api.get('/api/analytics/most-borrowed'),
};

// --- Users ---
export const usersAPI = {
  list: (params?: { role?: string; q?: string }) => api.get('/api/users', { params }),
  get: (id: number) => api.get(`/api/users/${id}`),
};

export default api;
