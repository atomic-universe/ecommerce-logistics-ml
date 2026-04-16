import streamlit as st
import os
import pandas as pd
def navigator():
    # ── Page Navigation ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Navigate Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.page_link("app.py",          label="📊 Overview",         use_container_width=True)
        st.caption("Sales trends, revenue, orders by state")

    with col2:
        st.page_link("pages/2_Delivery_Analysis.py", label="📦 Delivery Analysis", use_container_width=True)
        st.caption("Delivery times, on-time rates by state")

    with col3:
        st.page_link("pages/3_Prediction.py",        label="🤖 ML Prediction",     use_container_width=True)
        st.caption("Predict delivery days with XGBoost")

    with col4:
        st.page_link("pages/4_Seller_Analysis.py",   label="🏪 Seller Analysis",   use_container_width=True)
        st.caption("Top sellers, performance rankings")

    with col5:
        st.page_link("pages/5_Customer_Analysis.py", label="👥 Customer Analysis", use_container_width=True)
        st.caption("Reviews, satisfaction, payments")



@st.cache_data
def load_datasets(data_path="data/raw"):

    data = {}

    try:
        data['sellers'] = pd.read_csv(os.path.join(data_path,'sellers.csv'))
        data['items'] = pd.read_csv(os.path.join(data_path,'order_items.csv'))
        data['orders'] = pd.read_csv(os.path.join(data_path,'orders.csv'))
        data['reviews'] = pd.read_csv(os.path.join(data_path,'order_reviews.csv'))
        data['geolocation'] = pd.read_csv(os.path.join(data_path,'geolocation.csv'))
        data['customers'] = pd.read_csv(os.path.join(data_path,'customers.csv'))
        data['payments'] = pd.read_csv(os.path.join(data_path,'order_payments.csv'))
        data['products'] = pd.read_csv(os.path.join(data_path,'products.csv'))
        data['category'] = pd.read_csv(os.path.join(data_path,'product_category_name_translation.csv'))

    except FileNotFoundError as e:
        st.error(f"Missing file: {e}")
        return None

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

    return data


@st.cache_data
def load_processed_data(data_path='data/processed'):
    data = {}
    try:
        data['review_category_wise'] = pd.read_csv(os.path.join(data_path,'product_category_reviews.csv'))

    except FileNotFoundError as e:
        st.error(f"Missing file: {e}")
        return None

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

    return data