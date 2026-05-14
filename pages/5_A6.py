import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy.interpolate import PchipInterpolator
from scipy import stats
def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp = False
def trigger_math():
    st.session_state.calc_exp = True


st.set_page_config(page_title="Experiment A6", page_icon="📈", layout="centered")
st.title("A₆")
st.subheader("To construct saw tooth wave generator using Unijunction transistor (UJT) Relaxing oscillator and to calculate its frequency.")


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
        col1, col2, col3 = st.columns(3)
        
        c1 = col1.selectbox("resistance", uploaded_cols)
        c2 = col2.selectbox("Capacitance", uploaded_cols)
        c3 = col3.selectbox('time', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "resistance": df_raw[c1],
            "Capacitance": df_raw[c2],
            'time' : df_raw[c3]
        })
        if df_raw['resistance'].isna().any() :
            df_raw["resistance"] = df_raw["resistance"].ffill()
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    st.info('💡 Enter the Capacitance value only in the first row for each new resistor. Leave the cells below it blank(if convenient); they will auto-fill.')
    blank_template = pd.DataFrame(columns=["resistance", "Capacitance", "time"])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)
    df_raw["Capacitance"] = df_raw["Capacitance"].ffill()

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['resistance', 'Capacitance', 'time'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        df = df_raw.copy()
        df['resistance'] = df['resistance'].astype(float)
        df['Capacitance'] = df['Capacitance'].astype(float)
        df['time'] = df['time'].astype(float)
        unique_c = df['Capacitance'].unique()
        eta1 = []
        sigma1 = []
        st.subheader('Data table and calculation for each capacitor')
        for c in unique_c :
            df_x = df[df['Capacitance'] == c].copy()
            df_x['frequency'] = 1/df_x['time']
            df_x['η'] = 1 - np.exp(-df_x['time']/ (df_x['resistance'] *(c)))
            # df_x['nmean'] = df_x['η'].mean()
            st.write(f'#### For C = {c}µF')
            st.dataframe(df_x)
            eta1.append(df_x['η'].mean())
            std = stats.sem(df_x['η']).item()
            sigma1.append(std)
            mean_val = df_x['η'].mean().item()
            st.write(f'##### η(mean) = {mean_val}')
            st.write(f'##### σ : {std}')
            eta = np.array(eta1)
            sigma = np.array(sigma1)
        weights = 1/sigma**2
        result = np.average(eta, weights=weights)
        numerator = np.sum(eta / sigma**2)
        denominator = np.sum(1 / sigma**2)
        result_manual = numerator / denominator
        st.write(f'Intrinsic stand off ratio (η) : {result_manual}')
    
    