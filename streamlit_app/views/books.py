"""
Books Catalogue Page
Book listing with search, category filter, and card display.
"""

import streamlit as st
import math


def render(api):
    """Render the book catalogue page."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style="margin-bottom: 2px !important;">📚 Book Catalogue</h1>
    <p style="color: #64748b; font-size: 15px !important; margin-top: 0;">
        Browse and discover our collection
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # ── Search & Filters ──────────────────────────────────────────────────
    col_search, col_cat, col_avail = st.columns([3, 1.5, 1])

    with col_search:
        search = st.text_input(
            "Search",
            placeholder="Search books by title, ISBN, or description...",
            label_visibility="collapsed",
            key="books_search",
        )

    with col_cat:
        # Load categories
        try:
            categories = api.list_categories()
            cat_options = {"All Categories": None}
            for c in categories:
                cat_options[c["name"]] = c["id"]
            selected_cat_name = st.selectbox(
                "Category",
                options=list(cat_options.keys()),
                label_visibility="collapsed",
                key="books_category",
            )
            selected_cat_id = cat_options[selected_cat_name]
        except Exception:
            selected_cat_id = None
            st.selectbox("Category", ["All Categories"], label_visibility="collapsed", disabled=True)

    with col_avail:
        available_only = st.checkbox("Available only", key="books_avail")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    # ── Fetch Books ───────────────────────────────────────────────────────
    try:
        books = api.list_books(
            q=search if search else None,
            category_id=selected_cat_id,
            available_only=available_only,
        )
    except Exception as e:
        st.error(f"Failed to load books: {e}")
        return

    if not books:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 24px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
            <h3 style="color: #94a3b8;">No books found</h3>
            <p style="color: #64748b; font-size: 13px !important; margin-top: 4px;">
                Try adjusting your search or filters
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Results Count ─────────────────────────────────────────────────────
    st.markdown(f'<p style="color: #64748b; font-size: 13px !important; margin-bottom: 12px;">{len(books)} book{"s" if len(books) != 1 else ""} found</p>', unsafe_allow_html=True)

    # ── Book Grid ─────────────────────────────────────────────────────────
    cols_per_row = 4
    rows = math.ceil(len(books) / cols_per_row)

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            book_idx = row * cols_per_row + col_idx
            if book_idx >= len(books):
                break

            book = books[book_idx]
            with cols[col_idx]:
                # Author names
                authors = ", ".join(a["name"] for a in book.get("authors", [])) or "Unknown Author"
                category = book.get("category", {})
                cat_name = category.get("name", "") if category else ""
                rating = book.get("average_rating", 0) or 0
                avail = book.get("available_copies", 0)
                avail_color = "#34d399" if avail > 0 else "#f87171"
                avail_text = f"{avail} available" if avail > 0 else "Unavailable"

                # Star display
                stars_html = ""
                for i in range(5):
                    if i < int(round(rating)):
                        stars_html += '<span style="color: #fbbf24; font-size: 13px;">★</span>'
                    else:
                        stars_html += '<span style="color: #374151; font-size: 13px;">★</span>'

                # Category badge
                cat_badge = ""
                if cat_name:
                    cat_badge = f'<span style="display:inline-block; margin-top:8px; padding:3px 10px; border-radius:12px; background:rgba(99,102,241,0.1); color:#818cf8; font-size:11px !important; border:1px solid rgba(99,102,241,0.2);">{cat_name}</span>'

                # Cover image
                cover_url = book.get("cover_image")
                if cover_url:
                    cover_html = f'<div style="width:100%; height:180px; border-radius:12px; margin-bottom:14px; overflow:hidden;"><img src="{cover_url}" style="width:100%; height:100%; object-fit:cover;" onerror="this.style.display=\'none\'" /></div>'
                else:
                    cover_html = '<div style="width:100%; height:180px; border-radius:12px; background:linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.15)); display:flex; align-items:center; justify-content:center; margin-bottom:14px; font-size:40px;">📖</div>'

                st.markdown(f"""
                <div class="book-card">
                    {cover_html}
                    <h4 style="font-size: 14px !important; font-weight: 600; color: #e2e8f0; margin: 0; line-height: 1.4 !important; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        {book.get("title", "Untitled")}
                    </h4>
                    <p style="font-size: 12px !important; color: #64748b; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {authors}
                    </p>
                    {cat_badge}
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06);">
                        <div>{stars_html} <span style="font-size:13px; color:#94a3b8; margin-left:4px;">{rating:.1f}</span></div>
                        <span style="font-size:12px !important; font-weight:600; color:{avail_color};">{avail_text}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("View Details", key=f"view_book_{book['id']}", use_container_width=True):
                    st.session_state.selected_book_id = book["id"]
                    st.rerun()
