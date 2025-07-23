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

def create_earnings_summary(df, target_period='2025Q2', metric='NPATMI'):
    """
    Create earnings summary table for tickers with data in target period
    """
    # Filter for metric data in target period
    target_data = df[(df['DATE'] == target_period) & (df['KEYCODE'] == metric)].copy()
    
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
    
    # Create summary table
    summary_table = target_summary[['TICKER', 'VALUE', 'YoY_Growth', 'QoQ_Growth']].copy()
    summary_table.columns = ['TICKER', f'{target_period} {metric} (VND)', 'YoY Growth (%)', 'QoQ Growth (%)']
    
    # Format values
    summary_table[f'{target_period} {metric} (VND)'] = summary_table[f'{target_period} {metric} (VND)'].apply(
        lambda x: f"{x/1e9:,.1f}B" if pd.notnull(x) else "N/A"
    )
    summary_table['YoY Growth (%)'] = summary_table['YoY Growth (%)'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "N/A"
    )
    summary_table['QoQ Growth (%)'] = summary_table['QoQ Growth (%)'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "N/A"
    )
    
    return summary_table.sort_values('VALUE').reset_index(drop=True)

#%% Streamlit App
st.set_page_config(layout='wide', page_title="Earnings Summary")

st.title("Earnings Summary - Q2 2025")

# Load data
df = load_earnings_data()

# Metric selection buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("NPATMI", type="primary"):
        st.session_state.selected_metric = "NPATMI"
with col2:
    if st.button("EBIT"):
        st.session_state.selected_metric = "EBIT"
with col3:
    if st.button("Net Revenue"):
        st.session_state.selected_metric = "Net_Revenue"

# Initialize session state
if 'selected_metric' not in st.session_state:
    st.session_state.selected_metric = "NPATMI"

selected_metric = st.session_state.selected_metric

# Create earnings summary
earnings_summary = create_earnings_summary(df, '2025Q2', selected_metric)

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
