"""
Fund Comparison Page
Compare multiple funds side-by-side with interactive performance charts
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Fund Comparison",
    page_icon="🔄",
    layout="wide"
)

# Hide sidebar on this page - Apply immediately before anything else
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0 !important;
            visibility: hidden !important;
        }
        [class*="stSidebar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load CSS
def load_css():
    """Load external CSS file"""
    try:
        with open("styles/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
            <style>
                /* Hide Entire Sidebar on Fund Comparison Page */
                [class*="st-emotion-cache"] {
                    /* Target sidebar parent */
                }
                section[data-testid="stSidebar"] {
                    display: none !important;
                    visibility: hidden !important;
                }
                /* Expand main content to full width */
                .main {
                    margin-left: 0 !important;
                    width: 100% !important;
                }
                
                .main { padding-top: 0.5rem; }
                h1 { font-size: 24px !important; margin-bottom: 5px !important; }
                
                /* Page Tab Switcher Styling */
                .page-tab-switcher {
                    display: flex;
                    justify-content: center;
                    gap: 0px;
                    margin-bottom: 20px;
                }
                .page-tab {
                    padding: 12px 30px;
                    font-size: 16px;
                    font-weight: 600;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 0;
                }
                .page-tab:first-child {
                    border-radius: 8px 0 0 8px;
                }
                .page-tab:last-child {
                    border-radius: 0 8px 8px 0;
                }
                .page-tab.active {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .page-tab:hover:not(.active) {
                    background-color: #d0d0d0;
                }
                [data-testid="stSelectbox"] label { display: none !important; }
            </style>
        """, unsafe_allow_html=True)

load_css()

@st.cache_data
def load_csv():
    """Load CSV file from data folder"""
    data_folder = Path("data")
    cleaned_csv = data_folder / "funds_clean.csv"
    if cleaned_csv.exists():
        try:
            df = pd.read_csv(cleaned_csv)
            return df, cleaned_csv.name
        except Exception as e:
            st.warning(f"Could not load cleaned CSV: {e}")
    
    csv_files = list(data_folder.glob("*.csv"))
    if not csv_files:
        return None, None
    
    csv_file = max(csv_files, key=lambda x: x.stat().st_size)
    try:
        df = pd.read_csv(csv_file)
        return df, csv_file.name
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None, None

def detect_columns(df):
    """Auto-detect important columns"""
    col_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'name' in col_lower or 'fund' in col_lower:
            col_map['fund_name'] = col
        elif 'nav' in col_lower:
            col_map['nav'] = col
        elif 'category' in col_lower:
            col_map['category'] = col
        elif 'company' in col_lower or 'manager' in col_lower:
            col_map['company'] = col
        elif 'risk' in col_lower or 'rating' in col_lower:
            col_map['risk'] = col
    return col_map

def convert_rating_to_risk_level(rating):
    """Convert MUFAP rating to user-friendly risk level"""
    if pd.isna(rating) or rating == '':
        return 'High'
    
    rating_str = str(rating).strip().lower()
    
    if rating_str in ['aaa(f)', 'aaa', 'aa+(f)', 'aa+']:
        return 'Very Low'
    elif rating_str in ['aa(f)', 'aa', 'aa-(f)', 'aa-']:
        return 'Low'
    elif rating_str in ['a+(f)', 'a+', 'a(f)', 'a']:
        return 'Medium'
    else:
        return 'High'

@st.cache_data
def load_performance_data():
    """Load performance data from summary CSV"""
    try:
        performance_file = Path("data") / "Performance Summary  MUTUAL FUNDS ASSOCIATION OF PAKISTAN.csv"
        if performance_file.exists():
            df = pd.read_csv(performance_file, skiprows=1)
            return df
    except Exception as e:
        st.warning(f"Could not load performance data: {e}")
    return None

# Main app
# Page Tab Switcher UI with centered layout
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col2:
    col_dash, col_comp = st.columns(2, gap="small")
    with col_dash:
        if st.button("📊 Dashboard", key="dash_nav", use_container_width=True):
            st.switch_page("app.py")
    with col_comp:
        st.button("🔄 Fund Comparison", disabled=True, key="comp_disabled", use_container_width=True)

st.title("🔄 Fund Comparison Analysis")
st.markdown("Compare multiple funds side-by-side with detailed performance analytics")

# Load data
df, filename = load_csv()

if df is None:
    st.error("❌ No CSV file found!")
    st.stop()

# Detect columns
col_map = detect_columns(df)

if 'fund_name' not in col_map:
    st.error("❌ Could not find fund name column")
    st.stop()

if 'nav' not in col_map:
    st.error("❌ Could not find NAV column")
    st.stop()

# Convert Risk Ratings
if col_map.get('risk'):
    df['Risk Level'] = df[col_map['risk']].apply(convert_rating_to_risk_level)
    col_map['risk_level'] = 'Risk Level'

# Initialize session state for comparison
if 'comparison_funds' not in st.session_state:
    st.session_state.comparison_funds = []

# Get column references
fund_col = col_map['fund_name']
nav_col = col_map['nav']
cat_col = col_map.get('category')
risk_col = col_map.get('risk_level', col_map.get('risk'))

