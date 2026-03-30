import sys
import os
# Add project root to Python path
# This allows us to import modules from config/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import text
from config.db import get_engine

# Page config
st.set_page_config(page_title="Chinook Dashboard", layout="wide")

# Title
st.title("🎵 Chinook Music Store Analytics Dashboard")
st.caption(" :- Interactive dashboard to analyze sales, customers, and revenue trends")

# -------------------------------
# DATA LOADING FUNCTION
# -------------------------------
@st.cache_data
def load_data():
    """
    Load data from database and cache it
    """

    engine = get_engine()

    with engine.connect() as conn:

        # Invoices table
        invoices = pd.read_sql(text("""
            SELECT 
                invoice_id,
                customer_id,
                invoice_date,
                billing_country,
                total
            FROM invoice
        """), conn)

        # Invoice line + artist
        invoice_line_detail = pd.read_sql(text("""
            SELECT 
                il.invoice_id,
                ar.name AS artist,
                il.unit_price * il.quantity AS line_total
            FROM invoice_line il
            JOIN track t ON il.track_id = t.track_id
            JOIN album al ON t.album_id = al.album_id
            JOIN artist ar ON al.artist_id = ar.artist_id
        """), conn)

    # Convert date column
    invoices['invoice_date'] = pd.to_datetime(invoices['invoice_date'])

    return invoices, invoice_line_detail


# -------------------------------
# LOAD DATA
# -------------------------------
invoices, invoice_line_detail = load_data()


# -------------------------------------------------------------------------------------------------
# SIDEBAR FILTERS STARTS
# -------------------------------------------------------------------------------------------------
st.sidebar.header("Filters")

# Add spacing
st.sidebar.write("")

# Country filter
country_options = sorted(invoices['billing_country'].unique())

selected_countries = st.sidebar.multiselect(
    "Filter by Country :",
    options=country_options,
    default=country_options  # all selected by default
)

# -------------------------------
# DATE RANGE FILTER
# -------------------------------

# Add spacing
st.sidebar.write("")

# Add spacing
st.sidebar.write("")

# Convert to date
min_date = invoices['invoice_date'].min().date()
max_date = invoices['invoice_date'].max().date()

