"""
Fines Page
View and pay library fines.
"""

import streamlit as st
from datetime import datetime


def render(api, is_librarian_user: bool):
    """Render the fines page."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="margin-bottom: 2px !important;">💰 Fines</h1>
    <p style="color: #64748b; font-size: 15px !important; margin-top: 0;">
        View and manage library fines
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Fetch Fines ───────────────────────────────────────────────────────
    try:
        if is_librarian_user:
            fines_list = api.all_fines()
        else:
            fines_list = api.my_fines()
    except Exception as e:
        st.error(f"Failed to load fines: {e}")
        return

    # ── Summary Card ──────────────────────────────────────────────────────
    pending_fines = [f for f in fines_list if f.get("status") == "PENDING"]
    paid_fines = [f for f in fines_list if f.get("status") == "PAID"]
    total_pending = sum(f.get("amount", 0) for f in pending_fines)
    total_paid = sum(f.get("amount", 0) for f in paid_fines)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏳ Pending", f"${total_pending:.2f}")
    with col2:
        st.metric("✅ Paid", f"${total_paid:.2f}")
    with col3:
        st.metric("📊 Total Fines", str(len(fines_list)))

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    # ── Fines List ────────────────────────────────────────────────────────
    if not fines_list:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 48px 24px;">
            <div style="font-size: 40px; margin-bottom: 12px;">✨</div>
            <h3 style="color: #34d399;">No fines!</h3>
            <p style="color: #64748b; font-size: 13px !important; margin-top: 4px;">
                You're all clear. Keep up the good work!
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    for fine in fines_list:
        status = fine.get("status", "PENDING")
        amount = fine.get("amount", 0)
        reason = fine.get("reason", "Overdue fine")
        created = fine.get("created_at", "")

        if created:
            try:
                created_display = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%b %d, %Y")
            except Exception:
                created_display = created
        else:
            created_display = "N/A"

        badge_cls = {
            "PAID": "badge-paid",
            "PENDING": "badge-pending",
            "WAIVED": "badge-active",
        }.get(status, "badge-pending")

        col_info, col_action = st.columns([4, 1])

        with col_info:
            st.markdown(f"""
            <div class="glass-card" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 18px !important; font-weight: 700; color: #e2e8f0;">
                            ${amount:.2f}
                        </div>
                        <div style="font-size: 13px !important; color: #94a3b8; margin-top: 3px;">
                            {reason}
                        </div>
                        <div style="font-size: 12px !important; color: #64748b; margin-top: 2px;">
                            📅 {created_display}
                        </div>
                    </div>
                    <span class="badge {badge_cls}">{status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_action:
            if status == "PENDING":
                if st.button("💳 Pay", key=f"pay_fine_{fine['id']}", use_container_width=True):
                    try:
                        api.pay_fine(fine["id"])
                        st.success("Fine paid!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
