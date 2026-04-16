import streamlit as st
import pandas as pd
import os
from components.style import load_css
import plotly.express as px
import numpy as np
from components.utils import navigator,load_processed_data
from collections import Counter
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# style


load_css()

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
st.warning(": Yet to deployed....",icon='🤖')

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