date_range = st.sidebar.date_input(
    "Filter by Date Range :",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle invalid selection
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.warning("Please select a valid date range")
    st.stop()

# ------------------------------- APPLY FILTERS -------------------------------

# Country filter logic
country_mask = invoices['billing_country'].isin(selected_countries)

# Apply both filters
filtered_invoices = invoices[
    country_mask &
    (invoices['invoice_date'].dt.date >= date_range[0]) &
    (invoices['invoice_date'].dt.date <= date_range[1])
]

# ---------------------------------------------------------------------------------------------------------
# SIDEBAR FILTERS ENDS
# ---------------------------------------------------------------------------------------------------------



# -------------------------------------------------------------------------------------
# KPI METRICS STARTS (calculating KPIs from filtered_invoices only, not from full data)
# --------------------------------------------------------------------------------------
st.subheader("Key Metrics")

# Create 3 columns
col1, col2, col3 = st.columns(3)

# KPI 1: Total Revenue
with col1:
    total_revenue = filtered_invoices['total'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

# KPI 2: Total Invoices
with col2:
    total_invoices = len(filtered_invoices)
    st.metric("Total Invoices", f"{total_invoices:,}")

# KPI 3: Total Customers
with col3:
    total_customers = filtered_invoices['customer_id'].nunique()
    st.metric("Total Customers", f"{total_customers:,}")

st.divider()
# ------------------------------------------------------------------------------------------------------------
# KPI METRICS ENDS
# ------------------------------------------------------------------------------------------------------------


# ------------------------------------------------
# TOP 10 ARTISTS BY REVENUE STARTS
# ------------------------------------------------

# Get filtered invoice IDs
filtered_invoice_ids = filtered_invoices['invoice_id'].tolist()

# Filter line-level data using those IDs
filtered_lines = invoice_line_detail[
    invoice_line_detail['invoice_id'].isin(filtered_invoice_ids)
]

# Aggregate revenue by artist
artist_revenue = (
    filtered_lines
    .groupby('artist')['line_total']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# Rename column for clarity
artist_revenue.rename(columns={'line_total': 'revenue'}, inplace=True)


# ------------------- TOP 10 ARTISTS BY REVENUE (CHART) --------------------
st.subheader("Top 10 Artists by Revenue")

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    data=artist_revenue,
    x='revenue',
    y='artist',
    ax=ax
)

# ax.set_title("Top 10 Artists by Revenue")
ax.set_xlabel("Revenue ($)")
ax.set_ylabel("Artist")

# Add data labels
for bar in ax.patches:
    ax.text(
        bar.get_width(),
        bar.get_y() + bar.get_height() / 2,
        f"${bar.get_width():,.2f}",
        va='center'
    )

st.pyplot(fig)

st.divider()
# ---------------------------------------------------------------------------------------------------------------
# TOP 10 ARTISTS BY REVENUE ENDS
# ---------------------------------------------------------------------------------------------------------------


# ----------------------------------------
# MONTHLY REVENUE TREND STARTS
# -----------------------------------------

# Create month column (YYYY-MM format)
filtered_invoices = filtered_invoices.copy()
filtered_invoices['month'] = filtered_invoices['invoice_date'].dt.strftime('%Y-%m')

# Aggregate revenue by month
monthly_revenue = (
    filtered_invoices
    .groupby('month')['total']
    .sum()
    .reset_index()
)

# ------------------ MONTHLY REVENUE TREND (CHART) --------------------

st.subheader("Monthly Revenue Trend")

fig, ax = plt.subplots(figsize=(12, 5))

sns.lineplot(
    data=monthly_revenue,
    x='month',
    y='total',
    marker='o',
    ax=ax
)

# ax.set_title("Monthly Revenue Trend")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")

# Reduce number of x labels
for i, label in enumerate(ax.get_xticklabels()):
    if i % 3 != 0:  # show every 3rd month
        label.set_visible(False)

ax.tick_params(axis='x', rotation=45)

st.pyplot(fig)
st.divider()
# -------------------------------------------------------------------------------------------------
# MONTHLY REVENUE TREND Ends
# -------------------------------------------------------------------------------------------------



# -------------------------------
# REVENUE BY COUNTRY STARTS
# -------------------------------

country_revenue = (
    filtered_invoices
    .groupby('billing_country')['total']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Rename for clarity
country_revenue.rename(
    columns={'billing_country': 'country', 'total': 'revenue'},
    inplace=True
)

# ------------------------- REVENUE BY COUNTRY (CHART) -----------------------

st.subheader("Revenue by Country")

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    data=country_revenue,
    x='revenue',
    y='country',
    ax=ax
)

# ax.set_title("Revenue by Country")
ax.set_xlabel("Revenue ($)")
ax.set_ylabel("Country")

# Add data labels
for bar in ax.patches:
    ax.text(
        bar.get_width(),
        bar.get_y() + bar.get_height() / 2,
        f"${bar.get_width():,.2f}",
        va='center'
    )

st.pyplot(fig)
st.divider()
# -----------------------------------------------------------------------------------------------------------
# REVENUE BY COUNTRY ENDS
# -----------------------------------------------------------------------------------------------------------


# -------------------------------
# BUSINESS INSIGHTS
# -------------------------------

st.markdown("## 📌 Business Insights")

# Check if data exists after filtering
if filtered_invoices.empty:
    st.warning("No data available for the selected filters.")
else:
    insights = []

    # Top Artist
    if not artist_revenue.empty:
        top_artist = artist_revenue.iloc[0]
        insights.append(
            f"🎤 **Top Artist:** {top_artist['artist']} generated the highest revenue of **${top_artist['revenue']:,.2f}**."
        )

    # Top Country
    if not country_revenue.empty:
        top_country = country_revenue.iloc[0]
        insights.append(
            f"🌍 **Top Country:** {top_country['country']} contributed the most with **${top_country['revenue']:,.2f}**"
        )

    # Peak Month
    if not monthly_revenue.empty:
        peak_month = monthly_revenue.loc[monthly_revenue['total'].idxmax()]
        insights.append(
            f"📅 **Peak Month:** {peak_month['month']} recorded the highest revenue of **${peak_month['total']:,.2f}**"
        )

    # Display insights
    for insight in insights:
        st.markdown(f"- {insight}")