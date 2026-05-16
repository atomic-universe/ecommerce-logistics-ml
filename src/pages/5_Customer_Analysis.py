import streamlit as st
import pandas as pd
import numpy as np

# Plotly
import plotly.express as px
import plotly.graph_objects as go


from components.style import load_css
from components.utils import    navigator,load_datasets

load_css()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Analysis · Olist",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)





# ── Plotly Dark Theme ─────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#E6EDF3'),
    xaxis=dict(gridcolor='#30363D', linecolor='#30363D', tickfont=dict(color='#7D8590')),
    yaxis=dict(gridcolor='#30363D', linecolor='#30363D', tickfont=dict(color='#7D8590')),
    margin=dict(t=40, b=40, l=40, r=20),
)
 

@st.cache_data
def load_customer_dataset(dataset):
    orders   = dataset['orders']
    customers= dataset['customers']
    payments = dataset['payments']
    reviews  = dataset['reviews']
    items    = dataset['items']
    geolocation = dataset['geolocation']
 
    # Parse dates
    orders['order_purchase_timestamp']        = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_delivered_customer_date']   = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['order_estimated_delivery_date']   = pd.to_datetime(orders['order_estimated_delivery_date'])
 
    # Delivered orders only
    delivered = orders[orders['order_status'] == 'delivered'].copy()
    delivered.dropna(subset=['order_delivered_customer_date',
                              'order_estimated_delivery_date'], inplace=True)
 
    delivered['delivery_days'] = (
        delivered['order_delivered_customer_date'] -
        delivered['order_purchase_timestamp']
    ).dt.days
 
    delivered['is_late'] = (
        delivered['order_delivered_customer_date'] >
        delivered['order_estimated_delivery_date']
    ).astype(int)
 
    delivered['month_label'] = delivered['order_purchase_timestamp'].dt.to_period('M').astype(str)
    delivered['year']        = delivered['order_purchase_timestamp'].dt.year
 
    # Merge customer state
    delivered = delivered.merge(
        customers[['customer_id', 'customer_state', 'customer_unique_id','customer_zip_code_prefix']],
        on='customer_id', how='left'
    )
 
    # Merge payments — aggregate per order
    pay_agg = payments.groupby('order_id').agg(
        total_payment=('payment_value', 'sum'),
        payment_type =('payment_type',  'first'),
        installments =('payment_installments', 'max')
    ).reset_index()
    delivered = delivered.merge(pay_agg, on='order_id', how='left')
 
    # Merge reviews
    delivered = delivered.merge(
        reviews[['order_id', 'review_score']],
        on='order_id', how='left'
    )
 
    # Repeat customers — customers with more than 1 order
    order_counts = delivered.groupby('customer_unique_id')['order_id'].nunique()
    delivered['is_repeat'] = delivered['customer_unique_id'].map(
        lambda x: 1 if order_counts.get(x, 0) > 1 else 0
    )


     # add customer latitude and longitude
    unique_geolocation = geolocation.groupby('geolocation_zip_code_prefix').agg(latitude = ('geolocation_lat','median'),longitude=('geolocation_lng','median'))
    delivered = delivered.merge(unique_geolocation, left_on='customer_zip_code_prefix',right_on='geolocation_zip_code_prefix',how='left',validate='m:1')
 
    return delivered




# ── Load ──────────────────────────────────────────────────────────────────────
try:
    DATASET = load_datasets()
    customer_master = load_customer_dataset(DATASET)
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure all CSV files are in `data/raw/` folder.")
    data_loaded = False
 
 


# ----------------------------------------------------
# Page structure

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Customer <span>Analysis</span></div>
    <div class="page-subtitle">
        Customer satisfaction, review scores, payment behavior,
        repeat customers, and regional revenue breakdown.
    </div>
