import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from components.utils import navigator,load_datasets
from components.style import load_css

# style
load_css()


DATASETS = load_datasets()
# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Delivery Analysis · Olist",
    page_icon="📦",
    layout="wide",
     initial_sidebar_state="collapsed"

)


# ── Plotly dark theme ─────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#E6EDF3'),
    xaxis=dict(gridcolor='#30363D', linecolor='#30363D', tickfont=dict(color='#7D8590')),
    yaxis=dict(gridcolor='#30363D', linecolor='#30363D', tickfont=dict(color='#7D8590')),
    margin=dict(t=40, b=40, l=40, r=20),
)


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_delivery_data(DATASET=DATASETS):
    
  
    orders    = DATASETS['orders']
    customers = DATASETS['customers']
    items     = DATASETS['items']
    sellers   = DATASETS['sellers']
    products  = DATASETS['products']
    category  = DATASETS['category']

    # Parse dates
    for col in ['order_purchase_timestamp', 'order_delivered_customer_date',
                'order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col])

    # Keep only delivered
    df = orders[orders['order_status'] == 'delivered'].copy()

    # Calculate delivery days and late flag
    df['delivery_days'] = (
        df['order_delivered_customer_date'] -
        df['order_purchase_timestamp']
    ).dt.days
    df['is_late'] = (
        df['order_delivered_customer_date'] >
        df['order_estimated_delivery_date']
    ).astype(int)
    df['month']        = df['order_purchase_timestamp'].dt.month
    df['year']         = df['order_purchase_timestamp'].dt.year
    df['month_label']  = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    # Remove bad rows
    df = df[df['delivery_days'].between(1, 120)]

    # Merge customer state
    df = df.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')

    # Merge items + products + category for category analysis
    products = products.merge(category, on='product_category_name', how='left')
    items    = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')
    items_agg = items.groupby('order_id').agg(
        category=('product_category_name_english', 'first')
    ).reset_index()
    df = df.merge(items_agg, on='order_id', how='left')

    # Merge seller state
    items_seller = items.merge(sellers[['seller_id', 'seller_state']], on='seller_id', how='left')
    seller_agg = items_seller.groupby('order_id')['seller_state'].first().reset_index()
    df = df.merge(seller_agg, on='order_id', how='left')

    # Same state flag
    df['same_state'] = (df['customer_state'] == df['seller_state']).astype(int)

    return df



# ------------------------------------------------------
# Page Structure


# __ Navigation _____________________________________________________________________
navigator()


# ── Load Data ─────────────────────────────────────────────────────────────────
try:
    df = load_delivery_data(DATASETS)
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure all CSV files are in `data/raw/` folder.")
    data_loaded = False


# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Delivery <span>Analysis</span></div>
    <div class="page-subtitle">
        Delivery performance across Brazil — state-wise trends,
        on-time rates, seasonal patterns, and same-state analysis.
    </div>
</div>
""", unsafe_allow_html=True)

if not data_loaded:
    st.stop()


  

with st.container():

    # st.subheader("<hr style='border-color: #30363D; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.subheader("🔍 Filters",text_alignment='right',)
    _,year_col,state_col = st.columns(3)

    with year_col:
            # Year filter
        years = sorted(df['year'].dropna().unique().tolist())
        selected_years = st.multiselect("Year", years, )

    with state_col:
            # State filter
        all_states = sorted(df['customer_state'].dropna().unique().tolist())
        selected_states = st.multiselect("Customer State", all_states)

    st.markdown("""
        <div style='font-size: 0.72rem; color: #7D8590;'>
            <b style='color: #E6EDF3;'>Dataset</b><br>
            Olist Brazilian E-Commerce<br>
            2016 – 2018 · ~100K Orders
        </div>
        """, unsafe_allow_html=True)



# # Apply filters
# filtered = df[
#     (df['year'].isin(selected_years)) &
#     (df['customer_state'].isin(selected_states))
# ]

filtered = df.copy()

if selected_years:
    filtered = filtered[filtered['year'].isin(selected_years)]

if selected_states:
    filtered = filtered[filtered['customer_state'].isin(selected_states)]

if filtered.empty:
    st.warning("No data available for selected filters")
    st.stop()




# ── KPI Row ───────────────────────────────────────────────────────────────────
total        = len(filtered)
avg_days     = filtered['delivery_days'].mean()
on_time_pct  = (1 - filtered['is_late'].mean()) * 100
late_count   = filtered['is_late'].sum()
fastest_state = filtered.groupby('customer_state')['delivery_days'].mean().idxmin()


st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon">📦</div>
        <div class="kpi-label">Delivered Orders</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-sub">filtered selection</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Avg Delivery Days</div>
        <div class="kpi-value">{avg_days:.1f}</div>
        <div class="kpi-sub">days from purchase</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">✅</div>
        <div class="kpi-label">On-Time Rate</div>
        <div class="kpi-value">{on_time_pct:.1f}%</div>
        <div class="kpi-sub">{total - late_count:,} on-time orders</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-label">Fastest State</div>
        <div class="kpi-value">{fastest_state}</div>
        <div class="kpi-sub">{filtered.groupby('customer_state')['delivery_days'].mean().min():.1f} avg days</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Row 1: Delivery Distribution + On-Time Pie ────────────────────────────────
st.markdown('<div class="section-header">📊 Delivery Overview</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=filtered['delivery_days'],
        nbinsx=50,
        marker_color='#F0A500',
        opacity=0.85,
        name='Orders'
    ))
    fig.add_vline(x=avg_days, line_dash="dash", line_color="#E05C2A",
                  annotation_text=f"Mean: {avg_days:.1f}d",
                  annotation_font_color="#E05C2A")
    fig.add_vline(x=filtered['delivery_days'].median(), line_dash="dot", line_color="#3FB950",
                  annotation_text=f"Median: {filtered['delivery_days'].median():.1f}d",
                  annotation_font_color="#3FB950")
    fig.update_layout(
        title="Delivery Days Distribution",
        xaxis_title="Delivery Days",
        yaxis_title="Number of Orders",
        **PLOTLY_THEME
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    on_time = total - late_count
    fig2 = go.Figure(go.Pie(
        labels=['On Time', 'Late'],
        values=[on_time, late_count],
        hole=0.65,
        marker_colors=['#3FB950', '#F85149'],
        textinfo='percent',
        textfont_size=13,
    ))
    fig2.add_annotation(
        text=f"{on_time_pct:.1f}%<br><span style='font-size:11px'>On Time</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color='#E6EDF3', family='Syne')
    )
    fig2.update_layout(
        title="On-Time vs Late",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.2,
                    font=dict(color='#7D8590')),
        **PLOTLY_THEME
    )
    st.plotly_chart(fig2, use_container_width=True)


# ── Row 2: Delivery by Customer State ─────────────────────────────────────────
st.markdown('<div class="section-header">🗺️ Delivery by Customer State</div>', unsafe_allow_html=True)

state_stats = filtered.groupby('customer_state').agg(
    avg_days=('delivery_days', 'mean'),
    total_orders=('order_id', 'count'),
    late_rate=('is_late', 'mean')
).reset_index().sort_values('avg_days')

state_stats['late_pct'] = (state_stats['late_rate'] * 100).round(1)

col1, col2 = st.columns([3, 2])

with col1:
    fig3 = go.Figure(go.Bar(
        x=state_stats['customer_state'],
        y=state_stats['avg_days'],
        marker=dict(
            color=state_stats['avg_days'],
            colorscale=[[0, '#3FB950'], [0.5, '#F0A500'], [1, '#F85149']],
            showscale=True,
            colorbar=dict(title="Days", tickfont=dict(color='#7D8590'))
        ),
        text=state_stats['avg_days'].round(1),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f} days<extra></extra>'
    ))
    fig3.update_layout(
        title="Average Delivery Days by Customer State",
        xaxis_title="State", yaxis_title="Avg Days",
        **PLOTLY_THEME
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = go.Figure(go.Bar(
        y=state_stats.sort_values('late_pct', ascending=False).head(10)['customer_state'],
        x=state_stats.sort_values('late_pct', ascending=False).head(10)['late_pct'],
        orientation='h',
        marker_color='#F85149',
        opacity=0.85,
        text=state_stats.sort_values('late_pct', ascending=False).head(10)['late_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        textfont=dict(size=10, color='#7D8590'),
        hovertemplate='<b>%{y}</b><br>Late Rate: %{x:.1f}%<extra></extra>'
    ))
    fig4.update_layout(
        title="Top 10 States by Late Delivery Rate",
        xaxis_title="Late Rate (%)", yaxis_title="",
        **PLOTLY_THEME
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown(f"""
<div class="insight-box">
    💡 <strong>Key Insight:</strong>
    Fastest state: <strong>{state_stats.iloc[0]['customer_state']}</strong>
    ({state_stats.iloc[0]['avg_days']:.1f} days) vs slowest:
    <strong>{state_stats.iloc[-1]['customer_state']}</strong>
    ({state_stats.iloc[-1]['avg_days']:.1f} days) —
    a difference of <strong>{state_stats.iloc[-1]['avg_days'] - state_stats.iloc[0]['avg_days']:.1f} days</strong>.
    Geographic distance is the primary driver of this variation.
</div>
""", unsafe_allow_html=True)


# ── Row 3: Same State vs Cross State ─────────────────────────────────────────
st.markdown('<div class="section-header">📍 Same State vs Cross State Delivery</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

same     = filtered[filtered['same_state'] == 1]['delivery_days']
diff     = filtered[filtered['same_state'] == 0]['delivery_days']
same_avg = same.mean()
diff_avg = diff.mean()

with col1:
    fig5 = go.Figure()
    fig5.add_trace(go.Histogram(
        x=same, name='Same State',
        marker_color='#3FB950', opacity=0.75, nbinsx=40
    ))
    fig5.add_trace(go.Histogram(
        x=diff, name='Cross State',
        marker_color='#F85149', opacity=0.75, nbinsx=40
    ))
    fig5.update_layout(
        title="Delivery Days: Same vs Cross State",
        barmode='overlay',
        xaxis_title="Delivery Days", yaxis_title="Orders",
        legend=dict(font=dict(color='#7D8590')),
        **PLOTLY_THEME
    )
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    fig6 = go.Figure(go.Bar(
        x=['Same State', 'Cross State'],
        y=[same_avg, diff_avg],
        marker_color=['#3FB950', '#F85149'],
        text=[f"{same_avg:.1f} days", f"{diff_avg:.1f} days"],
        textposition='outside',
        textfont=dict(size=14, color='#E6EDF3'),
        width=0.5
    ))
    fig6.update_layout(
        title="Average Delivery: Same vs Cross State",
        yaxis_title="Avg Delivery Days",
        yaxis_range=[0, diff_avg * 1.3],
        **PLOTLY_THEME
    )
    st.plotly_chart(fig6, use_container_width=True)

st.markdown(f"""
<div class="insight-box">
    💡 <strong>Key Insight:</strong>
    Same-state orders deliver in <strong>{same_avg:.1f} days</strong> on average
    vs <strong>{diff_avg:.1f} days</strong> for cross-state orders —
    <strong>{diff_avg - same_avg:.1f} days faster</strong> when seller and customer
    are in the same state. This is the strongest single predictor of delivery speed.
</div>
""", unsafe_allow_html=True)


# ── Row 4: Monthly & Yearly Trends ───────────────────────────────────────────
st.markdown('<div class="section-header">📈 Time Trends</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    monthly = filtered.groupby('month_label').agg(
        avg_days=('delivery_days', 'mean'),
        on_time_rate=('is_late', lambda x: (1 - x.mean()) * 100),
        total_orders=('order_id', 'count')
    ).reset_index()

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=monthly['month_label'], y=monthly['avg_days'],
        mode='lines+markers',
        name='Avg Delivery Days',
        line=dict(color='#F0A500', width=2.5),
        marker=dict(size=6, color='#F0A500'),
        hovertemplate='%{x}<br>Avg: %{y:.1f} days<extra></extra>'
    ))
    fig7.add_trace(go.Scatter(
        x=monthly['month_label'], y=monthly['on_time_rate'],
        mode='lines+markers',
        name='On-Time Rate (%)',
        line=dict(color='#3FB950', width=2, dash='dot'),
        marker=dict(size=5, color='#3FB950'),
        yaxis='y2',
        hovertemplate='%{x}<br>On-Time: %{y:.1f}%<extra></extra>'
    ))
    fig7.update_layout(
        title="Monthly Delivery Days & On-Time Rate",
        xaxis_title="Month",
        yaxis=dict(title="Avg Days", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis2=dict(title="On-Time Rate (%)", overlaying='y', side='right',
                    tickfont=dict(color='#3FB950'), range=[0, 110]),
        xaxis=dict(tickangle=45, gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        legend=dict(font=dict(color='#7D8590'), orientation='h', y=1.1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=60, b=60, l=40, r=60),
    )
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    monthly_avg = filtered.groupby('month')['delivery_days'].mean().reset_index()
    monthly_avg.columns = ['month', 'avg_days']
    month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                   7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    monthly_avg['month_name'] = monthly_avg['month'].map(month_names)

    fig8 = go.Figure(go.Bar(
        x=monthly_avg['month_name'],
        y=monthly_avg['avg_days'],
        marker=dict(
            color=monthly_avg['avg_days'],
            colorscale=[[0, '#3FB950'], [0.5, '#F0A500'], [1, '#F85149']],
        ),
        text=monthly_avg['avg_days'].round(1),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f} days<extra></extra>'
    ))
    fig8.update_layout(
        title="Avg Delivery Days by Month",
        xaxis_title="Month", yaxis_title="Avg Days",
        **PLOTLY_THEME
    )
    st.plotly_chart(fig8, use_container_width=True)


# ── Row 5: Delivery by Product Category ──────────────────────────────────────
st.markdown('<div class="section-header">📦 Delivery by Product Category</div>', unsafe_allow_html=True)

top_cats = filtered['category'].value_counts().head(15).index
cat_df   = filtered[filtered['category'].isin(top_cats)]
cat_stats = cat_df.groupby('category').agg(
    avg_days=('delivery_days', 'mean'),
    total=('order_id', 'count')
).reset_index().sort_values('avg_days')

fig9 = go.Figure(go.Bar(
    y=cat_stats['category'],
    x=cat_stats['avg_days'],
    orientation='h',
    marker=dict(
        color=cat_stats['avg_days'],
        colorscale=[[0, '#3FB950'], [0.5, '#F0A500'], [1, '#F85149']],
    ),
    text=cat_stats['avg_days'].round(1),
    textposition='outside',
    textfont=dict(size=10, color='#7D8590'),
    hovertemplate='<b>%{y}</b><br>Avg: %{x:.1f} days<extra></extra>'
))
fig9.update_layout(
    title="Average Delivery Days by Top 15 Product Categories",
    xaxis_title="Avg Delivery Days",
    height=450,
    **PLOTLY_THEME
)
st.plotly_chart(fig9, use_container_width=True)


# ── Row 6: State Summary Table ────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 State Performance Summary</div>', unsafe_allow_html=True)

summary = state_stats.copy()
summary['avg_days']    = summary['avg_days'].round(1)
summary['late_pct']    = summary['late_pct'].round(1)
summary['total_orders']= summary['total_orders'].astype(int)
summary = summary.rename(columns={
    'customer_state': 'State',
    'avg_days'      : 'Avg Delivery Days',
    'total_orders'  : 'Total Orders',
    'late_pct'      : 'Late Rate (%)'
})[['State', 'Avg Delivery Days', 'Total Orders', 'Late Rate (%)']]

st.dataframe(
    summary.style
        .background_gradient(subset=['Avg Delivery Days'], cmap='RdYlGn_r')
        .background_gradient(subset=['Late Rate (%)'], cmap='RdYlGn_r')
        .format({'Avg Delivery Days': '{:.1f}', 'Late Rate (%)': '{:.1f}%', 'Total Orders': '{:,}'}),
    use_container_width=True,
    height=300
)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:3rem; padding-top:1.2rem; border-top:1px solid #30363D;
     display:flex; justify-content:space-between;'>
    <span style='font-size:0.8rem; color:#7D8590;'>
        Built with <span style='color:#F0A500;'>Streamlit</span> ·
        Olist Brazilian E-Commerce Dataset
    </span>
    <span style='font-size:0.75rem; color:#7D8590; font-family:monospace;'>
        XGBoost · Pandas · Plotly
    </span>
</div>
""", unsafe_allow_html=True)