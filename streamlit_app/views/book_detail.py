"""
Book Detail Page
Full book details with copies, reviews, borrowing, and related books.
"""

import streamlit as st
from datetime import datetime


def render(api, book_id: int):
    """Render the book detail page."""

    # Back button
    if st.button("← Back to Catalogue", key="back_to_books"):
        st.session_state.selected_book_id = None
        st.session_state.current_page = "books"
        st.rerun()

    if not book_id:
        st.warning("No book selected.")
        return

    # ── Fetch Book ────────────────────────────────────────────────────────
    try:
        book = api.get_book(book_id)
    except Exception as e:
        st.error(f"Failed to load book: {e}")
        return

    if not book:
        st.warning("Book not found.")
        return

    # ── Fetch Reviews & Graph ─────────────────────────────────────────────
    try:
        reviews = api.get_reviews(book_id)
    except Exception:
        reviews = []

    related = []
    try:
        graph_data = api.book_graph(book_id)
        related = [n for n in graph_data.get("nodes", []) if n.get("type") == "Book" and n.get("id") != f"book_{book_id}"]
    except Exception:
        pass

    # ── Layout ────────────────────────────────────────────────────────────
    col_cover, col_details = st.columns([1, 2.5])

    with col_cover:
        cover_url = book.get("cover_image")
        if cover_url:
            st.markdown(f"""
            <div class="glass-card" style="padding: 16px; text-align: center;">
                <div style="width: 100%; border-radius: 12px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                    <img src="{cover_url}" style="width: 100%; max-width: 240px; border-radius: 8px; object-fit: cover;" onerror="this.style.display='none'" />
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="padding: 24px; text-align: center;">
                <div style="width: 100%; aspect-ratio: 2/3; border-radius: 12px; background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2)); display: flex; align-items: center; justify-content: center; font-size: 64px;">
                    📖
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_details:
        # Title & Author
        authors = ", ".join(a["name"] for a in book.get("authors", [])) or "Unknown Author"
        rating = book.get("average_rating", 0) or 0
        total_ratings = book.get("total_ratings", 0) or 0

        # Stars
        stars = ""
        for i in range(5):
            if i < int(round(rating)):
                stars += '<span style="color: #fbbf24; font-size: 18px;">★</span>'
            else:
                stars += '<span style="color: #374151; font-size: 18px;">★</span>'

        # Availability
        copies = book.get("copies", [])
        avail_copies = [c for c in copies if c.get("status") == "AVAILABLE"]
        avail_count = len(avail_copies)

        if avail_count > 0:
            avail_badge = f'<span class="badge badge-available">{avail_count} copies available</span>'
        else:
            avail_badge = '<span class="badge badge-overdue">All copies borrowed</span>'

        # Category
        category = book.get("category", {})
        cat_name = category.get("name", "") if category else ""
        cat_badge = ""
        if cat_name:
            cat_badge = f'<span style="display:inline-block; padding:4px 14px; border-radius:14px; background:rgba(99,102,241,0.1); color:#818cf8; font-size:13px; border:1px solid rgba(99,102,241,0.2); margin-right: 8px;">{cat_name}</span>'

        st.markdown(f"""
        <h1 style="margin-bottom: 4px !important;">{book.get("title", "Untitled")}</h1>
        <p style="font-size: 17px !important; color: #94a3b8; margin-bottom: 16px;">by {authors}</p>
        <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 20px;">
            <div>{stars} <span style="font-size: 17px; font-weight: 600; color: #f1f5f9; margin-left: 6px;">{rating:.1f}</span>
                <span style="font-size: 13px; color: #64748b; margin-left: 4px;">({total_ratings} reviews)</span>
            </div>
            {cat_badge}
            {avail_badge}
        </div>
        """, unsafe_allow_html=True)

        # Info Grid
        info_items = [
            ("ISBN", book.get("isbn", "N/A")),
            ("Publisher", book.get("publisher", {}).get("name", "N/A") if book.get("publisher") else "N/A"),
            ("Year", book.get("publication_year", "N/A")),
            ("Pages", book.get("pages", "N/A")),
        ]
        info_cols = st.columns(4)
        for idx, (label, value) in enumerate(info_items):
            with info_cols[idx]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 12px 16px;">
                    <div style="font-size: 11px !important; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
                    <div style="font-size: 14px !important; font-weight: 600; color: #e2e8f0; margin-top: 4px;">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        # Description
        desc = book.get("description", "")
        if desc:
            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <h4 style="margin-bottom: 6px !important;">Description</h4>
            <p style="color: #94a3b8; font-size: 14px !important; line-height: 1.7 !important;">{desc}</p>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Copies ────────────────────────────────────────────────────────────
    st.markdown("### 📋 Book Copies")

    if copies:
        for copy in copies:
            status = copy.get("status", "UNKNOWN")
            badge_cls = {
                "AVAILABLE": "badge-available",
                "BORROWED": "badge-borrowed",
                "RESERVED": "badge-pending",
            }.get(status, "badge-pending")

            loc = copy.get("location", "")
            loc_html = f'<span style="font-size: 12px !important; color: #64748b;">📍 {loc}</span>' if loc else ""

            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                <div class="glass-card" style="padding: 14px 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 14px !important; font-weight: 500; color: #e2e8f0;">
                                📄 {copy.get("accession_number", "N/A")}
                            </span>
                            <div style="margin-top: 3px;">{loc_html}</div>
                        </div>
                        <span class="badge {badge_cls}">{status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_action:
                if status == "AVAILABLE":
                    if st.button("📖 Borrow", key=f"borrow_{copy['id']}", use_container_width=True):
                        try:
                            api.borrow_book(copy["id"])
                            st.success("Book borrowed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        # Reserve button if no copies available
        if avail_count == 0:
            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
            if st.button("🔖 Reserve This Book", key="reserve_book"):
                try:
                    api.create_reservation(book_id)
                    st.success("Reservation created!")
                except Exception as e:
                    st.error(str(e))

    st.markdown("---")

    # ── Related Books ─────────────────────────────────────────────────────
    if related:
        st.markdown("### 🔗 Related Books")
        rel_cols = st.columns(min(len(related), 5))
        for idx, node in enumerate(related[:5]):
            with rel_cols[idx]:
                bid = node["id"].replace("book_", "")
                label = node.get("label", "Unknown")
                isbn = node.get("properties", {}).get("isbn", "")
                st.markdown(f"""
                <div class="glass-card" style="padding: 14px 16px; min-height: 80px;">
                    <div style="font-size: 13px !important; font-weight: 600; color: #e2e8f0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        {label}
                    </div>
                    <div style="font-size: 11px !important; color: #818cf8; margin-top: 6px;">{isbn}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View →", key=f"related_{bid}", use_container_width=True):
                    st.session_state.selected_book_id = int(bid)
                    st.rerun()

        st.markdown("---")

    # ── Reviews ───────────────────────────────────────────────────────────
    col_reviews, col_write = st.columns(2)

    with col_reviews:
        st.markdown(f"### 💬 Reviews ({len(reviews)})")
        if not reviews:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 32px;">
                <p style="color: #64748b; font-size: 14px !important;">No reviews yet. Be the first to review!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for r in reviews:
                r_stars = ""
                for i in range(5):
                    if i < r.get("rating", 0):
                        r_stars += '<span style="color: #fbbf24; font-size: 14px;">★</span>'
                    else:
                        r_stars += '<span style="color: #374151; font-size: 14px;">★</span>'

                review_text = r.get("review_text", "")
                text_html = f'<p style="font-size: 13px !important; color: #94a3b8; margin-top: 8px; line-height: 1.5;">{review_text}</p>' if review_text else ""

                st.markdown(f"""
                <div class="glass-card" style="padding: 14px 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 14px !important; font-weight: 600; color: #e2e8f0;">
                            {r.get("user_name", "Anonymous")}
                        </span>
                        <div>{r_stars}</div>
                    </div>
                    {text_html}
                </div>
                """, unsafe_allow_html=True)

    with col_write:
        st.markdown("### ✍️ Write a Review")
        with st.form("review_form", clear_on_submit=True):
            review_rating = st.slider("Rating", 1, 5, 5, key="review_rating_slider")

            # Visual stars
            visual_stars = ""
            for i in range(5):
                if i < review_rating:
                    visual_stars += '<span style="color: #fbbf24; font-size: 22px;">★</span>'
                else:
                    visual_stars += '<span style="color: #374151; font-size: 22px;">★</span>'
            st.markdown(f'<div style="margin-bottom: 12px;">{visual_stars}</div>', unsafe_allow_html=True)

            review_text = st.text_area(
                "Your Review",
                placeholder="Share your thoughts about this book...",
                height=120,
                key="review_text_area",
            )

            if st.form_submit_button("📤 Submit Review", use_container_width=True):
                try:
                    api.create_review(book_id, review_rating, review_text)
                    st.success("Review submitted!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
