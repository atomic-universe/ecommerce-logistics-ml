import streamlit as st
import pandas as pd
import numpy as np

# P
import plotly.express as px
import plotly.graph_objects as go


from components.style import load_css
from components.utils import    navigator,load_datasets


load_css()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Seller Analysis · Olist",
    page_icon="🏪",
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





@st.cache_data
def load_seller_dataset(dataset):
    orders = dataset['orders']
    items = dataset['items']
    sellers = dataset['sellers']
    geolocation = dataset['geolocation']
    reviews =  dataset['reviews']


    delivered = orders[orders['order_status']=='delivered']
    delivered_items = items[items['order_id'].isin(delivered['order_id'])]

    #1 total revenue
    seller_total_revenue = np.round(delivered_items.groupby('seller_id')['price'].sum())

    #2 seller review
    seller_avg_reivew = np.round(delivered_items.merge( reviews[['order_id','review_score']],on='order_id',how='inner').groupby('seller_id')['review_score'].mean(),1)


    #3 seller joinned date
    delivered['order_purchase_timestamp'] = pd.to_datetime(delivered['order_purchase_timestamp'])
    seller_joinned_date = delivered_items.merge(delivered,on='order_id',how='inner').groupby('seller_id')['order_purchase_timestamp'].min()


    #4 Late Review
    delivered['order_delivered_carrier_date'] = pd.to_datetime(delivered['order_delivered_carrier_date'])
    seller_late_delivered = delivered[['order_id','order_delivered_carrier_date']].merge(delivered_items[['order_id','shipping_limit_date','seller_id']], on='order_id',how='inner')
    seller_late_delivered['is_late_delivered'] =  np.where(seller_late_delivered['order_delivered_carrier_date']> seller_late_delivered['shipping_limit_date'],1,0)
    seller_late_delivary_rate =  np.round(seller_late_delivered.groupby('seller_id')['is_late_delivered'].mean()*100)

    #5
    seller_total_orders =  delivered_items.groupby('seller_id')['order_id'].nunique()   

    # 6 ave delivary days.
    delivered['order_purchase_timestamp'] = pd.to_datetime(delivered['order_purchase_timestamp'])
    delivered['order_delivered_customer_date'] = pd.to_datetime(delivered['order_delivered_customer_date'])
    delivered['delivary_days'] =  (delivered['order_delivered_customer_date'] - delivered['order_purchase_timestamp']).dt.days

    delivered_item_order = delivered_items.merge(delivered[['order_id','delivary_days']],on='order_id',how='inner',validate='m:1')

    seller_avg_delivery_days = np.round(delivered_item_order.groupby('seller_id')['delivary_days'].mean())

    #Mapping.
    sellers['total_revenue'] = sellers['seller_id'].map(seller_total_revenue)
    sellers['joined_date'] = sellers['seller_id'].map(seller_joinned_date)
    sellers['review'] = sellers['seller_id'].map(seller_avg_reivew)
    sellers['late_delivered_rate'] = sellers['seller_id'].map(seller_late_delivary_rate)
    sellers['total_orders'] = sellers['seller_id'].map(seller_total_orders)
    sellers['avg_delivery_days'] = sellers['seller_id'].map(seller_avg_delivery_days)
    sellers['seller_joined']     = pd.to_datetime(
        sellers['seller_id'].map(seller_joinned_date), yearfirst=True)
    
     # Monthly new sellers series (kept separate for chart)
    sellers['joined_month'] = sellers['seller_joined'].dt.to_period('M').astype(str)

    # Add seller latitude and longitude 
    unique_geolocation = geolocation.groupby('geolocation_zip_code_prefix').agg(latitude= ('geolocation_lat','median'),longitude=('geolocation_lng','median'))
    sellers = sellers.merge(right=unique_geolocation,left_on='seller_zip_code_prefix',right_on='geolocation_zip_code_prefix',how='inner',validate='m:1')

    # Drop Null values records.
    sellers.dropna(subset=['total_revenue','joined_date','late_delivered_rate','total_orders'],inplace=True)

    # some sellers product are pursached but yet to be reviewed for that sellers we assign -10 values in review. 
    sellers['review'] = sellers['review'].fillna(value= -10)


    return sellers





# ── Load ──────────────────────────────────────────────────────────────────────
try:
    DATASETS      = load_datasets()
    seller_master = load_seller_dataset(DATASETS)
    data_loaded   = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure all CSV files are in `data/raw/` folder.")
    data_loaded = False