# Sidebar - Filters
st.sidebar.header("🔍 Filters")

# Initialize filter states
if 'comp_category_filter' not in st.session_state:
    st.session_state.comp_category_filter = []
if 'comp_risk_filter' not in st.session_state:
    st.session_state.comp_risk_filter = []
if 'comp_nav_range' not in st.session_state:
    nav_min = float(df[nav_col].min())
    nav_max = float(df[nav_col].max())
    st.session_state.comp_nav_range = [nav_min, nav_max]
if 'comp_search_term' not in st.session_state:
    st.session_state.comp_search_term = ""

# Filters
st.sidebar.markdown("### 🔎 Search Fund Name")
search_term = st.sidebar.text_input(
    "Type to search:",
    value=st.session_state.comp_search_term,
    key="comp_search",
    placeholder="e.g., ABL Cash..."
)
st.session_state.comp_search_term = search_term

st.sidebar.markdown("---")

# Category filter
categories = sorted(df[cat_col].dropna().unique().tolist()) if cat_col else []
if categories:
    st.sidebar.markdown("### 📂 Category")
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        categories,
        default=st.session_state.comp_category_filter,
        key="comp_cat_select"
    )
    st.session_state.comp_category_filter = selected_categories
    st.sidebar.markdown("---")

# Risk filter
if risk_col and risk_col in df.columns:
    risk_order = ['Very Low', 'Low', 'Medium', 'High']
    all_risks = df[risk_col].dropna().unique().tolist()
    risks = [r for r in risk_order if r in all_risks]
    
    st.sidebar.markdown("### ⚠️ Risk Level")
    selected_risks = st.sidebar.multiselect(
        "Select Risk Levels",
        risks,
        default=st.session_state.comp_risk_filter,
        key="comp_risk_select"
    )
    st.session_state.comp_risk_filter = selected_risks
    st.sidebar.markdown("---")

# NAV range filter
st.sidebar.markdown("### 💰 NAV Range (Rs.)")
nav_min = float(df[nav_col].min())
nav_max = float(df[nav_col].max())

nav_range = st.sidebar.slider(
    "Select NAV Range",
    nav_min,
    nav_max,
    (st.session_state.comp_nav_range[0], st.session_state.comp_nav_range[1]),
    step=0.5
)
st.session_state.comp_nav_range = list(nav_range)

st.sidebar.markdown("---")

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df[fund_col].str.contains(search_term, case=False, na=False)
    ]

if st.session_state.comp_category_filter and cat_col:
    filtered_df = filtered_df[filtered_df[cat_col].isin(st.session_state.comp_category_filter)]

if st.session_state.comp_risk_filter and 'Risk Level' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Risk Level'].isin(st.session_state.comp_risk_filter)]

filtered_df = filtered_df[
    (filtered_df[nav_col] >= st.session_state.comp_nav_range[0]) &
    (filtered_df[nav_col] <= st.session_state.comp_nav_range[1])
]

