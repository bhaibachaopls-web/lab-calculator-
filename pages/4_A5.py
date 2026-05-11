import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy.interpolate import PchipInterpolator

def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp = False
def trigger_math():
    st.session_state.calc_exp = True


st.set_page_config(page_title="Experiment A5", page_icon="📈", layout="centered")
st.title("A₅")
st.subheader("To study the design and construction of an Astable Multivibrator.")


st.subheader("Data Input:")
# input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])
data = {
    "Transistor": ["T1(C)", "T2(C)",'T1(B)','T2(B)'],
            't1(µs)' : ['','','',''],
            't2(µs)' : ['','','','']
}
df_raw = pd.DataFrame(data)
st.write("Type your data directly into the table below.")
df_raw = st.data_editor(df_raw, use_container_width=True, on_change=reset_calc)
df_raw['t1(µs)'] = pd.to_numeric(df_raw['t1(µs)'], errors='coerce')
df_raw['t2(µs)'] = pd.to_numeric(df_raw['t2(µs)'], errors='coerce')

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['t1(µs)', 't2(µs)'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        df = df_raw.copy()
        df['t1(µs)'] = df['t1(µs)'].astype(float)
        df['t2(µs)'] = df['t2(µs)'].astype(float)
        df['t'] = df['t1(µs)'] + df['t2(µs)']
        T = ((df['t'].sum())/len(df['t'])).item()
        st.subheader('Calculation:')
        st.write(f'#### **Average time period: {T}µs**')
        f = (1/T)* 10**6
        st.write(f'#### **Frequency : {f}Hz**')

        j = 1
        for t1,t in zip(df['t1(µs)'],df['t']) :
            D = (t1/t) * 100
            st.write(f'##### D{j} : {D}% ')
            st.write(f'##### Error in D{j} : {abs(50 - D)/.5}% ')
            j+=1