# Page structure


# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Seller <span>Analysis</span></div>
    <div class="page-subtitle">
        Seller revenue, delivery performance, review scores,
        late delivery rankings, and growth trends across Brazil.
    </div>
</div>
""", unsafe_allow_html=True)

if not data_loaded:
    st.stop()



#navigation header
navigator()


# ___ Filters ________________________________________


with st.container():

    st.subheader("🔍 Filters",text_alignment='right',)
    _,min_order,state_col = st.columns(3)

    with min_order:
            # Year filter
        min_order_val = st.number_input("Min Order", min_value=1,value=1 )

    with state_col:
            # State filter
        all_states = sorted(seller_master['seller_state'].dropna().unique().tolist())
        selected_states = st.multiselect("Seller State", all_states)

    st.markdown("""
        <div style='font-size: 0.72rem; color: #7D8590;'>
            <b style='color: #E6EDF3;'>Dataset</b><br>
            Olist Brazilian E-Commerce<br>
            2016 – 2018 · ~100K Orders
        </div>
        """, unsafe_allow_html=True)


 


filtered_sellers = seller_master

if min_order:
    filtered_sellers = filtered_sellers[filtered_sellers['total_orders']>=min_order_val]

if selected_states:
    filtered_sellers = filtered_sellers[filtered_sellers['seller_state'].isin(selected_states)]


if filtered_sellers.empty:
    st.warning("No Seller data available for selected filters")
    st.stop()



# ── KPI Row ───────────────────────────────────────────────────────────────────

total_sellers    = len(filtered_sellers)
avg_revenue      = filtered_sellers['total_revenue'].mean()
avg_delivery     = filtered_sellers['avg_delivery_days'].mean()
best_state       = filtered_sellers.groupby('seller_state')['review'].mean().idxmax()
best_state_score = filtered_sellers.groupby('seller_state')['review'].mean().max()



st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-icon">🏪</div>
        <div class="kpi-label">Total Sellers</div>
        <div class="kpi-value">{total_sellers:,}</div>
        <div class="kpi-sub"></div>
    </div>
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Avg Revenue / Seller</div>
        <div class="kpi-value">R${avg_revenue:,.0f}</div>
        <div class="kpi-sub">per seller total</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-label">Best Rated State</div>
        <div class="kpi-value">{best_state}</div>
        <div class="kpi-sub">{best_state_score:.2f} avg review score</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Avg Delivery Days</div>
        <div class="kpi-value">{avg_delivery:.1f}</div>
        <div class="kpi-sub">days across all sellers</div>
    </div>
</div>
""", unsafe_allow_html=True)




# ── Row 1: Top 10 by Revenue + Top 10 by Orders ───────────────────────────────

st.html('<div class="section-header">💰 Top Seller Rankings</div>')

col1, col2 = st.columns(2)