</div>
""", unsafe_allow_html=True)
 
if not data_loaded:
    st.stop()
 



# __ Navigation _____________________________________________________________________
navigator()


# ___ Filters ________________________________________

with st.container():
    st.subheader("🔍 Filters",text_alignment='right',)

    payment_type, year,state = st.columns(3)

    with payment_type:

        all_pay    = sorted(customer_master['payment_type'].dropna().unique().tolist())
        sel_pay    = st.multiselect("Payment Type", all_pay, default=None)
    
    with year:
        all_years  = sorted(customer_master['year'].dropna().unique().tolist())
        sel_years  = st.multiselect("Year", all_years, default=None)
    
    with state:
        all_states = sorted(customer_master['customer_state'].dropna().unique().tolist())
        sel_states = st.multiselect("Customer State", all_states, default=None)
 


    st.html("""
    <div style='font-size: 0.72rem; color: #7D8590;'>
        <b style='color: #E6EDF3;'>Dataset</b><br>
        Olist Brazilian E-Commerce<br>
        2016 – 2018 · ~100K Customers
    </div>
    """, )


filtered_customers = customer_master


if sel_pay:
    filtered_customers =filtered_customers[filtered_customers['payment_type'].isin(sel_pay)]

if sel_years:
    filtered_customers= filtered_customers[filtered_customers['year'].isin(sel_years)]

if sel_states:
    filtered_customers = filtered_customers[filtered_customers['customer_state'].isin(sel_states)]


if filtered_customers.empty:
    st.warning("No Customer data available for selected filters")
    st.stop()




# ── KPI Row ───────────────────────────────────────────────────────────────────
total_customers  = filtered_customers['customer_unique_id'].nunique()
repeat_customers = filtered_customers[filtered_customers['is_repeat'] == 1]['customer_unique_id'].nunique()
repeat_pct       = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
avg_order_val    = filtered_customers['total_payment'].mean()
avg_review       = filtered_customers['review_score'].mean()
 
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon">👥</div>
        <div class="kpi-label">Total Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
        <div class="kpi-sub">customers</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-icon">🔄</div>
        <div class="kpi-label">Repeat Customers</div>
        <div class="kpi-value">{repeat_pct:.1f}%</div>
        <div class="kpi-sub">{repeat_customers:,} customers returned</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">💳</div>
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">R${avg_order_val:.0f}</div>
        <div class="kpi-sub">per order</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-label">Avg Review Score</div>
        <div class="kpi-value">{avg_review:.2f}</div>
        <div class="kpi-sub">out of 5.0</div>
    </div>
</div>
""", unsafe_allow_html=True)




# ── Row 1: Review Score Distribution + Repeat vs One-time ────────────────────
st.markdown('<div class="section-header">⭐ Customer Satisfaction</div>', unsafe_allow_html=True)
 
col1, col2 = st.columns([3, 2])
 
with col1:
    review_counts = (
        filtered_customers['review_score']
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    review_counts.columns = ['score', 'count']
    total_reviews = review_counts['count'].sum()
    review_counts['pct'] = (review_counts['count'] / total_reviews * 100).round(1)
 
    color_map = {1: '#F85149', 2: '#E05C2A', 3: '#F0A500', 4: '#3FB950', 5: '#2ea043'}
    review_counts['color'] = review_counts['score'].map(color_map)
 
    fig1 = go.Figure(go.Bar(
        x=review_counts['score'],
        y=review_counts['count'],
        marker_color=review_counts['color'],
        text=review_counts['pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        textfont=dict(size=11, color='#7D8590'),
        hovertemplate='<b>%{x} Stars</b><br>Count: %{y:,}<extra></extra>',
        width=0.6
    ))
    fig1.update_layout(
        title="Review Score Distribution",
        xaxis=dict(
            title="Review Score",
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['⭐ 1', '⭐⭐ 2', '⭐⭐⭐ 3', '⭐⭐⭐⭐ 4', '⭐⭐⭐⭐⭐ 5'],
            gridcolor='#30363D', tickfont=dict(color='#7D8590')
        ),
        yaxis=dict(title="Number of Reviews", gridcolor='#30363D',
                   tickfont=dict(color='#7D8590')),
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig1, use_container_width=True)
 
with col2:
    one_time = total_customers - repeat_customers
 
    fig2 = go.Figure(go.Pie(
        labels=['One-time', 'Repeat'],
        values=[one_time, repeat_customers],
        hole=0.62,
        marker_colors=['#58A6FF', '#BC8CFF'],
        textinfo='percent',
        textfont_size=13,
        pull=[0, 0.05]
    ))
    fig2.add_annotation(
        text=f"{repeat_pct:.1f}%<br><span style='font-size:11px'>Repeat</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color='#E6EDF3', family='Syne')
    )
    fig2.update_layout(
        title="Repeat vs One-time Customers",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                    x=0.2, font=dict(color='#7D8590')),
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=60, l=20, r=20),
    )
    st.plotly_chart(fig2, use_container_width=True)
 
 
 
# ── Row 2: Late Delivery vs Review Score ─────────────────────────────────────
st.markdown('<div class="section-header">📦 Delivery Impact on Satisfaction</div>',
            unsafe_allow_html=True)
 
col1, col2 = st.columns(2)
 
