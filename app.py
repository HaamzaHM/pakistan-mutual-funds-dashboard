"""
Interactive Pakistan Mutual Funds Dashboard
A professional Streamlit application for exploring mutual fund data with advanced filtering and analytics.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import math
from config import (
    APP_TITLE, APP_ICON, APP_LAYOUT, SIDEBAR_STATE,
    ITEMS_PER_PAGE, RISK_ORDER, RISK_RATING_MAPPINGS,
    DATA_FOLDER, CLEANED_CSV_NAME, NAV_RANGE_DEFAULT
)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE
)

# Load CSS from external file with fallback
def load_css():
    """Load external CSS file"""
    try:
        with open("styles/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline CSS
        st.markdown("""
            <style>
                .main { padding-top: 1rem; }
                .metric-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 1.5rem; border-radius: 0.8rem;
                    margin: 0.5rem 0; text-align: center;
                }
                .metric-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
                .metric-label { font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; }
                [data-testid="stSelectbox"] label { display: none !important; }
            </style>
        """, unsafe_allow_html=True)

load_css()

@st.cache_data
def load_csv():
    """Load CSV file from data folder - prefer cleaned file"""
    data_folder = Path("data")
    
    # First try to load cleaned CSV
    cleaned_csv = data_folder / "funds_clean.csv"
    if cleaned_csv.exists():
        try:
            df = pd.read_csv(cleaned_csv)
            return df, cleaned_csv.name
        except Exception as e:
            st.warning(f"Could not load cleaned CSV: {e}")
    
    # Fallback to any CSV file
    csv_files = list(data_folder.glob("*.csv"))
    if not csv_files:
        return None, None
    
    # Prefer the largest CSV file
    csv_file = max(csv_files, key=lambda x: x.stat().st_size)
    try:
        df = pd.read_csv(csv_file)
        return df, csv_file.name
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None, None

def convert_rating_to_risk_level(rating):
    """Convert MUFAP rating (AAA(f), AA+(f), etc.) to user-friendly risk level"""
    if pd.isna(rating) or rating == '':
        return 'High'
    
    rating_str = str(rating).strip().lower()
    
    # Very Low Risk: AAA, AA+
    if rating_str in ['aaa(f)', 'aaa', 'aa+(f)', 'aa+']:
        return 'Very Low'
    
    # Low Risk: AA, AA-
    elif rating_str in ['aa(f)', 'aa', 'aa-(f)', 'aa-']:
        return 'Low'
    
    # Medium Risk: A+, A
    elif rating_str in ['a+(f)', 'a+', 'a(f)', 'a']:
        return 'Medium'
    
    # High Risk: A-, BBB and below
    elif rating_str in ['a-(f)', 'a-', 'bbb(f)', 'bbb', 'bbb+(f)', 'bbb+', 'bbb-(f)', 'bbb-', 'bb(f)', 'bb', 'b(f)', 'b']:
        return 'High'
    
    else:
        return 'High'

def detect_columns(df):
    """Auto-detect important columns"""
    col_map = {}
    
    for col in df.columns:
        col_lower = col.lower().strip()
        
        if 'fund' in col_lower and 'name' in col_lower:
            col_map['fund_name'] = col
        elif 'name' in col_lower and 'fund' not in col_lower:
            if 'fund_name' not in col_map:
                col_map['fund_name'] = col
        elif 'company' in col_lower or 'amc' in col_lower:
            col_map['company'] = col
        elif 'nav' in col_lower:
            col_map['nav'] = col
        elif 'category' in col_lower:
            col_map['category'] = col
        elif 'risk' in col_lower or 'rating' in col_lower:
            col_map['risk'] = col
        elif 'offer' in col_lower and 'price' in col_lower:
            col_map['offer_price'] = col
    
    return col_map

def reset_filters():
    """Reset all filters to default"""
    st.session_state.category_filter = []
    st.session_state.company_filter = []
    st.session_state.risk_filter = []
    st.session_state.nav_range = [0, 100]
    st.session_state.search_term = ""
    st.session_state.current_page = 1

def main():
    # Load data
    df, filename = load_csv()
    
    if df is None:
        st.error("❌ No CSV file found!")
        st.info("""
        📍 **How to use:**
        1. Place your CSV file in the `data/` folder
        2. Refresh this page
        """)
        return
    
    # Detect columns
    col_map = detect_columns(df)
    
    if 'fund_name' not in col_map:
        st.error("❌ Could not find fund name column")
        st.info("Expected columns: Fund Name, Name, Fund, etc.")
        return
    
    if 'nav' not in col_map:
        st.error("❌ Could not find NAV column")
        return
    
    # Convert Risk Ratings to User-Friendly Levels
    if col_map.get('risk'):
        df['Risk Level'] = df[col_map['risk']].apply(convert_rating_to_risk_level)
        col_map['risk_level'] = 'Risk Level'  # Use converted column
    
    # Header
    st.title("📊 Pakistan Mutual Funds Dashboard")
    st.markdown(f"**Data Source:** {filename} | **Total Records:** {len(df)}")
    
    # Initialize session state
    if 'category_filter' not in st.session_state:
        st.session_state.category_filter = []
    if 'company_filter' not in st.session_state:
        st.session_state.company_filter = []
    if 'risk_filter' not in st.session_state:
        st.session_state.risk_filter = []
    if 'nav_range' not in st.session_state:
        nav_min = float(df[col_map['nav']].min())
        nav_max = float(df[col_map['nav']].max())
        st.session_state.nav_range = [nav_min, nav_max]
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Sidebar - Filters
    st.sidebar.header("🔍 Filters")
    
    # Get unique values
    fund_col = col_map['fund_name']
    nav_col = col_map['nav']
    cat_col = col_map.get('category')
    comp_col = col_map.get('company')
    risk_col = col_map.get('risk_level', col_map.get('risk'))  # Use converted risk level if available
    
    # Start with full dataframe for dynamic filtering
    dynamic_df = df.copy()
    
    # Apply risk filter first if selected
    if st.session_state.risk_filter:
        if 'Risk Level' in dynamic_df.columns:
            dynamic_df = dynamic_df[dynamic_df['Risk Level'].isin(st.session_state.risk_filter)]
    
    # Get categories based on dynamically filtered data
    categories = sorted(dynamic_df[cat_col].dropna().unique().tolist()) if cat_col else []
    companies = sorted(df[comp_col].dropna().unique().tolist()) if comp_col else []
    
    # Get risk levels based on full data (we'll update this after category selection)
    if risk_col and risk_col in df.columns:
        risk_order = ['Very Low', 'Low', 'Medium', 'High']
        all_risks = df[risk_col].dropna().unique().tolist()
        all_risks_list = [r for r in risk_order if r in all_risks]
    else:
        all_risks_list = []
    
    risks = all_risks_list
    
    # Filter: Search by fund name
    st.sidebar.markdown("### 🔎 Search Fund Name")
    search_term = st.sidebar.text_input(
        "Type to search:",
        value=st.session_state.search_term,
        placeholder="e.g., ABL Cash..."
    )
    st.session_state.search_term = search_term
    
    st.sidebar.markdown("---")
    
    # Filter: Category
    if categories:
        st.sidebar.markdown("### 📂 Category")
        selected_categories = st.sidebar.multiselect(
            "Select Categories",
            categories,
            default=st.session_state.category_filter,
            key="cat_select"
        )
        st.session_state.category_filter = selected_categories
        st.sidebar.markdown("---")
        
        # Update risk levels based on selected categories
        if st.session_state.category_filter:
            category_filtered_df = df[df[cat_col].isin(st.session_state.category_filter)]
            if 'Risk Level' in category_filtered_df.columns:
                risk_order = ['Very Low', 'Low', 'Medium', 'High']
                category_risks = category_filtered_df['Risk Level'].dropna().unique().tolist()
                risks = [r for r in risk_order if r in category_risks]
    
    # Filter: Company
    if companies:
        st.sidebar.markdown("### 🏢 Company")
        selected_companies = st.sidebar.multiselect(
            "Select Companies",
            companies,
            default=st.session_state.company_filter,
            key="comp_select"
        )
        st.session_state.company_filter = selected_companies
        st.sidebar.markdown("---")
    
    # Filter: Risk Rating
    if risks:
        st.sidebar.markdown("### ⚠️ Risk Level")
        selected_risks = st.sidebar.multiselect(
            "Select Risk Levels",
            risks,
            default=st.session_state.risk_filter,
            key="risk_select"
        )
        st.session_state.risk_filter = selected_risks
        st.sidebar.markdown("---")
    
    # Filter: NAV Range
    st.sidebar.markdown("### 💰 NAV Range (Rs.)")
    nav_min = float(df[nav_col].min())
    nav_max = float(df[nav_col].max())
    
    nav_range = st.sidebar.slider(
        "Select NAV Range",
        nav_min,
        nav_max,
        (st.session_state.nav_range[0], st.session_state.nav_range[1]),
        step=0.5
    )
    st.session_state.nav_range = list(nav_range)
    
    st.sidebar.markdown("---")
    
    # Filter buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Apply Filters"):
            st.session_state.current_page = 1
            st.rerun()
    with col2:
        if st.button("🗑️ Clear All"):
            reset_filters()
            st.rerun()
    
    # Apply all filters
    filtered_df = df.copy()
    
    # Search filter
    if search_term:
        filtered_df = filtered_df[
            filtered_df[fund_col].str.contains(search_term, case=False, na=False)
        ]
    
    # Category filter
    if st.session_state.category_filter and cat_col:
        filtered_df = filtered_df[filtered_df[cat_col].isin(st.session_state.category_filter)]
    
    # Company filter
    if st.session_state.company_filter and comp_col:
        filtered_df = filtered_df[filtered_df[comp_col].isin(st.session_state.company_filter)]
    
    # Risk filter
    if st.session_state.risk_filter:
        # Always use the converted Risk Level column for filtering
        if 'Risk Level' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Risk Level'].isin(st.session_state.risk_filter)]
    
    # NAV range filter
    filtered_df = filtered_df[
        (filtered_df[nav_col] >= st.session_state.nav_range[0]) &
        (filtered_df[nav_col] <= st.session_state.nav_range[1])
    ]
    
    # Main content - Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Total Funds</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        avg_nav = filtered_df[nav_col].mean()
        st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Average NAV</div>
                <div class="metric-value">Rs. {:.2f}</div>
            </div>
        """.format(avg_nav), unsafe_allow_html=True)
    
    with col3:
        max_nav = filtered_df[nav_col].max()
        st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Highest NAV</div>
                <div class="metric-value">Rs. {:.2f}</div>
            </div>
        """.format(max_nav), unsafe_allow_html=True)
    
    with col4:
        min_nav = filtered_df[nav_col].min()
        st.markdown("""
            <div class="metric-container">
                <div class="metric-label">Lowest NAV</div>
                <div class="metric-value">Rs. {:.2f}</div>
            </div>
        """.format(min_nav), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📋 Data Table",
        "📊 Analytics",
        "⚠️ By Risk"
    ])
    
    # ==================== TAB 1: PAGINATED DATA TABLE ====================
    with tab1:
        st.subheader("📋 Fund Data ")
        
        # Pagination logic
        ITEMS_PER_PAGE = 50
        total_items = len(filtered_df)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
        
        # Ensure current page is valid
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = max(1, total_pages)
        
        # Calculate start and end index
        start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_data = filtered_df.iloc[start_idx:end_idx]
        
        # Display sorting options
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                filtered_df.columns.tolist(),
                index=0
            )
        with col2:
            sort_order = st.selectbox("Order", ["⬇️ Ascending", "⬆️ Descending"])
        with col3:
            st.write("")  # Spacing
        
        # Sort the data
        sort_reverse = sort_order == "⬆️ Descending"
        display_df = filtered_df.sort_values(by=sort_by, ascending=not sort_reverse)
        
        # Recalculate page data after sorting
        page_data = display_df.iloc[start_idx:end_idx]
        
        # Remove Risk Rating column from display if it exists
        display_columns = [col for col in page_data.columns if col.lower() != 'risk rating']
        page_data_display = page_data[display_columns]
        
        # Display the table
        st.dataframe(
            page_data_display,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        # ==================== PAGINATION CONTROLS ====================
        st.markdown("---")
        
        # Pagination info
        st.markdown(f"""
            <div class="pagination-info">
                <strong>Page {st.session_state.current_page} of {total_pages}</strong> 
                | Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} funds
            </div>
        """, unsafe_allow_html=True)
        
        # Pagination buttons
        col_prev, col_page_num, col_next, col_download = st.columns([1, 3, 1, 2])
        
        with col_prev:
            if st.button("⬅️ Previous", key="btn_prev", use_container_width=True):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
                else:
                    st.warning("Already on first page")
        
        with col_page_num:
            # Page number selector
            page_options = list(range(1, total_pages + 1))
            selected_page = st.selectbox(
                "Page",
                page_options,
                index=st.session_state.current_page - 1,
                key="page_selector"
            )
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
        
        with col_next:
            if st.button("Next ➡️", key="btn_next", use_container_width=True):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
                else:
                    st.warning("Already on last page")
        
        with col_download:
            # Download button for entire filtered dataset
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download All",
                data=csv,
                file_name=f"filtered_funds.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # ==================== TAB 2: ANALYTICS ====================
    with tab2:
        st.subheader("📊 Data Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**NAV Distribution (Top 20)**")
            st.bar_chart(filtered_df[nav_col].value_counts().sort_index().head(20))
        
        with col2:
            if cat_col:
                st.markdown("**Category Distribution**")
                st.bar_chart(filtered_df[cat_col].value_counts())
        
        col3, col4 = st.columns(2)
        
        with col3:
            if risk_col:
                st.markdown("**Risk Rating Distribution**")
                st.bar_chart(filtered_df[risk_col].value_counts())
        
        with col4:
            st.markdown("**Top 10 Highest NAV Funds**")
            top_nav = filtered_df.nlargest(10, nav_col)[[fund_col, nav_col]]
            st.dataframe(top_nav, use_container_width=True, hide_index=True)
    
    # ==================== TAB 3: BY RISK ====================
    with tab3:
        st.subheader("⚠️ Analysis by Risk Rating")
        
        if risk_col:
            # Risk statistics
            risk_stats = filtered_df.groupby(risk_col).agg({
                fund_col: 'count',
                nav_col: ['mean', 'min', 'max']
            }).round(2)
            
            risk_stats.columns = ['Number of Funds', 'Avg NAV', 'Min NAV', 'Max NAV']
            risk_stats = risk_stats.sort_values('Number of Funds', ascending=False)
            
            st.markdown("**Risk Rating Statistics**")
            st.dataframe(risk_stats, use_container_width=True)
            
            # Risk distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Funds by Risk Rating**")
                risk_counts = filtered_df[risk_col].value_counts()
                st.bar_chart(risk_counts)
            
            with col2:
                st.markdown("**Average NAV by Risk Rating**")
                avg_nav_by_risk = filtered_df.groupby(risk_col)[nav_col].mean().sort_values(ascending=False)
                st.bar_chart(avg_nav_by_risk)
        else:
            st.info("Risk column not found in data")

if __name__ == "__main__":
    main()