with col1:
    top_rev = filtered_sellers.nlargest(10, 'total_revenue')
    fig1 = go.Figure(go.Bar(
        y=top_rev['seller_id'].str[:8] + '...',
        x=top_rev['total_revenue'],
        orientation='h',
        marker=dict(
            color=top_rev['total_revenue'],
            colorscale=[[0, '#E05C2A'], [1, '#F0A500']],
        ),
        text=top_rev['total_revenue'].apply(lambda x: f"R${x:,.0f}"),
        textposition='outside',
        textfont=dict(size=10, color='#7D8590'),
        hovertemplate='<b>%{y}</b><br>Revenue: R$%{x:,.0f}<extra></extra>'
    ))
    fig1.update_layout(
        title="Top 10 Sellers by Revenue",
        xaxis_title="Total Revenue (R$)",
        yaxis=dict(gridcolor='#30363D', linecolor='#30363D',
                   tickfont=dict(color='#7D8590'), autorange='reversed'),
        height=380,
        **{k: v for k, v in PLOTLY_THEME.items() if k != 'yaxis'}
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    top_orders = filtered_sellers.nlargest(10, 'total_orders')
    fig2 = go.Figure(go.Bar(
        y=top_orders['seller_id'].str[:8] + '...',
        x=top_orders['total_orders'],
        orientation='h',
        marker=dict(
            color=top_orders['total_orders'],
            colorscale=[[0, '#1f6feb'], [1, '#58A6FF']],
        ),
        text=top_orders['total_orders'].apply(lambda x: f"{x:,}"),
        textposition='outside',
        textfont=dict(size=10, color='#7D8590'),
        hovertemplate='<b>%{y}</b><br>Orders: %{x:,}<extra></extra>'
    ))
    fig2.update_layout(
        title="Top 10 Sellers by Order Volume",
        xaxis_title="Total Orders",
        yaxis=dict(gridcolor='#30363D', linecolor='#30363D',
                   tickfont=dict(color='#7D8590'), autorange='reversed'),
        height=380,
        **{k: v for k, v in PLOTLY_THEME.items() if k != 'yaxis'}
    )
    st.plotly_chart(fig2, use_container_width=True)



# ── Row 2: Scatter + State Delivery ──────────────────────────────────────────
st.html('<div class="section-header">📊 Seller Performance Deep Dive</div>')


col1, col2 = st.columns([3, 2])

with col1:
    fig3 = px.scatter(
        filtered_sellers[filtered_sellers['review']>=0],
        x='avg_delivery_days',
        y='total_revenue',
        color='review',
        size='total_orders',
        hover_data={'seller_id': True, 'seller_state': True,
                    'late_delivered_rate': ':.1f', 'review': ':.2f'},
        color_continuous_scale=[[0, '#F85149'], [0.5, '#F0A500'], [1, '#3FB950']],
        labels={
            'avg_delivery_days': 'Avg Delivery Days',
            'total_revenue'    : 'Total Revenue (R$)',
            'review' : 'Review Score',
            'total_orders'     : 'Order Count'
        },
        title="Revenue vs Delivery Days (colored by Review Score)"
    )
    fig3.update_traces(marker=dict(opacity=0.75, line=dict(width=0)))
    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        xaxis=dict(gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        coloraxis_colorbar=dict(tickfont=dict(color='#7D8590'), title='Review'),
        margin=dict(t=50, b=40, l=40, r=20),
        height=420
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        💡 <strong>How to read this chart:</strong>
        Each dot = one seller. <strong>Left = faster delivery</strong>,
        <strong>Up = higher revenue</strong>.
        <strong>Green dots</strong> = high review scores,
        <strong>Red dots</strong> = low review scores.
        Bigger dots = more orders.
    </div>
    """, unsafe_allow_html=True)

with col2:
    state_delivery = filtered_sellers.groupby('seller_state').agg(
        avg_days=('avg_delivery_days', 'mean'),
        seller_count=('seller_id', 'count')
    ).reset_index().sort_values('avg_days')

    fig4 = go.Figure(go.Bar(
        y=state_delivery['seller_state'],
        x=state_delivery['avg_days'],
        orientation='h',
        marker=dict(
            color=state_delivery['avg_days'],
            colorscale=[[0, '#3FB950'], [0.5, '#F0A500'], [1, '#F85149']],
            showscale=False
        ),
        text=state_delivery['avg_days'].round(1),
        textposition='outside',
        textfont=dict(size=9, color='#7D8590'),
        hovertemplate='<b>%{y}</b><br>Avg: %{x:.1f} days<extra></extra>'
    ))
    fig4.update_layout(
        title="Avg Delivery Days by Seller State",
        xaxis_title="Avg Days",
        yaxis=dict(gridcolor='#30363D', linecolor='#30363D',
                   tickfont=dict(color='#7D8590'), autorange='reversed'),
        height=420,
        **{k: v for k, v in PLOTLY_THEME.items() if k != 'yaxis'}
    )
    st.plotly_chart(fig4, use_container_width=True)



# ── Row 3: Worst Sellers Table ────────────────────────────────────────────────
st.markdown('<div class="section-header">⚠️ Worst 10 Sellers by Late Delivery Rate</div>',
            unsafe_allow_html=True)

worst = (
    filtered_sellers[(filtered_sellers['total_orders'] >= 5) & (filtered_sellers['review']>=0) ]
    .nlargest(10, 'late_delivered_rate')[
        ['seller_id', 'seller_state', 'total_orders',
         'total_revenue', 'avg_delivery_days', 'late_delivered_rate', 'review']
    ].copy()
)

worst['seller_id']         = worst['seller_id'].str[:12] + '...'
worst['total_orders']      = worst['total_orders'].astype('int')
worst['total_revenue']     = worst['total_revenue'].round(0)
worst['avg_delivery_days'] = worst['avg_delivery_days']
worst['late_delivered_rate']         = worst['late_delivered_rate']
worst['review']  = worst['review']

worst = worst.rename(columns={
    'seller_id'        : 'Seller ID',
    'seller_state'     : 'State',
    'total_orders'     : 'Orders',
    'total_revenue'    : 'Revenue (R$)',
    'avg_delivery_days': 'Avg Days',
    'late_delivered_rate'        : 'Late Rate (%)',
    'review' : 'Review Score'
})

st.dataframe(
    worst.style
        .background_gradient(subset=['Late Rate (%)'], cmap='Reds')
        .background_gradient(subset=['Review Score'],  cmap='RdYlGn')
        .format({
            'Revenue (R$)' : 'R${:,.0f}',
            'Avg Days'     : '{:.1f}',
            'Late Rate (%)': '{:.1f}%',
            'Review Score' : '{:.2f}'
        }),
    use_container_width=True,
    height=320
)

st.html("""
<div class="insight-box">
    💡 <strong>Key Insight:</strong>
    Sellers with high late delivery rates consistently show
    <strong>lower review scores</strong>.
    These sellers are candidates for performance improvement programs
    or platform warnings.
</div>
""")




# ── Row 4: New Sellers Growth + Review Score Distribution ────────────────────
st.markdown('<div class="section-header">📈 Seller Growth & Satisfaction</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    monthly_new = (
        filtered_sellers.dropna(subset=['joined_month'])
        .groupby('joined_month')
        .size()
        .reset_index(name='new_sellers')
        .sort_values('joined_month')
    )
    monthly_new['cumulative'] = monthly_new['new_sellers'].cumsum()

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=monthly_new['joined_month'],
        y=monthly_new['new_sellers'],
        name='New Sellers',
        marker_color='#F0A500',
        opacity=0.8,
        hovertemplate='%{x}<br>New: %{y}<extra></extra>'
    ))
    fig5.add_trace(go.Scatter(
        x=monthly_new['joined_month'],
        y=monthly_new['cumulative'],
        name='Cumulative',
        mode='lines+markers',
        line=dict(color='#58A6FF', width=2.5),
        marker=dict(size=5),
        yaxis='y2',
        hovertemplate='%{x}<br>Total: %{y}<extra></extra>'
    ))
    fig5.update_layout(
        title="New Sellers Joining per Month",
        xaxis=dict(tickangle=45, gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(title="New Sellers", gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis2=dict(title="Cumulative Sellers", overlaying='y', side='right',
                    tickfont=dict(color='#58A6FF')),
        legend=dict(font=dict(color='#7D8590'), orientation='h', y=1.1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=60, b=60, l=40, r=60),
        height=380
    )
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    review_dist = (
        filtered_sellers[filtered_sellers['review']>=0]['review']
        .dropna()
        .apply(lambda x: round(x))
        .clip(1, 5)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    review_dist.columns = ['score', 'count']
    color_map = {1: '#F85149', 2: '#E05C2A', 3: '#F0A500', 4: '#3FB950', 5: '#2ea043'}
    review_dist['color'] = review_dist['score'].map(color_map)

    fig6 = go.Figure(go.Bar(
        x=review_dist['score'],
        y=review_dist['count'],
        marker_color=review_dist['color'],
        text=review_dist['count'],
        textposition='outside',
        textfont=dict(size=11, color='#7D8590'),
        hovertemplate='<b>%{x} Stars</b><br>Sellers: %{y}<extra></extra>'
    ))
    fig6.update_layout(
        title="Seller Avg Review Score Distribution",
        xaxis=dict(title="Review Score (Stars)", tickmode='array',
                   tickvals=[1, 2, 3, 4, 5],
                   ticktext=['⭐ 1', '⭐⭐ 2', '⭐⭐⭐ 3', '⭐⭐⭐⭐ 4', '⭐⭐⭐⭐⭐ 5'],
                   gridcolor='#30363D', tickfont=dict(color='#7D8590')),
        yaxis=dict(title="Number of Sellers", gridcolor='#30363D',
                   tickfont=dict(color='#7D8590')),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#E6EDF3'),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig6, use_container_width=True)



# ── Row 4: Sellers Distriubtion on map ────────────────────
st.html('<div class="section-header">🌎 Seller Distribution on map </div>')

st.map(filtered_sellers[['latitude','longitude']],color='#0000FF')