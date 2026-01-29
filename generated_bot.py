import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing

st.set_page_config(page_title="House Price AI Bot", page_icon="🏠")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I can help you generate a Linear Regression model for house pricing using the California Housing dataset. Type **'train'** to build the model or **'data'** to see the features."}
    ]

st.title("🏠 House Price ML Bot")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        cmd = prompt.lower()
        
        if "train" in cmd:
            # Load Dataset
            data = fetch_california_housing()
            df = pd.DataFrame(data.data, columns=data.feature_names)
            target = data.target
            
            # Split Data
            X_train, X_test, y_train, y_test = train_test_split(df, target, test_size=0.2, random_state=42)
            
            # Model Training
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Evaluation
            predictions = model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            
            response = f"""
            ### ✅ Model Training Complete!
            I have trained a Linear Regression model using 8 features (MedInc, HouseAge, etc.).
            
            **Model Performance:**
            - **Mean Squared Error (MSE):** {mse:.4f}
            - **R² Score:** {r2:.4f}
            
            The model is now ready for predictions.
            """
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        elif "data" in cmd:
            data = fetch_california_housing()
            response = f"The dataset includes features like: {', '.join(data.feature_names)}. It targets the median house value for California districts."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        else:
            response = "I'm specialized in Linear Regression. Try typing **'train'** to see the model metrics."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})