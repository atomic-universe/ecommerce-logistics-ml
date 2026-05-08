# E-Commerce Delivery Prediction & Analytics Dashboard

## Overview

This project is a complete end-to-end Data Science and Business Intelligence system built using the Brazilian Olist E-Commerce Dataset.

The system predicts e-commerce delivery time using Machine Learning and provides a fully interactive Streamlit Analytics Dashboard for business insights and decision-making.

The project combines:

* Data Engineering
* Exploratory Data Analysis (EDA)
* Feature Engineering
* Machine Learning
* NLP-based Customer Review Analysis
* Interactive Dashboard Development

The prediction system estimates delivery days at the time of order placement using features such as:

* Customer and seller location
* Product dimensions and weight
* Freight value
* Payment information
* Delivery distance
* Seller performance
* Seasonal trends

Along with prediction, the project includes a professional multi-page Streamlit dashboard that allows users to explore delivery performance, seller behavior, customer satisfaction, revenue trends, and live ML predictions.

The project is based on the Olist Brazilian E-Commerce Public Dataset containing over 100K real e-commerce orders from 2016–2018. fileciteturn0file0

---

# Project Objectives

## Delivery Time Prediction

Predict the estimated delivery duration for customer orders.

## Customer Review Analysis

Analyze customer reviews to understand customer satisfaction levels.

## Business Insights

Provide insights that can help:

* Improve logistics efficiency
* Reduce delivery delays
* Increase customer satisfaction
* Monitor customer feedback trends

---

# Features

## Data Engineering

* Merged 9 relational CSV tables into a unified dataset
* Handled multi-seller and multi-item order aggregation
* Geolocation preprocessing using median zip-code coordinates
* Temporal and geographic feature extraction

## Machine Learning Features

* Delivery days prediction using regression models
* Feature engineering and preprocessing pipeline
* Time-based train-test splitting to prevent leakage
* Target encoding for high-cardinality categorical features
* Log transformation for skewed numerical features
* Model evaluation using MAE, RMSE, and R² Score

## NLP & Customer Analytics

* Portuguese-to-English review translation
* Text cleaning and preprocessing
* Sentiment analysis of customer reviews
* Positive/Negative/Neutral review distribution
* Top repeated keywords extraction

## Streamlit Dashboard Features

* Interactive business analytics dashboard
* KPI cards for orders, revenue, sellers, and customers
* Delivery analysis visualizations
* Seller performance monitoring
* Customer review insights
* Real-time ML prediction interface
* Interactive Plotly charts and maps

## Visualization Features

* Delivery trend analysis
* Revenue trend analysis
* Choropleth state maps
* Correlation heatmaps
* Customer satisfaction analysis
* On-time vs late delivery comparison

---

# Tech Stack

## Programming Language

* Python

## Libraries Used

### Data Processing

* pandas
* numpy

### Visualization

* matplotlib
* seaborn
* plotly

### Machine Learning

* scikit-learn
* xgboost

### NLP

* nltk
* spacy
* textblob
* googletrans / deep-translator

### Web Application

* streamlit

---

# Dataset Information

The dataset contains e-commerce order information including:

* Customer details
* Seller details
* Product details
* Order timestamps
* Delivery timestamps
* Freight values
* Customer reviews
* Geolocation information

---

# Project Workflow

## 1. Data Collection

Load and integrate multiple Olist relational datasets.

## 2. Data Cleaning

* Handle missing values
* Remove invalid records
* Filter delivered orders only
* Remove leaky columns
* Fix inconsistent data types

## 3. Feature Engineering

Engineered important features such as:

* Delivery distance (km)
* Product volume
* Same-state flag
* Purchase month/year
* Seller historical performance
* Encoded categorical delivery patterns

## 4. Exploratory Data Analysis

Performed analysis on:

* Delivery trends
* State-wise performance
* Seller behavior
* Seasonal demand
* Delivery delay patterns
* Customer satisfaction trends

## 5. Machine Learning

Trained and compared multiple regression models:

