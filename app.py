import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import requests
from streamlit_lottie import st_lottie
from sklearn.preprocessing import MinMaxScaler

# Load Lottie animation
def load_lottie(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Lottie animation URLs
loading_animation = load_lottie("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")

# Streamlit app title
st.title("📊Data Analysis App")

# Show animation
if loading_animation:
    st_lottie(loading_animation, height=200, key="loading")

# Upload file
uploaded_file = st.file_uploader("📂 Upload an Excel or CSV file", type=["csv", "xlsx"])

if uploaded_file:
    with st.spinner("⏳ Processing file..."):
        time.sleep(2)  # Simulate processing time

    # Determine file type and read data
    file_extension = uploaded_file.name.split(".")[-1]
    df = pd.read_csv(uploaded_file) if file_extension == "csv" else pd.read_excel(uploaded_file)

    st.success("✅ File successfully loaded!")

    # Progress Bar Animation
    progress_bar = st.progress(0)
    for percent in range(100):
        time.sleep(0.01)  # Simulate progress
        progress_bar.progress(percent + 1)
    st.success("🎉 Data Ready!")

    # Display dataset
    st.subheader("📌 View Dataset")
    if not df.empty:
        num_rows = st.number_input("🔢 Enter number of rows to display", min_value=1, max_value=len(df), value=5)
        selected_columns = st.multiselect("📊 Select columns to display", df.columns.tolist(), default=df.columns.tolist())

        if selected_columns:
            st.write(df[selected_columns].head(num_rows))
            st.write(df[selected_columns].tail(num_rows))
        else:
            st.warning("⚠️ Please select at least one column to display.")

        # Dataset Summary
        st.subheader("📊 Dataset Summary")
        st.write(df.describe())

        # Data Filtering
        st.subheader("🔍 Filter Data")
        filter_column = st.selectbox("Select a column to filter", df.columns)
        unique_values = df[filter_column].dropna().unique()
        selected_value = st.selectbox(f"Select a value from '{filter_column}'", unique_values)
        filtered_df = df[df[filter_column] == selected_value]
        st.write("Filtered Data:", filtered_df)

        # Handle Missing Values
        st.subheader("🧹 Handle Missing Values")
        missing_action = st.radio("📌 Choose an action:", ["Do Nothing", "Drop Missing Values", "Fill Missing Values"])

        if missing_action == "Drop Missing Values":
            df = df.dropna()
            st.success("✅ Missing values dropped!")

        elif missing_action == "Fill Missing Values":
            fill_value = st.text_input("🔢 Enter a value to fill missing data:")
            if fill_value:
                df = df.fillna(fill_value)
                st.success("✅ Missing values filled!")

        # Remove Duplicate Rows
        st.subheader("🚮 Remove Duplicate Rows")
        if st.button("🗑 Remove Duplicates"):
            df = df.drop_duplicates()
            st.success("✅ Duplicates removed!")

        # Convert Column Data Type
        st.subheader("🔄 Convert Column Data Type")
        column_to_convert = st.selectbox("📌 Select column", df.columns)
        new_dtype = st.radio("📌 Choose new data type:", ["int", "float", "string"])

        if st.button("Convert Data Type"):
            try:
                if new_dtype == "int":
                    df[column_to_convert] = pd.to_numeric(df[column_to_convert], errors='coerce').astype("Int64")
                elif new_dtype == "float":
                    df[column_to_convert] = pd.to_numeric(df[column_to_convert], errors='coerce')
                elif new_dtype == "string":
                    df[column_to_convert] = df[column_to_convert].astype(str)
                st.success(f"✅ Converted '{column_to_convert}' to {new_dtype}")
            except Exception as e:
                st.error(f"❌ Error converting data type: {e}")

        # Normalize Data
        st.subheader("📏 Normalize Data (Scale between 0-1)")
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_columns:
            column_to_scale = st.selectbox("📌 Select column to normalize", numeric_columns)

            if st.button("🔄 Normalize Column"):
                scaler = MinMaxScaler()
                df[column_to_scale] = scaler.fit_transform(df[[column_to_scale]])
                st.success(f"✅ '{column_to_scale}' normalized between 0 and 1")

        # Clean Text Data
        st.subheader("🔠 Clean Text Data")
        text_columns = df.select_dtypes(include=["object"]).columns.tolist()
        if text_columns:
            text_column = st.selectbox("📌 Select a text column to clean", text_columns)

            if st.button("🧹 Clean Text Data"):
                df[text_column] = df[text_column].str.strip().str.lower()
                st.success(f"✅ '{text_column}' cleaned!")

        # Data Visualization
        st.subheader("📊 Data Visualization")

        # Choose a column for visualization
        numerical_columns = df.select_dtypes(include=["number"]).columns.tolist()
        if numerical_columns:
            selected_column = st.selectbox("📊 Select a column for visualization", numerical_columns)

            # Histogram
            st.subheader(f"📈 {selected_column} Distribution")
            fig, ax = plt.subplots()
            df[selected_column].hist(ax=ax, bins=20, edgecolor="black")
            st.pyplot(fig)

            # Scatter Plot
            st.subheader("📌 Scatter Plot")
            scatter_x = st.selectbox("Select X-axis", numerical_columns)
            scatter_y = st.selectbox("Select Y-axis", numerical_columns)
            fig, ax = plt.subplots()
            ax.scatter(df[scatter_x], df[scatter_y], alpha=0.5)
            ax.set_xlabel(scatter_x)
            ax.set_ylabel(scatter_y)
            ax.set_title(f"Scatter Plot: {scatter_x} vs {scatter_y}")
            st.pyplot(fig)

        # Pie Chart for categorical data
        categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()
        if categorical_columns:
            pie_column = st.selectbox("📊 Select a categorical column for Pie Chart", categorical_columns)
            pie_data = df[pie_column].value_counts()
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Distribution of {pie_column}")
            st.pyplot(fig)

        # Correlation Heatmap
        if len(numerical_columns) > 1:
            st.subheader("🔥 Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(df[numerical_columns].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig)

        # Export Processed Data
        st.subheader("💾 Export Processed Data")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data as CSV", csv, "filtered_data.csv", "text/csv", key='download-csv')

else:
    st.warning("⚠️ Please upload a file to proceed.")

# Footer
st.markdown("🚀 **Made with Streamlit, Pandas, Matplotlib & Seaborn**")
