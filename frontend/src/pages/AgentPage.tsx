/**
 * AI Agent Page
 * Chat interface for LibraryAI with tool call visualization.
 */
import { useState, useRef, useEffect } from 'react';
import { agentAPI } from '../api';
import { Bot, Send, User, Wrench, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[];
  reasoning_steps?: any[];
}

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 Hi! I'm **LibraryAI**, your intelligent library assistant. I can help you:\n\n• 📚 Search and find books\n• ✅ Check book availability\n• 📖 Get personalized recommendations\n• 📊 View library statistics\n• 💰 Check your fines\n• 🔍 Explore the entity graph\n\nAsk me anything about the library!",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedTools, setExpandedTools] = useState<Set<number>>(new Set());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const res = await agentAPI.chat(userMessage);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.response,
        tool_calls: res.data.tool_calls,
        reasoning_steps: res.data.reasoning_steps,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  const toggleTools = (index: number) => {
    setExpandedTools(prev => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const suggestions = [
    "Which books about AI are available?",
    "Recommend books for me",
    "Show my borrowing history",
    "What are the library statistics?",
    "Check my fines",
    "Who are the most borrowed authors?",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Bot size={24} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            LibraryAI <Sparkles size={18} className="text-amber-400" />
          </h1>
          <p className="text-sm text-slate-400">Intelligent library assistant powered by AI</p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot size={16} className="text-white" />
              </div>
            )}
            <div className={`max-w-[75%] ${msg.role === 'user'
              ? 'bg-indigo-600/20 border border-indigo-500/20 rounded-2xl rounded-tr-md px-4 py-3'
              : 'glass-card px-4 py-3 !rounded-2xl !rounded-tl-md'
            }`}>
              <div className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed"
                   dangerouslySetInnerHTML={{
                     __html: msg.content
                       .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
                       .replace(/• /g, '<br/>• ')
                       .replace(/\n/g, '<br/>')
                   }}
              />

              {/* Tool calls */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/5">
                  <button onClick={() => toggleTools(i)} className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                    <Wrench size={12} />
                    {msg.tool_calls.length} tool{msg.tool_calls.length > 1 ? 's' : ''} used
                    {expandedTools.has(i) ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                  </button>
                  {expandedTools.has(i) && (
                    <div className="mt-2 space-y-2">
                      {msg.tool_calls.map((tc: any, j: number) => (
                        <div key={j} className="p-2 rounded-lg bg-white/[0.03] border border-white/5 text-xs">
                          <span className="text-indigo-300 font-mono">{tc.tool}</span>
                          {tc.result && !tc.result.error && (
                            <pre className="mt-1 text-slate-500 overflow-x-auto max-h-32 overflow-y-auto">
                              {JSON.stringify(tc.result, null, 2).slice(0, 500)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center flex-shrink-0 mt-1">
                <User size={16} className="text-white" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 animate-fadeIn">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="glass-card px-4 py-3 !rounded-2xl !rounded-tl-md">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                Thinking...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 my-4">
          {suggestions.map((s) => (
            <button key={s} onClick={() => { setInput(s); }} className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-slate-300 hover:bg-indigo-500/10 hover:border-indigo-500/20 hover:text-indigo-300 transition-all">
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-3 mt-4">
        <div className="flex-1 relative">
          <input
            type="text" value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask LibraryAI anything..."
            className="w-full px-5 py-3.5 rounded-2xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all pr-14"
            disabled={loading}
          />
        </div>
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-5 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
