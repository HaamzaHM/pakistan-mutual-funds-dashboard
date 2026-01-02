"""
Interactive Pakistan Mutual Funds Dashboard
A professional Streamlit application for exploring mutual fund data with advanced filtering and analytics.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import math
import plotly.graph_objects as go
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
        # Fallback inline CSS - Compact version
        st.markdown("""
            <style>
                .main { padding-top: 0.5rem; }
                h1 { font-size: 24px !important; margin-bottom: 5px !important; }
                .metric-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white; padding: 12px 15px !important; border-radius: 0.6rem !important;
                    margin: 2px 0 !important; text-align: center; font-size: 12px !important;
                }
                .metric-value { font-size: 16px !important; font-weight: bold !important; margin: 2px 0 !important; }
                .metric-label { font-size: 10px !important; opacity: 0.9 !important; text-transform: uppercase; margin-bottom: 2px !important; }
                .stTabs [data-baseweb="tab-list"] button { font-size: 16px !important; padding: 12px 20px !important; font-weight: 600 !important; }
                .stTabs [data-baseweb="tab-list"] { gap: 15px !important; }
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
    st.session_state.selected_tab = 0  # Initialize selected tab to first tab

def load_performance_data():
    """Load performance data from the summary CSV"""
    try:
        performance_file = Path("data") / "Performance Summary  MUTUAL FUNDS ASSOCIATION OF PAKISTAN.csv"
        if performance_file.exists():
            # Skip the first row which is a title row
            df = pd.read_csv(performance_file, skiprows=1)
            return df
    except Exception as e:
        st.warning(f"Could not load performance data: {e}")
    return None

