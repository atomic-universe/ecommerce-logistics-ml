import streamlit as st
import pandas as pd
import os
from components.style import load_css
import plotly.express as px
import numpy as np
from components.utils import navigator, load_datasets

data_path = os.path.join('data', 'raw')

DATASETS = load_datasets()

# Style 
load_css()


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_summary_stats(dataset):

    
    customers = dataset['customers']
    sellers   = dataset['sellers']
    payments  = dataset['payments']
    products  = dataset['products']
    orders    = dataset['orders']

    delivered     = orders[orders['order_status'] == 'delivered']
    total_revenue = payments['payment_value'].sum()

    return {
        'total_orders'    : len(orders),
        'delivered_orders': len(delivered),
        'total_customers' : customers['customer_unique_id'].nunique(),
        'total_sellers'   : sellers['seller_id'].nunique(),
        'total_revenue'   : total_revenue,
        'total_products'  : products['product_id'].nunique(),
        'on_time_rate'    : round(len(delivered) / len(orders) * 100, 1),
    }



# ------------------------------------------------------
# Page Structure

#navigation
navigator()



# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🇧🇷 Brazilian E-Commerce</div>
    <div class="hero-title">Olist <span>Analytics</span> Dashboard</div>
    <div class="hero-subtitle">
        End-to-end analytics platform for Olist e-commerce data —
        delivery intelligence, seller performance, customer insights,
        and ML-powered delivery predictions.
    </div>
</div>
""", unsafe_allow_html=True)


# ── KPI Cards ─────────────────────────────────────────────────────────────────
try:
    stats = load_summary_stats(DATASETS)
    st.markdown('<div class="section-header">Platform Overview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{stats['total_orders']:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Unique Customers</div>
            <div class="kpi-value">{stats['total_customers']:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏪</div>
            <div class="kpi-label">Active Sellers</div>
            <div class="kpi-value">{stats['total_sellers']:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">R${stats['total_revenue']/1e6:.1f}M</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

except FileExistsError as e:
    st.info("📂 Place your Olist CSV files in the `data/raw/` folder to load live stats.")
    st.error(f"Error: {e}")



# ── Dataset Info ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Dataset</div>', unsafe_allow_html=True)
st.markdown("""
<div class="dataset-grid">
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">orders.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">customers.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">sellers.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">order_items.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">order_payments.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">order_reviews.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">products.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">geolocation.csv</div></div>
    <div class="dataset-item"><div class="dataset-dot"></div><div class="dataset-name">category_translation.csv</div></div>
</div>
""", unsafe_allow_html=True)

