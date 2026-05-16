import streamlit as st
import pandas as pd
import os
import plotly.express as px
import numpy as np
import joblib
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from datetime import timedelta

from components.style import load_css
from components.utils import navigator,load_processed_data,create_record

# style

load_css()

# new session
if not 'payment_type' in st.session_state:
    st.session_state.payment_type= None

if not 'predicted_days' in st.session_state:
    st.session_state.predicted_days = 'Enter Information'
@st.cache_data
def load_review_analysis_dataset():
    dataset = load_processed_data()
    return dataset['review_category_wise']


@st.cache_data
def plot_wordcount_plot(category, dataset):
    
    # Filter data
    filtered = dataset[
        dataset['product_category_name_english'] == category
    ]
    
    if filtered.empty:
        st.warning("No data available for this category")
        return
    
    # Flatten word list (Word and sentence tokenization)
    all_words = [word for row in filtered['lemmatized_text'] for word in row.split()]
    
    # Get top words (Portuguese)
    top_words = Counter(all_words).most_common(50)
    
    # Translator
    translator = GoogleTranslator(source='pt', target='en')


    
    # Translate and merge duplicates properly
    translated_counter = Counter()
    
    for word, freq in top_words:
        try:
            translated_word = translator.translate(word).strip().lower()
            translated_counter[translated_word] += freq
        except:
            continue  # skip failed translations
    
    # Generate text for word cloud
    wc = WordCloud(width=800, height=400, background_color='white') \
        .generate_from_frequencies(translated_counter)
    
    fig, ax = plt.subplots(figsize=(8,4))
    ax.imshow(wc,interpolation='bilinear')
    ax.axis('off')
    
    st.pyplot(fig)


# ── Load Data ─────────────────────────────────────────────────────────────────
try:
    review_analysis = load_review_analysis_dataset()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure all CSV files are in `data/processed/` folder.")
    data_loaded = False


if not data_loaded:
    st.stop()


# ----------------------------------------------------
# page structure
#navigation 
navigator()



# ── Page Header ───────────────────────────────────────────────────────────────
st.html("""
<div class="page-header">
    <div class="page-title">Prediction <span>Model</span></div>
    <div class="page-subtitle">
        Delivery performance across Brazil — state-wise trends,
        on-time rates, seasonal patterns, and same-state analysis.
    </div>
</div>
""")


@st.cache_resource
def load_model_data():
    '''
     Return data used for user order data show.\n
     return as (seller,unique_geo,product)
    '''
    path = os.path.join('data','processed')
    
    seller = pd.read_csv(os.path.join(path,'seller_performance.csv'))
    unique_geo = pd.read_csv(os.path.join(path,'unique_geo.csv'))
    product = pd.read_csv(os.path.join(path,'inp_form_orders_show.csv'))

    model_path = os.path.join('models','prediction_model.pkl')
    prediction_model = joblib.load(model_path)

    return (seller,unique_geo,product,prediction_model)
    # return (seller,unique_geo,product)



seller,unique_geo,product,prediction_model = load_model_data()

st.subheader("Select Product")
category_col,product_col,seller_col = st.columns(3)

with category_col:
    filter_categories = np.sort(product['category_formated'].unique().tolist())
    category_inp = st.selectbox(label='Select Category',options=filter_categories)

with product_col:
    filtered_products = np.sort(product[product['category_formated'] == category_inp]['product_id'].unique().tolist())
    product_inp = st.selectbox(label="Select Product", options=filtered_products)


with seller_col:
    filter_seller = np.sort(product[product['product_id']==product_inp]['seller_id'].unique().tolist())

    seller_id_inp = st.selectbox(label='Select Seller',options=filter_seller)

item_quantity_cols,_,_ = st.columns(3)

with item_quantity_cols:
    item_quantity_inp = st.number_input(label='Quantity',min_value=1,max_value=200,value=1)



st.subheader("Costing")
total_price_col,total_freight_col,_ = st.columns(3)