def show_fund_performance_analysis(fund_name, performance_df):
    """Display interactive fund performance analysis with line chart"""
    st.markdown("---")
    st.subheader(f"📈 {fund_name} - Performance Analysis")
    
    # Filter performance data for selected fund
    fund_data = performance_df[performance_df['Fund Name'] == fund_name]
    
    if fund_data.empty:
        st.warning(f"Performance data not available for {fund_name}")
        return
    
    # Performance columns available
    performance_columns = ['YTD', 'MTD', '1 Day', '15 Days', '30 Days', 
                          '90 Days', '180 Days', '270 Days', '365 Days', '2 Years', '3 Years']
    
    # Filter only available columns
    available_columns = [col for col in performance_columns if col in performance_df.columns]
    
    # Initialize session state for selected period (default to 3 Years)
    if 'selected_fund' not in st.session_state or st.session_state.selected_fund != fund_name:
        st.session_state.selected_fund = fund_name
        st.session_state.selected_period = '3 Years'
    
    # Time period buttons with highlighting
    st.markdown("**Select Time Period:**")
    button_cols = st.columns(len(available_columns))
    
    for idx, col_name in enumerate(available_columns):
        with button_cols[idx]:
            # Check if this button is the selected period
            is_selected = col_name == st.session_state.selected_period
            
            # Create button with different styling if selected
            if is_selected:
                if st.button(f"✓ {col_name}", key=f"perf_{fund_name}_{col_name}", use_container_width=True):
                    st.session_state.selected_period = col_name
            else:
                if st.button(col_name, key=f"perf_{fund_name}_{col_name}", use_container_width=True):
                    st.session_state.selected_period = col_name
    
    selected_period = st.session_state.selected_period
    
    # Get fund details
    fund_row = fund_data.iloc[0]
    
    # Display metrics (Removed Rating, Benchmark, and Category)
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            nav_value = float(fund_row['NAV']) if 'NAV' in fund_row and pd.notna(fund_row['NAV']) else None
            st.metric("NAV", f"Rs. {nav_value:.2f}" if nav_value else "N/A")
        except:
            st.metric("NAV", "N/A")
    
    with col2:
        validity = str(fund_row['Validity Date']) if 'Validity Date' in fund_row else "N/A"
        st.metric("Validity Date", validity)
    
    # Display the selected period value
    if selected_period in performance_df.columns:
        perf_value = fund_row[selected_period]
        if pd.notna(perf_value):
            try:
                perf_float = float(perf_value)
                st.markdown(f"**{selected_period} Return:** `{perf_float:.2f}%`")
            except:
                st.markdown(f"**{selected_period} Return:** `{perf_value}`")
        else:
            st.markdown(f"**{selected_period} Return:** `N/A`")
    
    # Create LINE CHART showing all periods with highlighted selected period
    st.markdown(f"**Performance Data - {selected_period}:**")
    
    # Prepare data for all periods
    periods = available_columns
    values = []
    for period in periods:
        try:
            val = float(fund_row[period]) if period in fund_row.index and pd.notna(fund_row[period]) else 0
            values.append(val)
        except:
            values.append(0)
    
    fig = go.Figure()
    
    # Add line trace for all data
    fig.add_trace(go.Scatter(
        x=periods,
        y=values,
        mode='lines+markers',
        name=fund_name,
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
    ))
    
    # Highlight the selected period with a special marker
    selected_idx = periods.index(selected_period) if selected_period in periods else 0
    selected_value = values[selected_idx] if selected_idx < len(values) else 0
    
    fig.add_trace(go.Scatter(
        x=[selected_period],
        y=[selected_value],
        mode='markers',
        marker=dict(size=15, color='#FF6B6B', symbol='star'),
        name='Selected Period',
        hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{fund_name} - Performance Across Time Periods",
        xaxis_title="Time Period",
        yaxis_title="Return (%)",
        hovermode='x unified',
        height=450,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

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
    
    # Header - Compact version
    st.markdown("""
        <style>
        h1 { font-size: 24px !important; margin-bottom: 5px !important; }
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white; padding: 12px 15px !important; border-radius: 0.6rem !important;
            margin: 2px 0 !important; text-align: center; font-size: 12px !important;
        }
        .metric-label { font-size: 10px !important; opacity: 0.9 !important; text-transform: uppercase; margin-bottom: 2px !important; }
        .metric-value { font-size: 16px !important; font-weight: bold !important; margin: 2px 0 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Pakistan Mutual Funds Dashboard")
    st.markdown(f"<small>**Data Source:** {filename} | **Total Records:** {len(df)}</small>", unsafe_allow_html=True)
    
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
    
    # Main content - Metrics (Compact)
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
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
    
    st.markdown("""<div style="margin-top: -10px; margin-bottom: 10px;"></div>""", unsafe_allow_html=True)
    
    # Add custom CSS for tabs and spacing
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px !important;
            padding: 12px 20px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px !important;
        }
        .main { padding-top: 0.5rem !important; }
        [data-testid="stSelectbox"] label { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # Tabs for different views - Reordered: Performance Analysis first
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Performance Analysis",
        "📋 Data Table",
        "📊 Analytics",
        "⚠️ By Risk"
    ])
    
    # Update session state when tabs change
    tabs = [tab1, tab2, tab3, tab4]
    
    # Track which tab is currently active
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = 0
    
    # ==================== TAB 1: PERFORMANCE ANALYSIS ====================
    with tab1:
        st.subheader("📈 Interactive Fund Performance Analysis")
        
        # Load performance data
        performance_df = load_performance_data()
        
        if performance_df is not None:
            st.info("📌 Select a fund to view detailed performance analysis with interactive charts")
            
            # Apply the same filters as the Data Table to Performance Analysis
            # Filter performance data based on the filtered_df (which has all filters applied)
            available_funds = sorted(filtered_df[fund_col].unique().tolist())
            
            # Only show funds that exist in both filtered_df and performance_df
            available_funds = [f for f in available_funds if f in performance_df['Fund Name'].values]
            
            if available_funds:
                selected_fund = st.selectbox(
                    "🔍 Select a Fund for Analysis:",
                    available_funds,
                    key="fund_selector"
                )
                
                if selected_fund:
                    # Show performance analysis
                    show_fund_performance_analysis(selected_fund, performance_df)
            else:
                st.warning("⚠️ No funds match the selected filters. Please adjust your filter selections.")
        else:
            st.warning("⚠️ Performance data file not found. Please ensure 'Performance Summary  MUTUAL FUNDS ASSOCIATION OF PAKISTAN.csv' exists in the data folder.")
    
    # ==================== TAB 2: PAGINATED DATA TABLE ====================
    with tab2:
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
    
    # ==================== TAB 3: ANALYTICS ====================
    with tab3:
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
    
    # ==================== TAB 4: BY RISK ====================
    with tab4:
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
