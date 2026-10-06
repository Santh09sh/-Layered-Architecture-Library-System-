"""
Dashboard Page
Role-aware dashboard with analytics, stats, and quick actions.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render(api, is_librarian_user: bool):
    """Render the dashboard page."""
    user = st.session_state.user

    # ── Header ────────────────────────────────────────────────────────────
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        first_name = user.get("name", "User").split(" ")[0]
        st.markdown(f"""
        <h1 style="margin-bottom: 2px !important;">
            Welcome back, <span class="gradient-text">{first_name}</span>
        </h1>
        <p style="color: #64748b; font-size: 15px !important; margin-top: 0;">
            {"Library Management Dashboard" if is_librarian_user else "Your Library Dashboard"}
        </p>
        """, unsafe_allow_html=True)
    with col_actions:
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🤖 Ask AI", use_container_width=True, key="dash_ai"):
                st.session_state.current_page = "agent"
                st.rerun()
        with c2:
            if st.button("🕸️ Graph", use_container_width=True, key="dash_graph"):
                st.session_state.current_page = "graph"
                st.rerun()

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Librarian Analytics ───────────────────────────────────────────────
    if is_librarian_user:
        try:
            overview = api.analytics_overview()

            # Stat cards
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.metric("📚 Total Books", overview.get("total_books", 0))
            with c2:
                st.metric("👥 Active Members", overview.get("active_members", 0))
            with c3:
                st.metric("📖 Borrowed", overview.get("books_borrowed", 0))
            with c4:
                st.metric("⚠️ Overdue", overview.get("overdue_books", 0))
            with c5:
                st.metric("🕐 Reservations", overview.get("pending_reservations", 0))
            with c6:
                fines_val = overview.get("total_fines_collected", 0)
                st.metric("💵 Fines Collected", f"${fines_val:.2f}")

            st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

            # Charts Row
            chart_left, chart_right = st.columns(2)

            with chart_left:
                st.markdown("### 📈 Borrowing Trends")
                try:
                    trends_data = api.borrowing_trends()
                    trends = trends_data.get("trends", [])
                    if trends:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=[t["month"] for t in trends],
                            y=[t["count"] for t in trends],
                            marker=dict(
                                color=[t["count"] for t in trends],
                                colorscale=[[0, "#4f46e5"], [1, "#a855f7"]],
                            ),
                            text=[t["count"] for t in trends],
                            textposition="outside",
                            textfont=dict(size=12, color="#94a3b8"),
                        ))
                        fig.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter", color="#94a3b8", size=12),
                            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
                            margin=dict(l=40, r=20, t=20, b=40),
                            height=300,
                            showlegend=False,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No borrowing trend data available.")
                except Exception:
                    st.info("Unable to load borrowing trends.")

            with chart_right:
                st.markdown("### 📊 Popular Categories")
                try:
                    cat_data = api.popular_categories()
                    categories = cat_data.get("categories", [])
                    if categories:
                        colors = ["#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6", "#fb7185", "#f97316", "#facc15"]
                        fig = go.Figure()
                        fig.add_trace(go.Pie(
                            labels=[c["category"] for c in categories],
                            values=[c["count"] for c in categories],
                            hole=0.5,
                            marker=dict(colors=colors[:len(categories)]),
                            textinfo="label+percent",
                            textfont=dict(size=11, color="#e2e8f0"),
                            hovertemplate="<b>%{label}</b><br>Borrows: %{value}<extra></extra>",
                        ))
                        fig.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter", color="#94a3b8", size=12),
                            margin=dict(l=20, r=20, t=20, b=20),
                            height=300,
                            showlegend=False,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No category data available.")
                except Exception:
                    st.info("Unable to load category data.")

        except Exception as e:
            st.warning(f"Unable to load analytics: {e}")

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── User's Active Borrows & Fines ─────────────────────────────────────
    col_borrows, col_fines = st.columns(2)

    with col_borrows:
        st.markdown("### 📖 Currently Borrowed")
        try:
            my_borrows = api.my_borrows()
            if not my_borrows:
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 40px 24px;">
                    <div style="font-size: 32px; margin-bottom: 12px;">📚</div>
                    <p style="color: #64748b; font-size: 14px !important;">
                        No active borrows. Visit the catalogue to borrow a book!
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for b in my_borrows[:5]:
                    due = datetime.fromisoformat(b["due_date"].replace("Z", "+00:00"))
                    status = b.get("status", "ACTIVE")
                    if status == "ACTIVE" and due < datetime.now(due.tzinfo):
                        status = "OVERDUE"
                    badge = {
                        "ACTIVE": "badge-active",
                        "OVERDUE": "badge-overdue",
                    }.get(status, "badge-pending")
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 14px 18px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px !important; font-weight: 600; color: #e2e8f0;">
                                    {b.get("book_title", "Unknown")}
                                </div>
                                <div style="font-size: 12px !important; color: #64748b; margin-top: 2px;">
                                    Due: {due.strftime("%b %d, %Y")}
                                </div>
                            </div>
                            <span class="badge {badge}">{status}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if len(my_borrows) > 5:
                    st.caption(f"+ {len(my_borrows) - 5} more…")

                if st.button("View All Borrows →", key="dash_view_borrows"):
                    st.session_state.current_page = "circulation"
                    st.rerun()

        except Exception:
            st.info("Unable to load borrows.")

    with col_fines:
        st.markdown("### 💰 Pending Fines")
        try:
            my_fines = api.my_fines()
            pending_fines = [f for f in my_fines if f.get("status") == "PENDING"]

            if not pending_fines:
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 40px 24px;">
                    <div style="font-size: 32px; margin-bottom: 12px;">✨</div>
                    <p style="color: #34d399; font-size: 14px !important; font-weight: 600;">
                        No pending fines!
                    </p>
                    <p style="color: #64748b; font-size: 13px !important; margin-top: 4px;">
                        Keep up the good work!
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                total = sum(f.get("amount", 0) for f in pending_fines)
                st.markdown(f"""
                <div class="glass-card" style="padding: 14px 18px; margin-bottom: 12px; border-left: 3px solid #fbbf24;">
                    <div style="font-size: 12px !important; color: #64748b;">Total Pending</div>
                    <div style="font-size: 24px !important; font-weight: 700; color: #fbbf24;">${total:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                for f in pending_fines:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 14px 18px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px !important; font-weight: 600; color: #e2e8f0;">
                                    ${f.get("amount", 0):.2f}
                                </div>
                                <div style="font-size: 12px !important; color: #64748b; margin-top: 2px;">
                                    {f.get("reason", "Overdue fine")}
                                </div>
                            </div>
                            <span class="badge badge-pending">PENDING</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if st.button("Manage Fines →", key="dash_view_fines"):
                    st.session_state.current_page = "fines"
                    st.rerun()

        except Exception:
            st.info("Unable to load fines.")