* Linear Regression
* Random Forest Regressor
* XGBoost Regressor

## 6. NLP Processing

* Translate Portuguese reviews into English
* Clean and normalize text
* Lemmatize reviews
* Perform sentiment analysis

## 7. Dashboard Development

Developed a 5-page Streamlit dashboard for:

* Business monitoring
* Analytics visualization
* Delivery insights
* Seller analysis
* Customer analysis
* Live prediction

## 8. Deployment

Deploy the dashboard using Streamlit.

---

# Machine Learning Pipeline

```text
Raw Dataset
     ↓
Data Cleaning
     ↓
Feature Engineering
     ↓
Preprocessing
     ↓
Model Training
     ↓
Evaluation
     ↓
Prediction
     ↓
Deployed
```

---

# Streamlit Dashboard Pages

## 1. Overview Dashboard

Displays:

* Total Orders
* Revenue KPIs
* Seller and Customer Counts
* Monthly Sales Trends
* Orders-by-State Map
* Top Product Categories

## 2. Delivery Analysis Dashboard

Displays:

* Average delivery days by state
* On-time vs late delivery ratio
* Same-state vs cross-state comparison
* Monthly delivery performance trends

## 3. ML Prediction Dashboard

Allows users to:

* Enter customer and seller details
* Input product and payment information
* Predict delivery days instantly using the trained XGBoost model

## 4. Seller Analysis Dashboard

Displays:

* Top sellers by revenue
* Seller delivery rankings
* Worst-performing sellers
* Seller growth trends

## 5. Customer Analysis Dashboard

Displays:

* Review score distribution
* Late delivery vs review score analysis
* Revenue by customer state
* Payment method breakdown

---

# NLP Pipeline

```text
Portuguese Reviews
        ↓
Text Cleaning and Standardization
        ↓
Tokenization
        ↓
Lemmatization
        ↓
Translation to English
        ↓
Sentiment Analysis
        ↓
Visualization
```

---

# Model Evaluation Metrics

Used evaluation metrics:

* Mean Absolute Error (MAE)
* Mean Squared Error (MSE)
* Root Mean Squared Error (RMSE)
* R² Score

---

---

# Installation

## Clone Repository

```bash
git clone <your-github-repository-link>
```

## Move into Project Folder

```bash
cd Ecommerce-Delivery-Prediction
```

## Create Virtual Environment

```bash
python -m venv env
```

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run the Project

## Run Streamlit Application

```bash
streamlit run app.py
```

---

# Sample Use Cases

* Predict estimated delivery time before order confirmation
* Detect customer satisfaction trends
* Analyze delayed delivery patterns
* Improve logistics planning
* Monitor product category reviews

---

# Future Improvements

* Real-time delivery prediction system
* Deep Learning-based delivery forecasting
* Advanced NLP models using Transformers
* Recommendation system integration
* Delay risk classification
* Cloud deployment using AWS/GCP
* FastAPI backend integration
* Real-time shipment tracking
* Mobile-friendly dashboard
* Automated seller performance alerts

---

# Challenges Faced

* Handling large multi-table relational datasets
* Aggregating multi-seller order information
* Preventing feature leakage in temporal data
* Handling duplicate geolocation zip codes
* Translating multilingual customer reviews
* Managing highly skewed feature distributions
* Building scalable Streamlit dashboard architecture
* Designing business-friendly visualizations

---

# Key Learnings

Through this project, I learned:

* End-to-end Machine Learning workflow
* Data preprocessing techniques
* Feature engineering strategies
* NLP preprocessing and sentiment analysis
* Model evaluation and optimization
* Streamlit deployment
* Real-world logistics data analysis

---

# Screenshots


* Dashboard screenshots
   
* Prediction page
* Sentiment analysis charts
* Visualizations

---

# Author

## Vighnesh Sankpal

B.Tech Data Science Student

Interested in:

* Data Science
* Machine Learning
* NLP
* Analytics
* AI Applications

---

# License

This project is developed for educational and learning purposes.