# Main content - Split layout
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    st.subheader("📋 Select Funds")
    
    available_funds = sorted(filtered_df[fund_col].unique().tolist())
    
    if available_funds:
        # Multi-select for funds
        selected_funds = st.multiselect(
            "Choose funds to compare:",
            available_funds,
            default=st.session_state.comparison_funds,
            key="fund_selector"
        )
        st.session_state.comparison_funds = selected_funds
        
        # Display best and worst performing funds
        if selected_funds:
            st.markdown("---")
            st.markdown("### 🏆 Best & Worst Performers")
            
            # Load performance data to find best and worst
            performance_df = load_performance_data()
            
            if performance_df is not None:
                # Get 1-year (365 Days) performance if available, otherwise use 3 Years
                perf_period = '365 Days' if '365 Days' in performance_df.columns else '3 Years'
                
                # Find best and worst from selected funds
                best_fund = None
                worst_fund = None
                best_perf = float('-inf')
                worst_perf = float('inf')
                
                for fund_name in selected_funds:
                    fund_perf = performance_df[performance_df['Fund Name'] == fund_name]
                    if not fund_perf.empty and perf_period in fund_perf.columns:
                        try:
                            perf_val = float(fund_perf.iloc[0][perf_period])
                            if perf_val > best_perf:
                                best_perf = perf_val
                                best_fund = fund_name
                            if perf_val < worst_perf:
                                worst_perf = perf_val
                                worst_fund = fund_name
                        except:
                            pass
                
                # Display best and worst performers
                col1, col2 = st.columns(2, gap="medium")
                
                with col1:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px 20px; border-radius: 10px; text-align: center; color: white; 
                                min-height: 200px; display: flex; flex-direction: column; justify-content: center; 
                                align-items: center; width: 100%;">
                        <p style="margin: 5px 0; font-size: 12px; opacity: 0.9; width: 100%;">⭐ Best Fund</p>
                        <p style="margin: 10px 0; font-size: 18px; font-weight: bold; word-wrap: break-word; width: 100%;">""" + (best_fund if best_fund else "N/A") + """</p>
                        <p style="margin: 5px 0; font-size: 14px; color: #4ade80; width: 100%;">↑ """ + (f"{best_perf:.2f}%" if best_perf != float('-inf') else "N/A") + """</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                                padding: 30px 20px; border-radius: 10px; text-align: center; color: white; 
                                min-height: 200px; display: flex; flex-direction: column; justify-content: center; 
                                align-items: center; width: 100%;">
                        <p style="margin: 5px 0; font-size: 12px; opacity: 0.9; width: 100%;">📉 Worst Fund</p>
                        <p style="margin: 10px 0; font-size: 18px; font-weight: bold; word-wrap: break-word; width: 100%;">""" + (worst_fund if worst_fund else "N/A") + """</p>
                        <p style="margin: 5px 0; font-size: 14px; color: #fff9c4; width: 100%;">↑ """ + (f"{worst_perf:.2f}%" if worst_perf != float('inf') else "N/A") + """</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # List selected funds with their NAV
            st.markdown("---")
            st.markdown("### 💾 Selected Fund Details")
            for fund_name in selected_funds:
                fund_info = filtered_df[filtered_df[fund_col] == fund_name].iloc[0]
                nav_val = fund_info[nav_col]
                category = fund_info[cat_col] if cat_col else "N/A"
                risk = fund_info.get('Risk Level', 'N/A') if 'Risk Level' in fund_info else "N/A"
                
                st.markdown(f"""
                <div style="background-color: #1f3a93; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <strong>{fund_name}</strong><br/>
                    NAV: Rs. {nav_val:.2f} | {category} | Risk: {risk}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No funds match the selected filters")

with col_right:
    # Load performance data
    performance_df = load_performance_data()
    
    if performance_df is not None and st.session_state.comparison_funds:
        st.subheader("📈 Performance Comparison")
        
        # Time period selector
        performance_columns = ['YTD', 'MTD', '1 Day', '15 Days', '30 Days', 
                               '90 Days', '180 Days', '270 Days', '365 Days', '2 Years', '3 Years']
        available_columns = [col for col in performance_columns if col in performance_df.columns]
        
        # Create line chart comparing selected funds across time periods
        if st.session_state.comparison_funds:
            # Prepare data for line chart
            line_data = []
            
            for fund_name in st.session_state.comparison_funds:
                fund_perf = performance_df[performance_df['Fund Name'] == fund_name]
                if not fund_perf.empty:
                    perf_values = []
                    for period in available_columns:
                        if period in fund_perf.columns:
                            try:
                                perf_val = float(fund_perf.iloc[0][period])
                                perf_values.append(perf_val)
                            except:
                                perf_values.append(None)
                        else:
                            perf_values.append(None)
                    
                    if perf_values and any(v is not None for v in perf_values):
                        line_data.append({
                            'fund': fund_name,
                            'values': perf_values
                        })
            
            if line_data:
                # Create line chart
                fig = go.Figure()
                
                # Define colors for different funds
                colors = [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#43e97b', '#fa709a', '#30cfd0', '#330867',
                    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'
                ]
                
                for idx, data in enumerate(line_data):
                    color = colors[idx % len(colors)]
                    fig.add_trace(go.Scatter(
                        x=available_columns,
                        y=data['values'],
                        mode='lines+markers',
                        name=data['fund'],
                        line=dict(color=color, width=3),
                        marker=dict(size=8, color=color),
                        hovertemplate='<b>' + data['fund'] + '</b><br>Period: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Fund Performance Comparison - Multi-Period Analysis",
                    xaxis_title="Time Period",
                    yaxis_title="Return (%)",
                    height=600,
                    template='plotly_dark',
                    hovermode='x unified',
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    ),
                    margin=dict(b=80)
                )
                
                fig.update_xaxes(tickangle=-45)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📌 No performance data available for selected funds")
            
            # Detailed comparison table
            st.markdown("---")
            st.markdown("### 📑 Detailed Performance Table")
            
            detailed_table = []
            for fund_name in st.session_state.comparison_funds:
                fund_data = filtered_df[filtered_df[fund_col] == fund_name]
                fund_perf = performance_df[performance_df['Fund Name'] == fund_name]
                
                if not fund_data.empty and not fund_perf.empty:
                    nav_val = fund_data.iloc[0][nav_col]
                    category = fund_data.iloc[0][cat_col] if cat_col else "N/A"
                    
                    perf_dict = {'Fund Name': fund_name, 'NAV': f"Rs. {nav_val:.2f}", 'Category': category}
                    
                    for period in available_columns:
                        if period in fund_perf.columns:
                            try:
                                perf_val = float(fund_perf.iloc[0][period])
                                perf_dict[period] = f"{perf_val:.2f}%"
                            except:
                                perf_dict[period] = "N/A"
                    
                    detailed_table.append(perf_dict)
            
            if detailed_table:
                table_df = pd.DataFrame(detailed_table)
                st.dataframe(table_df, use_container_width=True, hide_index=True)
        else:
            st.info("📌 Select funds to view performance comparison")
    elif performance_df is None:
        st.warning("⚠️ Performance data file not found")
    else:
        st.info("📌 Select funds from the left panel to compare")