with total_price_col:
    total_price_inp = st.number_input(label='Total Product Cost',min_value=0,value=0)

with total_freight_col:
    total_freight_inp = st.number_input(label='Total Fright Cost',min_value=0,value=0)


st.subheader("Customer Address")
cust_zip_col,_,_ = st.columns(3)

with cust_zip_col:
    cust_zip_code_inp = st.number_input(label='Customer Zip Code Prefix',min_value=1001,max_value=99999,  format="%d")


# Zip code validation.    
is_invalid_zip_code=False

if unique_geo[unique_geo['geolocation_zip_code_prefix'] == cust_zip_code_inp].shape[0]<1:
    st.warning(f'{cust_zip_code_inp} zip code not in database,\ntry other in 1001-99990')
    is_invalid_zip_code = True



st.subheader("Payment")
payment_type_col, payment_installments_col,_ = st.columns(3)
with payment_type_col:

    payment_type_opt = [ 'boleto', 'voucher', 'debit_card','credit_card']
    
    payment_type_inp = st.selectbox(label='Payment Type',options=payment_type_opt)
    st.session_state.payment_type = payment_type_inp

    
with payment_installments_col:
    payment_installments_inp  = st.number_input('Payment Installments',min_value=1,max_value=12)


if st.session_state.payment_type =='credit_card':

    payment_value_cols,_,_ =st.columns(3)
    with payment_value_cols:
        payment_value_inp = st.number_input("Down Payment",placeholder='Value',value=None,
                                             min_value=0,max_value=(total_price_inp+total_freight_inp))

else :
    payment_value_inp =(total_price_inp+total_freight_inp)

    
inputs = {
                            'category_inp':category_inp,
                            'product_inp':product_inp,
                            'seller_id_inp':seller_id_inp,
                            'item_quantity_inp':item_quantity_inp,
                            'total_price_inp':total_price_inp,
                            'total_freight_inp':total_freight_inp,
                            'cust_zip_code_inp':cust_zip_code_inp,
                            'payment_type_inp':payment_type_inp,
                            'payment_installments_inp':payment_installments_inp,
                            'payment_value_inp':payment_value_inp
                            

                        }
dataset ={
    'seller': seller ,
    'unique_geo': unique_geo, 
    'product' :product ,

}

order_date_col,_,_ = st.columns(3)
with order_date_col:
    order_date_inp =  st.date_input("Order Date")

# predict_delivery = st.button("Predict.",disabled=is_invalid_zip_code,on_click=create_record,
#                              args=(inputs,dataset,prediction_model))

predict_delivery = st.button(
    "🚀 Predict Delivery Time",
    disabled=is_invalid_zip_code,
    on_click=create_record,
    args=(inputs, dataset,prediction_model),
    use_container_width=True
)


#   # ── Result Display ────────────────────────────────────────────────────

# logic
if not st.session_state.predicted_days =='Enter Information':

    days = st.session_state.predicted_days
    color ="#fff"
   

    st.html(f"""
    <div class="result-card">
        <div class="result-title">Estimated Delivery Date</div>
        
        <div class="result-days" style="color:{color};">
            {(order_date_inp+timedelta(days=days)).strftime("%d/%m/%Y")}
        </div>
        
        <div class="result-label">{days} days from purchase</div>
        
    </div>
    """)



# --------------------- Sentiment model ---------------------------



st.html("""
<div class="page-header" style = 'margin-top: 2rem;'>
    <div class="page-title">Sentiment <span>Model</span></div>
    <div class="page-subtitle">
        Customer review sentiment across Brazil — product-level wise,  
        product satisfaction and sentiment patterns.
    </div>
</div>
""")

st.subheader("Customer Sentiment analysis by product category.")



with st.form(key='review_sentiment_analysis'):
    category_name =  st.selectbox(label='Select Catagory', options=review_analysis['product_category_name_english'].unique().tolist())

    form_btn = st.form_submit_button("Analyse.")



if form_btn:
    plot_wordcount_plot(category_name,review_analysis)
