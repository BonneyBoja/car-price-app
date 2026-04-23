import streamlit as st
import pandas as pd
import numpy as np
import pickle
import gzip

# 1. Page Configuration
st.set_page_config(page_title="Car Price Predictor", layout="wide")


page_bg_img = f"""
<style>
/* Target the absolute main application wrapper */
.stApp {{
    background-image: url("https://images.unsplash.com/photo-1668037069509-ba4c569475b1?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8ZGFyayUyMHNwb3J0cyUyMGNhcnxlbnwwfHwwfHx8MA%3D%3D");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

/* Make the top header area transparent */
[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 2. Load the trained model
import joblib

@st.cache_resource
def load_model():
    return joblib.load("car_price_pipeline.joblib")

model = load_model()

st.title(":green[Predicting Car Prices Using Machine Learning Model]")
st.markdown("---")
#Sidebar Layout
with st.sidebar:
    st.image("Car_Image.jfif",width=300)
    st.title("Car Price Prediction")
    st.sidebar.write("**Model:** Random Forest Regressor")
    st.sidebar.write("**Dataset:** Used Car Listings Dataset")
    st.sidebar.write("**Target:** Log of car price (in USD)")


    st.sidebar.subheader("Model Performance")
      # Replace these values with your actual evaluation metrics
    st.sidebar.metric(label="R² Score", value="0.14")
    st.sidebar.metric(label="RMSE", value="$132,580")
    st.markdown("""
    This app predicts the **price of used cars** based on various features using a Random Forest Regressor model.
    """)
    st.markdown("## About")
    st.markdown("""
    This application utilizes a pre-trained Random Forest model to estimate car prices.
    Users can input various features of the car, and the model will provide a price prediction.
    """)


# CREATE TABS FOR THE U
tab1, tab2 = st.tabs(["**Single Car Predictor**",               "**Upload Whole Dataset**"])


# TAB 1: SINGLE CAR (Your existing code)

with tab1:
    st.write("Enter the specifications of a new vehicle below.")
    
    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Vehicle Brand", ["BMW", "Audi", "Mercedes", "Ford", "Tesla", "Honda", "Toyota"])
        model_year = st.number_input("Model Year", min_value=2000, max_value=2025, value=2021)
        horsepower = st.number_input("Horsepower", min_value=50.0, max_value=1000.0, value=200.0)
        fuel_type = st.selectbox("Fuel Type", ["Gasoline", "Diesel", "Electric", "Hybrid"])

    with col2:
        milage = st.number_input("Mileage (mi)", min_value=0, max_value=500000, value=45000)
        transmission = st.selectbox("Transmission", ["Automatic", "Manual"])
        has_clean_title = st.selectbox("Clean Title?", ["Yes", "No"])
        accident_reported = st.selectbox("Accident History", ["None reported", "Reported"])

    if st.button("Calculate Estimated Price", type="primary"):
        car_age = 2025 - model_year
        
        #  THE TRANSLATOR FIX: Convert dropdown text into the math the model expects
        acc_status = 0 if accident_reported == "None reported" else 1
        title_status = 1 if has_clean_title == "Yes" else 0
        
        user_input = {
            'brand': [brand], 
            'model_year': [model_year], 
            'car_age': [car_age],               
            'horsepower': [horsepower], 
            'fuel_type': [fuel_type], 
            'transmission': [transmission],
            'milage': [milage], 
            'has_clean_title': [title_status],  
            'accident_reported': [acc_status]
        }
        
        input_df = pd.DataFrame(user_input)
        predicted_log_price = model.predict(input_df)
        final_price = np.expm1(predicted_log_price)[0]
        st.success(f"### Recommended Listing Price: **${final_price:,.2f}**")



# TAB 2: BATCH FILE UPLOAD (The New Feature!)
# This tab allows users to upload an entire CSV or Excel file with multiple cars, and the app will generate recommended prices for each one in a new column. It also includes error handling and a download button for the results.
with tab2:
    st.write("Upload a CSV or Excel file containing multiple cars to generate pricing.")
    
    #accepts both csv AND xlsx!
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        
        
        # Check the file extension and use the correct pandas reader
        if uploaded_file.name.endswith('.csv'):
            batch_df = pd.read_csv(uploaded_file)
        else:
            batch_df = pd.read_excel(uploaded_file)
            
        
        # Force all column names to lowercase automatically!
        batch_df.columns = batch_df.columns.str.lower()
        
        # Drop any duplicate columns 
        batch_df = batch_df.loc[:, ~batch_df.columns.duplicated()]
        
        # Catch alternate names and rename them 
        batch_df = batch_df.rename(columns={
            'mileage': 'milage',
            'year': 'model_year',
            'hp': 'horsepower',
            'title_status': 'has_clean_title' 
        })
        
        # Calculate car age for the entire spreadsheet!
        if 'model_year' in batch_df.columns and 'car_age' not in batch_df.columns:
            batch_df['car_age'] = 2025 - batch_df['model_year']
        
        st.write("Preview of uploaded inventory:")
        st.dataframe(batch_df.head()) 
    
        if st.button("Generate Prices for Batch", type="primary"):
            try:
                # 1. Run the whole spreadsheet through the pipeline
                predicted_log_prices = model.predict(batch_df)
                
                # 2. Reverse the math to real dollars
                real_dollars = np.expm1(predicted_log_prices)
                
                # 3. Add a brand new column to the spreadsheet with the prices
                batch_df['Recommended_Price'] = real_dollars
                
                st.success(f"Successfully generated prices for {len(batch_df)} vehicles!")
                
                # 4. Show the final spreadsheet with the prices attached
                st.dataframe(batch_df)
                
            
                # Convert the dataframe back to a CSV in the background
                csv_data = batch_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="⬇️ Download The File with Recommended Prices",
                    data=csv_data,
                    file_name="recommended_prices.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"An error occurred. Please check your column names! Error details: {e}")
