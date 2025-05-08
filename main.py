import streamlit as st
import pandas as pd
import base64

# App Configuration
st.set_page_config(page_title="Data Cleanlytics - ETL + Dashboard", layout="wide")
st.title("Data Cleanlytics: Transform Your Raw Data into Clear Insights")

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Extract
    st.subheader("Uploaded Data (Raw)")
    raw_df = pd.read_csv(uploaded_file)
    st.dataframe(raw_df.head())

    # Copy for transformation
    df = raw_df.copy()

    # Transform - Cleaning
    st.subheader("Data Cleaning")
    if st.checkbox("Drop duplicate rows"):
        df = df.drop_duplicates()

    if st.checkbox("Drop rows with missing values"):
        df = df.dropna()

    # Rename Columns
    st.subheader("Rename Columns (Optional)")
    rename_map = {}
    for col in df.columns:
        new_name = st.text_input(f"Rename '{col}'", value=col)
        rename_map[col] = new_name
    df.rename(columns=rename_map, inplace=True)

    # Encode Categorical Columns with Mapping
    st.subheader("Encode Categorical Columns (with Custom Mapping)")
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if cat_cols:
        selected_cols = st.multiselect("Select categorical columns to map", cat_cols)

        for col in selected_cols:
            st.markdown(f"**Mapping for '{col}':**")
            unique_vals = df[col].dropna().unique()
            mapping = {}
            cols = st.columns(2)

            for i, val in enumerate(unique_vals):
                with cols[i % 2]:
                    mapped_val = st.number_input(f"Map '{val}' to:", key=f"{col}_{val}")
                    mapping[val] = mapped_val

            if st.button(f"Apply Mapping to '{col}'", key=f"map_{col}"):
                df[col] = df[col].map(mapping)
                st.success(f"Applied mapping to column: {col}")
                st.dataframe(df.head())
    else:
        st.info("No categorical columns found.")

    # Download Transformed Data
    st.subheader("Download Cleaned Data")
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Dashboard Visualization
    st.subheader("Data Visualization Dashboard")

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            num_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
            if num_cols:
                y_col = st.selectbox("Select numeric column to visualize", num_cols)
                chart_type = st.radio("Chart Type", ["Histogram" , "Line", "Bar"])

                if chart_type == "Line":
                    st.line_chart(df[y_col])
                elif chart_type == "Bar":
                    st.bar_chart(df[y_col])
                elif chart_type == "Histogram":
                    st.bar_chart(df[y_col].value_counts())
            else:
                st.info("No numeric columns to visualize.")

        with col2:
            cat_cols_viz = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols_viz:
                cat_col = st.selectbox("Select categorical column for frequency chart", cat_cols_viz)
                st.bar_chart(df[cat_col].value_counts())
            else:
                st.info("No categorical columns to visualize.")

# Footer
st.markdown("---")
st.markdown("Developed by **Deepan Balu**")
