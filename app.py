import streamlit as st
import pandas as pd
import numpy as np
import pickle
import gzip
import joblib
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Car Price Predictor", layout="wide")

# ==========================================
# 2. LOAD AUTHENTICATION DATABASE
# ==========================================
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ==========================================
# 3. THE LOGIN PORTAL
# ==========================================
authenticator.login()

# ==========================================
# 4. LOGIN MESSAGES & ACCOUNT HELP
# ==========================================
if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

if not st.session_state["authentication_status"]:
    with st.expander("Forgot Password?"):
        try:
            username_forgot, email_forgot, new_password = authenticator.forgot_password()
            if username_forgot:
                st.success('Password successfully reset!')
                st.info(f"Your temporary password is: {new_password}")
                st.warning("Please copy this, log in, and use Account Settings to change it immediately!")
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)

    with st.expander("➕ Don't have an account? Click here to register"):
        try:
            if authenticator.register_user():
                st.success('User registered successfully! You can now log in.')
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)

# ==========================================
# 5. THE MAIN APP (If SUCCESSFULLY logged in)
# ==========================================
elif st.session_state["authentication_status"]:
    
    # --- Sidebar Controls ---
    with st.sidebar:
        st.write(f'Welcome, *{st.session_state["name"]}*!')
        authenticator.logout('Logout', 'sidebar')
        
        # Show a special badge if they are the admin
        if st.session_state.get("username") == "boja":
            st.success(" Admin Mode Active")

        st.divider()
        
        with st.expander("⚙️ Account Settings / Reset Password"):
            try:
                if authenticator.reset_password(st.session_state["username"]):
                    st.success('Password modified successfully')
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(e)

        try:
            st.image("Car_Image.jfif", width=300)
        except:
            pass 
            
        st.title("Car Price Prediction")
        st.write("**Model:** Random Forest Regressor")
        st.write("**Dataset:** Used Car Listings Dataset")
        st.write("**Target:** Log of car price (in USD)")

        st.subheader("Model Performance")
        st.metric(label="R² Score", value="0.74")
        st.metric(label="RMSE", value="$132,580")

    # --- Load Model & Background ---
    @st.cache_resource
    def load_model():
        return joblib.load('car_price_model.joblib')
        
    model = load_model()

    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1668037069509-ba4c569475b1?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8ZGFyayUyMHNwb3J0cyUyMGNhcnxlbnwwfHwwfHx8MA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.title(":green[Predicting Car Prices Using Machine Learning Model]")
    st.markdown("---")

    # ==========================================
    # 🧠 DYNAMIC TABS LOGIC
    # ==========================================
    # If Admin, create 3 tabs. If Normal User, create 2 tabs.
    if st.session_state.get("username") == "boja":
        tab1, tab2, tab3 = st.tabs(["**Single Car Predictor**", "**Upload Whole Dataset**", "**Admin Dashboard**"])
    else:
        tab1, tab2 = st.tabs(["**Single Car Predictor**", "**Upload Whole Dataset**"])

    # --- TAB 1: SINGLE CAR ---
    with tab1:
        st.write("Enter the specifications of a new vehicle below.")
        
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Vehicle Brand", ["BMW", "Audi", "Mercedes", "Ford", "Tesla", "Honda", "Toyota"])
            model_year = st.number_input("Model Year", min_value=2000, max_value=2025, value=2021)
            horsepower = st.number_input("Horsepower", min_value=50.0, max_value=1000.0, value=200.0)
            fuel_type = st.selectbox("Fuel Type", ["Gasoline", "Diesel", "Electric", "Hybrid"])

        with col2:
            milage = st.number_input("Enter Mileage", min_value=0, step=1)
            transmission = st.selectbox("Transmission", ["Automatic", "Manual"])
            has_clean_title = st.selectbox("Clean Title?", ["Yes", "No"])
            accident_reported = st.selectbox("Accident History", ["None reported", "Reported"])

        if st.button("Calculate Estimated Price", type="primary"):
            car_age = 2025 - model_year
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

    # --- TAB 2: BATCH FILE UPLOAD ---
    with tab2:
        st.write("Upload a CSV or Excel file containing multiple cars to generate pricing.")
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                batch_df = pd.read_csv(uploaded_file)
            else:
                batch_df = pd.read_excel(uploaded_file)
                
            batch_df.columns = batch_df.columns.str.lower()
            batch_df = batch_df.loc[:, ~batch_df.columns.duplicated()]
            batch_df = batch_df.rename(columns={
                'mileage': 'milage',
                'year': 'model_year',
                'hp': 'horsepower',
                'title_status': 'has_clean_title' 
            })
            
            if 'model_year' in batch_df.columns and 'car_age' not in batch_df.columns:
                batch_df['car_age'] = 2025 - batch_df['model_year']
            
            st.write("Preview of uploaded inventory:")
            st.dataframe(batch_df.head()) 
        
            if st.button("Generate Prices for Batch", type="primary"):
                try:
                    predicted_log_prices = model.predict(batch_df)
                    real_dollars = np.expm1(predicted_log_prices)
                    batch_df['Recommended_Price'] = real_dollars
                    
                    st.success(f"Successfully generated prices for {len(batch_df)} vehicles!")
                    st.dataframe(batch_df)
                    
                    csv_data = batch_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download The File with Recommended Prices",
                        data=csv_data,
                        file_name="recommended_prices.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"An error occurred. Please check your column names! Error details: {e}")

    # --- TAB 3: ADMIN DASHBOARD (Only executes if Admin) ---
    if st.session_state.get("username") == "boja":
        with tab3:
            st.write("Welcome to the Administrative Control Panel.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 👥 Registered Users")
                for user in config['credentials']['usernames']:
                    st.write(f"- {user}")
                    
            with col2:
                st.write("### 🔒 Security Settings")
                all_users = list(config['credentials']['usernames'].keys())
                user_to_delete = st.selectbox("Select User to Remove", all_users)
                
                if st.button(f"Delete '{user_to_delete}' Account", type="primary"):
                    if user_to_delete == "admin" or user_to_delete == "boja":
                        st.error("⚠️ You cannot delete the master admin account!")
                    else:
                        del config['credentials']['usernames'][user_to_delete]
                        with open('config.yaml', 'w') as file:
                            yaml.dump(config, file, default_flow_style=False)
                        st.success(f"✅ User '{user_to_delete}' has been permanently removed.")
                        st.rerun()