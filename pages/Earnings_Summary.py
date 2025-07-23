#%%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.utils import get_data_path

#%% Load data
@st.cache_data
def load_earnings_data():
    df = pd.read_csv(get_data_path("FA_processed.csv"))
    return df

@st.cache_data
def load_market_cap_data():
    df = pd.read_csv(get_data_path("MktCap_processed.csv"))
    return df

def create_earnings_summary(df, mktcap_df, target_period='2025Q2', metric='NPATMI', min_market_cap=500):
    """
    Create earnings summary table for tickers with data in target period and market cap above threshold
    """
    # Filter tickers by market cap
    large_cap_tickers = mktcap_df[mktcap_df['CUR_MKT_CAP'] >= min_market_cap]['TICKER'].unique()
    
    # Filter for metric data in target period for large cap tickers only
    target_data = df[(df['DATE'] == target_period) & 
                    (df['KEYCODE'] == metric) & 
                    (df['TICKER'].isin(large_cap_tickers))].copy()
    
    if target_data.empty:
        return pd.DataFrame()
    
    # Get list of tickers that have target period data
    tickers_with_data = target_data['TICKER'].unique()
    
    # Filter for all metric data for these tickers
    metric_data = df[(df['TICKER'].isin(tickers_with_data)) & (df['KEYCODE'] == metric)].copy()
    
    # Sort by ticker and date for proper calculation
    metric_data = metric_data.sort_values(['TICKER', 'DATE'])
    
    # Calculate YoY and QoQ growth
    metric_data['YoY_Growth'] = metric_data.groupby('TICKER')['VALUE'].pct_change(periods=4)
    metric_data['QoQ_Growth'] = metric_data.groupby('TICKER')['VALUE'].pct_change(periods=1)
    
    # Filter for target period only
    target_summary = metric_data[metric_data['DATE'] == target_period].copy()
    
    # Add market cap data
    target_summary = target_summary.merge(
        mktcap_df[['TICKER', 'CUR_MKT_CAP']], 
        on='TICKER', 
        how='left'
    )
    
    # Create summary table with numeric values for sorting
    summary_table = target_summary[['TICKER', 'VALUE', 'YoY_Growth', 'QoQ_Growth', 'CUR_MKT_CAP']].copy()
    
    # Convert to appropriate units but keep as numbers for sorting
    summary_table['VALUE_BILLIONS'] = summary_table['VALUE'] / 1e9  # Convert to billions
    summary_table['YoY_Growth_Pct'] = summary_table['YoY_Growth'] * 100  # Convert to percentage
    summary_table['QoQ_Growth_Pct'] = summary_table['QoQ_Growth'] * 100  # Convert to percentage
    
    # Select and rename columns for display
    final_table = summary_table[['TICKER', 'VALUE_BILLIONS', 'YoY_Growth_Pct', 'QoQ_Growth_Pct', 'CUR_MKT_CAP']].copy()
    final_table.columns = ['TICKER', f'{target_period} {metric} (Billions VND)', 'YoY Growth (%)', 'QoQ Growth (%)', 'Market Cap (Billions VND)']
    
    # Sort by market cap descending and reset index
    return final_table.sort_values('Market Cap (Billions VND)', ascending=False).reset_index(drop=True)

#%% Streamlit App
st.set_page_config(layout='wide', page_title="Earnings Summary")

st.title("Earnings Summary - Q2 2025")

# Load data
df = load_earnings_data()
mktcap_df = load_market_cap_data()

# Market cap filter input
st.subheader("Filter Settings")
min_market_cap = st.number_input(
    "Minimum Market Cap (Billion VND)", 
    min_value=0, 
    value=500, 
    step=1,
    help="Filter companies by minimum market cap in billions VND"
)

# Metric selection dropdown
selected_metric = st.selectbox(
    "Select Metric",
    options=["NPATMI", "EBIT", "Net_Revenue"],
    index=0,
    help="Choose the financial metric to display"
)

# Create earnings summary
earnings_summary = create_earnings_summary(df, mktcap_df, '2025Q2', selected_metric, min_market_cap)

if earnings_summary.empty:
    st.warning(f"No {selected_metric} data found for Q2 2025")
else:
    st.subheader(f"Companies with Q2 2025 {selected_metric} Data ({len(earnings_summary)} companies)")
    st.dataframe(earnings_summary, use_container_width=True)
    
    # Download button
    csv = earnings_summary.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"earnings_summary_2025Q2_{selected_metric}.csv",
        mime="text/csv"
    )
