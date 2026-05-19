import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks



def reset_calc():
    st.session_state.calc_exp2 = False
def trigger_math():
    st.session_state.calc_exp2 = True


st.set_page_config(page_title="Experiment B4", page_icon="📈", layout="centered")
st.title("B₄")
st.subheader("A survey of gamma radiation dose rate in the experimental laboratory.")


st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

df_raw = pd.DataFrame()

if input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"], on_change=reset_calc)
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully!")
        st.success("File read successfully! Please map your columns below.")
        
        uploaded_cols = df_raw.columns.tolist()
        st.write("Match your file's columns to the required experiment variables:")
        col1, col2, col3,col4, col5,col6 = st.columns(6)
        c1 = col1.selectbox("Distance", uploaded_cols)
        c2 = col2.selectbox("count_1", uploaded_cols)
        c3 = col3.selectbox("count_2", uploaded_cols)
        c4 = col4.selectbox("count_3", uploaded_cols)
        c5 = col5.selectbox("count_4", uploaded_cols)
        c6 = col6.selectbox("count_5", uploaded_cols)

        df_raw = pd.DataFrame({
            "distance": df_raw[c1],
            "count_1": df_raw[c2],
            "count_2": df_raw[c3],
            "count_3": df_raw[c4],
            "count_4": df_raw[c5],
            "count_5": df_raw[c6]
        })
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    blank_template = pd.DataFrame(columns=["distance", 'count_1', 'count_2','count_3','count_4','count_5'])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['distance', 'count_1', 'count_2','count_3','count_4','count_5'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp2' not in st.session_state:
    st.session_state.calc_exp2 = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)
    

    if st.session_state.calc_exp2 :
        st.divider()
        st.subheader("Uploaded Data")
        st.dataframe(df_raw, use_container_width=True)
        df = df_clean.copy()
        for col in df.columns :
            df[col] = df[col].astype(float)
        st.divider()
        st.subheader("Completed Data table")
        counts = ['count_1','count_2','count_3','count_4','count_5']
        df['mean'] = df[counts].mean(axis = 1)
        st.dataframe(df)