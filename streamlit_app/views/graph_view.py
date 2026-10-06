"""
Entity Graph Page
Interactive graph visualization using Plotly network graph.
"""

import streamlit as st
import plotly.graph_objects as go
import math


# Node colors matching the React frontend
NODE_COLORS = {
    "User": {"bg": "#3b82f6", "label": "👤"},
    "Book": {"bg": "#8b5cf6", "label": "📖"},
    "Author": {"bg": "#f59e0b", "label": "✍️"},
    "Publisher": {"bg": "#10b981", "label": "🏢"},
    "Category": {"bg": "#f43f5e", "label": "🏷️"},
    "BookCopy": {"bg": "#6366f1", "label": "📄"},
}


def render(api):
    """Render the entity graph page."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="margin-bottom: 2px !important;">🕸️ Entity Graph</h1>
    <p style="color: #64748b; font-size: 15px !important; margin-top: 0;">
        Explore relationships between library entities
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────────────────
    col_search, col_btn_search, col_btn_my = st.columns([3, 1, 1])

    with col_search:
        search_query = st.text_input(
            "Search entities",
            placeholder="Search entities (e.g., 'Machine Learning', 'Robert Martin')...",
            label_visibility="collapsed",
            key="graph_search",
        )

    with col_btn_search:
        search_clicked = st.button("🔍 Search Graph", use_container_width=True, key="graph_search_btn")

    with col_btn_my:
        my_clicked = st.button("👤 My Graph", use_container_width=True, key="graph_my_btn")

    # ── Node Type Filters ─────────────────────────────────────────────────
    filter_cols = st.columns(7)
    node_types = ["All", "User", "Book", "Author", "Category", "Publisher", "BookCopy"]

    if "graph_filter" not in st.session_state:
        st.session_state.graph_filter = "All"

    for idx, ntype in enumerate(node_types):
        with filter_cols[idx]:
            emoji = NODE_COLORS.get(ntype, {}).get("label", "📊") if ntype != "All" else "📊"
            if st.button(f"{emoji} {ntype}", key=f"filter_{ntype}", use_container_width=True):
                st.session_state.graph_filter = ntype

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Load Graph Data ───────────────────────────────────────────────────
    graph_data = None

    if search_clicked and search_query.strip():
        try:
            graph_data = api.search_graph(search_query.strip())
        except Exception as e:
            st.error(f"Search failed: {e}")
    elif my_clicked or ("graph_data_cache" not in st.session_state):
        try:
            graph_data = api.my_graph()
        except Exception as e:
            st.error(f"Failed to load graph: {e}")

    # Cache the data
    if graph_data:
        st.session_state.graph_data_cache = graph_data
    elif "graph_data_cache" in st.session_state:
        graph_data = st.session_state.graph_data_cache

    if not graph_data:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 24px;">
            <div style="font-size: 48px; margin-bottom: 16px;">🕸️</div>
            <h3 style="color: #94a3b8;">No graph data</h3>
            <p style="color: #64748b; font-size: 13px !important; margin-top: 4px;">
                Search for entities or borrow books to see your graph
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Process Graph Data ────────────────────────────────────────────────
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.info("No nodes to display.")
        return

    # Apply filter
    active_filter = st.session_state.graph_filter
    if active_filter != "All":
        filtered_ids = {n["id"] for n in nodes if n.get("type") == active_filter}
        nodes = [n for n in nodes if n["id"] in filtered_ids]
        edges = [e for e in edges if e.get("source") in filtered_ids and e.get("target") in filtered_ids]

    if not nodes:
        st.info(f"No {active_filter} nodes found in the graph.")
        return

    # ── Node Stats ────────────────────────────────────────────────────────
    all_nodes = graph_data.get("nodes", [])
    type_counts = {}
    for n in all_nodes:
        t = n.get("type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    stat_cols = st.columns(len(type_counts) + 1)
    with stat_cols[0]:
        st.markdown(f"""
        <div class="glass-card" style="padding: 10px 14px; text-align: center;">
            <div style="font-size: 18px !important; font-weight: 700; color: #e2e8f0;">{len(all_nodes)}</div>
            <div style="font-size: 11px !important; color: #64748b;">Total Nodes</div>
        </div>
        """, unsafe_allow_html=True)
    for idx, (ntype, count) in enumerate(type_counts.items()):
        with stat_cols[idx + 1]:
            color = NODE_COLORS.get(ntype, {}).get("bg", "#64748b")
            emoji = NODE_COLORS.get(ntype, {}).get("label", "📊")
            st.markdown(f"""
            <div class="glass-card" style="padding: 10px 14px; text-align: center; border-left: 3px solid {color};">
                <div style="font-size: 18px !important; font-weight: 700; color: {color};">{count}</div>
                <div style="font-size: 11px !important; color: #64748b;">{emoji} {ntype}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Build Plotly Network Graph ────────────────────────────────────────
    # Create node positions using circular layout
    node_map = {n["id"]: idx for idx, n in enumerate(nodes)}
    n_nodes = len(nodes)

    positions = {}
    for i, node in enumerate(nodes):
        angle = (2 * math.pi * i) / n_nodes
        radius = max(2, n_nodes * 0.3)
        positions[node["id"]] = (radius * math.cos(angle), radius * math.sin(angle))

    # Edge traces
    edge_x = []
    edge_y = []
    edge_labels = []

    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src in positions and tgt in positions:
            x0, y0 = positions[src]
            x1, y1 = positions[tgt]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_labels.append(edge.get("relationship", ""))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.2, color="rgba(100,100,140,0.4)"),
        hoverinfo="none",
        mode="lines",
    )

    # Node traces (grouped by type for coloring)
    node_traces = []
    for ntype, config in NODE_COLORS.items():
        type_nodes = [n for n in nodes if n.get("type") == ntype]
        if not type_nodes:
            continue

        node_x = [positions[n["id"]][0] for n in type_nodes]
        node_y = [positions[n["id"]][1] for n in type_nodes]
        node_text = [f"{config['label']} {n.get('label', n['id'])}" for n in type_nodes]
        hover_text = [
            f"<b>{n.get('label', n['id'])}</b><br>Type: {ntype}<br>ID: {n['id']}"
            for n in type_nodes
        ]

        trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            marker=dict(
                size=22,
                color=config["bg"],
                line=dict(width=2, color="rgba(255,255,255,0.2)"),
                symbol="circle",
            ),
            text=node_text,
            textposition="bottom center",
            textfont=dict(size=10, color="#94a3b8", family="Inter"),
            hovertext=hover_text,
            hoverinfo="text",
            name=f"{config['label']} {ntype}",
        )
        node_traces.append(trace)

    # Create figure
    fig = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            plot_bgcolor="rgba(10,10,15,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#94a3b8", size=11),
            showlegend=True,
            legend=dict(
                bgcolor="rgba(0,0,0,0.3)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(size=11, color="#94a3b8"),
                x=1, y=1,
            ),
            hovermode="closest",
            margin=dict(l=20, r=20, t=20, b=20),
            height=550,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            dragmode="pan",
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})

    # ── Edge List ─────────────────────────────────────────────────────────
    if edges:
        with st.expander(f"📋 Relationships ({len(edges)})"):
            for edge in edges[:20]:
                src_label = next((n.get("label", n["id"]) for n in graph_data.get("nodes", []) if n["id"] == edge.get("source")), edge.get("source"))
                tgt_label = next((n.get("label", n["id"]) for n in graph_data.get("nodes", []) if n["id"] == edge.get("target")), edge.get("target"))
                rel = edge.get("relationship", "RELATED")
                st.markdown(f"""
                <div style="padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 13px !important;">
                    <span style="color: #e2e8f0; font-weight: 500;">{src_label}</span>
                    <span style="color: #818cf8; margin: 0 8px;">→ {rel} →</span>
                    <span style="color: #e2e8f0; font-weight: 500;">{tgt_label}</span>
                </div>
                """, unsafe_allow_html=True)
            if len(edges) > 20:
                st.caption(f"Showing 20 of {len(edges)} relationships")