with col1:
    # Box plot: review score by late/on-time
    on_time_reviews = filtered_customers[filtered_customers['is_late'] == 0]['review_score'].dropna()
    late_reviews    = filtered_customers[filtered_customers['is_late'] == 1]['review_score'].dropna()
 
    fig3 = go.Figure()
    fig3.add_trace(go.Box(
        y=on_time_reviews,
        name='On Time',
        marker_color='#3FB950',
        boxmean=True,
        hovertemplate='On Time<br>Score: %{y}<extra></extra>'
    ))
    fig3.add_trace(go.Box(
        y=late_reviews,
        name='Late',
        marker_color='#F85149',
        boxmean=True,
        hovertemplate='Late<br>Score: %{y}<extra></extra>'
    ))
    fig3.update_layout(
        title="Review Score: On-Time vs Late Delivery",
        yaxis=dict(title="Review Score", range=[0, 5.5],
                   gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        xaxis=dict(gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        showlegend=True,
        legend=dict(font=dict(color='#7D8590')),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig3, use_container_width=True)
 
with col2:
    # Avg review score by delivery day bucket
    bins   = [0, 5, 10, 15, 20, 30, 120]
    labels = ['0-5d', '6-10d', '11-15d', '16-20d', '21-30d', '30d+']
    filtered_customers['delivery_bucket'] = pd.cut(
        filtered_customers['delivery_days'], bins=bins, labels=labels
    )
 
    bucket_review = (
        filtered_customers.groupby('delivery_bucket', observed=True)['review_score']
        .mean()
        .reset_index()
    )
 
    fig4 = go.Figure(go.Bar(
        x=bucket_review['delivery_bucket'].astype(str),
        y=bucket_review['review_score'],
        marker=dict(
            color=bucket_review['review_score'],
            colorscale=[[0, '#F85149'], [0.5, '#F0A500'], [1, '#3FB950']],
            cmin=1, cmax=5
        ),
        text=bucket_review['review_score'].round(2),
        textposition='outside',
        textfont=dict(size=11, color='#7D8590'),
        hovertemplate='<b>%{x}</b><br>Avg Review: %{y:.2f}<extra></extra>'
    ))
    fig4.update_layout(
        title="Avg Review Score by Delivery Speed",
        xaxis=dict(title="Delivery Time Bucket", gridcolor='#30363D',
                   tickfont=dict(color='#7D8590')),
        yaxis=dict(title="Avg Review Score", range=[3, 5.2],
                   gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig4, use_container_width=True)
 
st.markdown(f"""
<div class="insight-box">
    💡 <strong>Key Insight:</strong>
    On-time deliveries average a review score of
    <strong>{on_time_reviews.mean():.2f}</strong>
    vs late deliveries at
    <strong>{late_reviews.mean():.2f}</strong> —
    a drop of <strong>{on_time_reviews.mean() - late_reviews.mean():.2f} points</strong>.
    Faster delivery is the single most controllable factor in customer satisfaction.
</div>
""", unsafe_allow_html=True)
 


 
# ── Row 3: Revenue by State + Avg Order Value by State ───────────────────────
st.markdown('<div class="section-header">🗺️ Regional Analysis</div>', unsafe_allow_html=True)
 
col1, col2 = st.columns(2)
 
state_stats = filtered_customers.groupby('customer_state').agg(
    total_revenue  =('total_payment', 'sum'),
    avg_order_value=('total_payment', 'mean'),
    total_orders   =('order_id', 'count'),
    avg_review     =('review_score', 'mean')
).reset_index()
 
with col1:
    fig5 = go.Figure(go.Bar(
        x=state_stats.sort_values('total_revenue', ascending=False)['customer_state'],
        y=state_stats.sort_values('total_revenue', ascending=False)['total_revenue'],
        marker=dict(
            color=state_stats.sort_values('total_revenue', ascending=False)['total_revenue'],
            colorscale=[[0, '#1f6feb'], [1, '#58A6FF']],
        ),
        text=state_stats.sort_values('total_revenue', ascending=False)['total_revenue']
             .apply(lambda x: f"R${x/1000:.0f}K"),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{x}</b><br>Revenue: R$%{y:,.0f}<extra></extra>'
    ))
    fig5.update_layout(
        title="Total Revenue by Customer State",
        xaxis=dict(title="State", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(title="Revenue (R$)", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        height=360,
        **{k: v for k, v in PLOTLY_THEME.items() if k not in ['xaxis', 'yaxis']}
    )
    st.plotly_chart(fig5, use_container_width=True)
 
with col2:
    fig6 = go.Figure(go.Bar(
        x=state_stats.sort_values('avg_order_value', ascending=False)['customer_state'],
        y=state_stats.sort_values('avg_order_value', ascending=False)['avg_order_value'],
        marker=dict(
            color=state_stats.sort_values('avg_order_value', ascending=False)['avg_order_value'],
            colorscale=[[0, '#8957e5'], [1, '#BC8CFF']],
        ),
        text=state_stats.sort_values('avg_order_value', ascending=False)['avg_order_value']
             .apply(lambda x: f"R${x:.0f}"),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{x}</b><br>Avg Value: R$%{y:.2f}<extra></extra>'
    ))
    fig6.update_layout(
        title="Avg Order Value by Customer State",
        xaxis=dict(title="State", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(title="Avg Order Value (R$)", gridcolor='#30363D',
                   tickfont=dict(color='#7D8590')),
        height=360,
        **{k: v for k, v in PLOTLY_THEME.items() if k not in ['xaxis', 'yaxis']}
    )
    st.plotly_chart(fig6, use_container_width=True)



    
# ── Row 4: Payment Method + Installments ─────────────────────────────────────
st.markdown('<div class="section-header">💳 Payment Behavior</div>', unsafe_allow_html=True)
 
col1, col2, col3 = st.columns([2, 2, 1])
 
with col1:
    pay_counts = (
        filtered_customers['payment_type']
        .value_counts()
        .reset_index()
    )
    pay_counts.columns = ['payment_type', 'count']
    pay_counts['pct']  = (pay_counts['count'] / pay_counts['count'].sum() * 100).round(1)
 
    color_map_pay = {
        'credit_card': '#58A6FF',
        'boleto'     : '#F0A500',
        'voucher'    : '#3FB950',
        'debit_card' : '#BC8CFF',
        'not_defined': '#7D8590',
    }
    pay_counts['color'] = pay_counts['payment_type'].map(color_map_pay).fillna('#7D8590')
 
    fig7 = go.Figure(go.Pie(
        labels=pay_counts['payment_type'],
        values=pay_counts['count'],
        hole=0.55,
        marker_colors=pay_counts['color'].tolist(),
        textinfo='percent+label',
        textfont_size=11,
    ))
    fig7.update_layout(
        title="Payment Method Distribution",
        showlegend=False,
        height=340,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig7, use_container_width=True)
 
with col2:
    install_dist = (
        filtered_customers['installments']
        .dropna()
        .astype(int)
        .clip(1, 12)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    install_dist.columns = ['installments', 'count']
 
    fig8 = go.Figure(go.Bar(
        x=install_dist['installments'],
        y=install_dist['count'],
        marker_color='#58A6FF',
        opacity=0.85,
        text=install_dist['count'].apply(lambda x: f"{x:,}"),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{x} installments</b><br>Orders: %{y:,}<extra></extra>'
    ))
    fig8.update_layout(
        title="Payment Installments Distribution",
        xaxis=dict(title="Installments", tickmode='linear',
                   gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(title="Orders", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        height=340,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig8, use_container_width=True)
 
with col3:
    # Payment type stats card
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    dominant_pay  = pay_counts.iloc[0]['payment_type'].replace('_', ' ').title()
    dominant_pct  = pay_counts.iloc[0]['pct']
    avg_install   = filtered_customers['installments'].mean()
    max_install   = filtered_customers['installments'].max()
 
    st.markdown(f"""
    <div style='background: var(--surface); border: 1px solid var(--border);
         border-radius: 12px; padding: 1.2rem;'>
        <div style='font-size:0.72rem; color:#7D8590; text-transform:uppercase;
             letter-spacing:0.08em; margin-bottom:1rem;'>Quick Stats</div>
        <div style='margin-bottom:1rem;'>
            <div style='font-size:0.8rem; color:#7D8590;'>Dominant Method</div>
            <div style='font-family:Syne,sans-serif; font-size:1.1rem;
                 font-weight:700; color:#58A6FF;'>{dominant_pay}</div>
            <div style='font-size:0.75rem; color:#7D8590;'>{dominant_pct:.1f}% of orders</div>
        </div>
        <div style='margin-bottom:1rem;'>
            <div style='font-size:0.8rem; color:#7D8590;'>Avg Installments</div>
            <div style='font-family:Syne,sans-serif; font-size:1.1rem;
                 font-weight:700; color:#BC8CFF;'>{avg_install:.1f}x</div>
        </div>
        <div>
            <div style='font-size:0.8rem; color:#7D8590;'>Max Installments</div>
            <div style='font-family:Syne,sans-serif; font-size:1.1rem;
                 font-weight:700; color:#F0A500;'>{int(max_install)}x</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 

 
# ── Row 5: Monthly Order Trend + Avg Review Over Time ────────────────────────
st.markdown('<div class="section-header">📈 Customer Trends Over Time</div>',
            unsafe_allow_html=True)
 
monthly = filtered_customers.groupby('month_label').agg(
    total_orders  =('order_id', 'count'),
    avg_review    =('review_score', 'mean'),
    total_revenue =('total_payment', 'sum'),
    on_time_rate  =('is_late', lambda x: (1 - x.mean()) * 100)
).reset_index().sort_values('month_label')
 
fig9 = go.Figure()
fig9.add_trace(go.Bar(
    x=monthly['month_label'],
    y=monthly['total_orders'],
    name='Orders',
    marker_color='rgba(88, 166, 255, 0.5)',
    hovertemplate='%{x}<br>Orders: %{y:,}<extra></extra>'
))
fig9.add_trace(go.Scatter(
    x=monthly['month_label'],
    y=monthly['avg_review'],
    name='Avg Review',
    mode='lines+markers',
    line=dict(color='#F0A500', width=2.5),
    marker=dict(size=6),
    yaxis='y2',
    hovertemplate='%{x}<br>Avg Review: %{y:.2f}<extra></extra>'
))
fig9.add_trace(go.Scatter(
    x=monthly['month_label'],
    y=monthly['on_time_rate'],
    name='On-Time Rate (%)',
    mode='lines+markers',
    line=dict(color='#3FB950', width=2, dash='dot'),
    marker=dict(size=5),
    yaxis='y3',
    hovertemplate='%{x}<br>On-Time: %{y:.1f}%<extra></extra>'
))
fig9.update_layout(
    title="Monthly Orders, Review Score & On-Time Rate",
    xaxis=dict(tickangle=45, gridcolor='#30363D', tickfont=dict(color='#7D8590')),
    yaxis =dict(title="Orders",          gridcolor='#30363D', tickfont=dict(color='#7D8590')),
    yaxis2=dict(title="Avg Review Score", overlaying='y', side='right',
                range=[3.5, 5.2], tickfont=dict(color='#F0A500')),
    yaxis3=dict(title="On-Time Rate (%)", overlaying='y', side='right',
                position=0.95, range=[0, 120], tickfont=dict(color='#3FB950')),
    legend=dict(font=dict(color='#7D8590'), orientation='h', y=1.12),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#E6EDF3'),
    margin=dict(t=60, b=60, l=40, r=100),
    height=420
)
st.plotly_chart(fig9, use_container_width=True)
 

# ── Row 6: Customer Distriubtion on map ────────────────────
st.html('<div class="section-header">🌎 Customer Distribution on map </div>')



st.map(filtered_customers[['latitude','longitude']].dropna(),color="#F21313")


# ── Row 7: Customer State Summary Table ──────────────────────────────────────
st.markdown('<div class="section-header">📋 State Performance Summary</div>',
            unsafe_allow_html=True)
 
summary = state_stats.copy()
summary['total_revenue']   = summary['total_revenue'].round(0)
summary['avg_order_value'] = summary['avg_order_value'].round(2)
summary['avg_review']      = summary['avg_review'].round(2)
summary['total_orders']    = summary['total_orders'].astype(int)
 
summary = summary.rename(columns={
    'customer_state' : 'State',
    'total_revenue'  : 'Revenue (R$)',
    'avg_order_value': 'Avg Order (R$)',
    'total_orders'   : 'Orders',
    'avg_review'     : 'Avg Review'
}).sort_values('Revenue (R$)', ascending=False)
 
st.dataframe(
    summary.style
        .background_gradient(subset=['Revenue (R$)'],   cmap='Blues')
        .background_gradient(subset=['Avg Review'],     cmap='RdYlGn')
        .background_gradient(subset=['Avg Order (R$)'], cmap='Purples')
        .format({
            'Revenue (R$)'  : 'R${:,.0f}',
            'Avg Order (R$)': 'R${:.2f}',
            'Orders'        : '{:,}',
            'Avg Review'    : '{:.2f}'
        }),
    use_container_width=True,
    height=320
)
 
# st.markdown("""
# <div class="insight-box">
#     💡 <strong>Key Insight:</strong>
#     São Paulo (SP) dominates in total revenue and order volume due to its
#     dense population and proximity to most Customer.
#     However, <strong>average order value varies significantly by state</strong>
#     — northern states tend to have higher average values despite fewer orders,
#     possibly due to higher freight costs being included in payment totals.
# </div>
# """, unsafe_allow_html=True)
 
