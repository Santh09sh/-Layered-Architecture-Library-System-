/**
 * Entity Graph Page
 * Interactive graph visualization using ReactFlow.
 */
import { useState, useEffect, useCallback } from 'react';
import ReactFlow, { Controls, Background, MiniMap, Node, Edge, useNodesState, useEdgesState, MarkerType, Position } from 'reactflow';
import 'reactflow/dist/style.css';
import { graphAPI } from '../api';
import { useAuth } from '../AuthContext';
import { Search, Share2, User, BookOpen, PenTool, Building2, Tag, Copy } from 'lucide-react';

const NODE_COLORS: Record<string, { bg: string; border: string; icon: any }> = {
  User: { bg: '#3b82f6', border: '#60a5fa', icon: User },
  Book: { bg: '#8b5cf6', border: '#a78bfa', icon: BookOpen },
  Author: { bg: '#f59e0b', border: '#fbbf24', icon: PenTool },
  Publisher: { bg: '#10b981', border: '#34d399', icon: Building2 },
  Category: { bg: '#f43f5e', border: '#fb7185', icon: Tag },
  BookCopy: { bg: '#6366f1', border: '#818cf8', icon: Copy },
};

function CustomNode({ data }: { data: any }) {
  const config = NODE_COLORS[data.type] || { bg: '#64748b', border: '#94a3b8', icon: Share2 };
  const Icon = config.icon;
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-xl text-white text-xs font-medium shadow-lg"
         style={{ background: config.bg, border: `2px solid ${config.border}`, minWidth: 120 }}>
      <Icon size={14} />
      <div className="min-w-0">
        <p className="truncate max-w-[140px]">{data.label}</p>
        <p className="text-[9px] opacity-70">{data.type}</p>
      </div>
    </div>
  );
}

const nodeTypes = { custom: CustomNode };

export default function GraphPage() {
  const { user } = useAuth();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'my' | 'search'>('my');

  const loadMyGraph = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const res = await graphAPI.myGraph();
      buildGraph(res.data);
    } catch { } finally { setLoading(false); }
  };

  const handleSearch = async () => {
    if (!search.trim()) return;
    setLoading(true);
    setMode('search');
    try {
      const res = await graphAPI.search(search);
      buildGraph(res.data);
    } catch { } finally { setLoading(false); }
  };

  const buildGraph = (data: any) => {
    const gNodes = (data.nodes || []).map((n: any, i: number) => {
      const angle = (2 * Math.PI * i) / (data.nodes?.length || 1);
      const radius = Math.max(200, (data.nodes?.length || 1) * 30);
      return {
        id: n.id,
        type: 'custom',
        position: { x: 400 + radius * Math.cos(angle), y: 300 + radius * Math.sin(angle) },
        data: { label: n.label, type: n.type, properties: n.properties },
      } as Node;
    });

    const gEdges = (data.edges || []).map((e: any, i: number) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.relationship,
      type: 'smoothstep',
      animated: e.relationship === 'BORROWED',
      labelStyle: { fill: '#94a3b8', fontSize: 10, fontWeight: 500 },
      style: { stroke: '#4a4a6a', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#4a4a6a', width: 12, height: 12 },
    } as Edge));

    setNodes(gNodes);
    setEdges(gEdges);
  };

  useEffect(() => { loadMyGraph(); }, [user]);

  const nodeFilters = ['All', 'User', 'Book', 'Author', 'Category', 'Publisher', 'BookCopy'];
  const [filter, setFilter] = useState('All');

  const filteredNodes = filter === 'All' ? nodes : nodes.filter(n => n.data.type === filter);
  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

  return (
    <div className="space-y-4 animate-fadeIn h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Entity Graph</h1>
          <p className="text-slate-400 mt-1">Explore relationships between library entities</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text" placeholder="Search entities (e.g., 'Machine Learning', 'Robert Martin')..."
            value={search} onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 transition-all text-sm"
          />
        </div>
        <button onClick={handleSearch} className="px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-500 transition-colors">
          Search Graph
        </button>
        <button onClick={loadMyGraph} className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/10 transition-all">
          My Graph
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {nodeFilters.map(f => (
          <button
            key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === f ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/20' : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10'
            }`}
          >
            {f} {f !== 'All' && `(${nodes.filter(n => n.data.type === f).length})`}
          </button>
        ))}
      </div>

      {/* Graph */}
      <div className="glass-card rounded-2xl overflow-hidden flex-1" style={{ height: 'calc(100% - 160px)' }}>
        {loading ? (
          <div className="flex items-center justify-center h-full text-slate-400">Loading graph...</div>
        ) : filteredNodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500">
            <Share2 size={48} className="mb-4 text-slate-600" />
            <p className="text-lg">No graph data</p>
            <p className="text-sm mt-1">Search for entities or borrow books to see your graph</p>
          </div>
        ) : (
          <ReactFlow
            nodes={filteredNodes}
            edges={filteredEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            className="bg-[#0a0a0f]"
          >
            <Controls className="!bg-[#1e1e3a] !border-white/10 !rounded-xl [&_button]:!bg-[#1e1e3a] [&_button]:!border-white/10 [&_button]:!text-slate-300" />
            <Background color="#1e1e3a" gap={20} />
            <MiniMap
              nodeColor={(n) => NODE_COLORS[n.data?.type]?.bg || '#64748b'}
              maskColor="rgba(0,0,0,0.7)"
              className="!bg-[#0d0d1a] !border-white/10 !rounded-xl"
            />
          </ReactFlow>
        )}
      </div>
    </div>
  );
}
