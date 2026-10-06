"""
Circulation Page
Active borrows, history, overdue management with return/renew actions.
"""

import streamlit as st
from datetime import datetime


def render(api, is_librarian_user: bool):
    """Render the circulation page."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="margin-bottom: 2px !important;">🔄 Circulation</h1>
    <p style="color: #64748b; font-size: 15px !important; margin-top: 0;">
        Manage borrowed books, returns, and renewals
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_list = ["📖 Active Borrows", "📜 History"]
    if is_librarian_user:
        tab_list.append("⚠️ Overdue")

    tabs = st.tabs(tab_list)

    # ── Active Borrows Tab ────────────────────────────────────────────────
    with tabs[0]:
        try:
            records = api.my_borrows()
            _render_borrow_records(records, api, show_actions=True, tab_key="active")
        except Exception as e:
            st.error(f"Failed to load active borrows: {e}")

    # ── History Tab ───────────────────────────────────────────────────────
    with tabs[1]:
        try:
            records = api.borrow_history()
            _render_borrow_records(records, api, show_actions=False, tab_key="history")
        except Exception as e:
            st.error(f"Failed to load history: {e}")

    # ── Overdue Tab (Librarian only) ──────────────────────────────────────
    if is_librarian_user and len(tabs) > 2:
        with tabs[2]:
            try:
                records = api.overdue_borrows()
                _render_borrow_records(records, api, show_actions=True, tab_key="overdue")
            except Exception as e:
                st.error(f"Failed to load overdue records: {e}")


def _render_borrow_records(records: list, api, show_actions: bool, tab_key: str):
    """Render a list of borrow records."""

    if not records:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 40px; margin-bottom: 12px;">📋</div>
            <h3 style="color: #94a3b8;">No records found</h3>
            <p style="color: #64748b; font-size: 13px !important; margin-top: 4px;">
                No borrowing records in this category
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    for record in records:
        status = record.get("status", "UNKNOWN")
        due_str = record.get("due_date", "")
        is_overdue = False

        if due_str:
            try:
                due_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                due_display = due_dt.strftime("%b %d, %Y")
                if status == "ACTIVE" and due_dt < datetime.now(due_dt.tzinfo):
                    is_overdue = True
                    status = "OVERDUE"
            except Exception:
                due_display = due_str
        else:
            due_display = "N/A"

        borrowed_str = record.get("borrowed_at", "")
        if borrowed_str:
            try:
                borrowed_display = datetime.fromisoformat(borrowed_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
            except Exception:
                borrowed_display = borrowed_str
        else:
            borrowed_display = "N/A"

        returned_str = record.get("returned_at", "")
        returned_display = ""
        if returned_str:
            try:
                returned_display = datetime.fromisoformat(returned_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
            except Exception:
                returned_display = returned_str

        badge_cls = {
            "ACTIVE": "badge-active",
            "OVERDUE": "badge-overdue",
            "RETURNED": "badge-returned",
        }.get(status, "badge-pending")

        renewal_count = record.get("renewal_count", 0)
        renewal_html = f'<span style="font-size:12px; color:#818cf8; margin-left:12px;">🔄 Renewed {renewal_count}x</span>' if renewal_count > 0 else ""
        returned_html = f'<span style="font-size:12px; color:#64748b; margin-left:12px;">✅ Returned: {returned_display}</span>' if returned_display else ""
        borrower_html = ""
        if record.get("user_name"):
            borrower_html = f'<span style="font-size:12px; color:#64748b; margin-right:12px;">👤 {record["user_name"]}</span>'

        col_info, col_actions = st.columns([4, 1])

        with col_info:
            st.markdown(f"""
            <div class="glass-card" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 15px !important; font-weight: 600; color: #e2e8f0;">
                            {record.get("book_title", "Unknown Book")}
                        </div>
                        <div style="margin-top: 6px; display: flex; align-items: center; flex-wrap: wrap;">
                            {borrower_html}
                            <span style="font-size: 12px !important; color: #64748b; margin-right: 12px;">
                                📅 Borrowed: {borrowed_display}
                            </span>
                            <span style="font-size: 12px !important; color: {'#f87171; font-weight:600;' if is_overdue else '#64748b;'}">
                                ⏰ Due: {due_display}
                            </span>
                            {renewal_html}
                            {returned_html}
                        </div>
                    </div>
                    <span class="badge {badge_cls}">{status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_actions:
            if show_actions and record.get("status") == "ACTIVE":
                if st.button("🔄 Renew", key=f"renew_{tab_key}_{record['id']}", use_container_width=True):
                    try:
                        api.renew_book(record["id"])
                        st.success("Book renewed!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

                if st.button("✅ Return", key=f"return_{tab_key}_{record['id']}", use_container_width=True):
                    try:
                        result = api.return_book(record["id"])
                        if result and result.get("fine"):
                            fine = result["fine"]
                            st.warning(f"Book returned. Fine: ${fine['amount']:.2f} ({fine['days_overdue']} days overdue)")
                        else:
                            st.success("Book returned successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
