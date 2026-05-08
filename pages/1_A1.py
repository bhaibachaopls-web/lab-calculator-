import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 



st.set_page_config(page_title="Experiment 1", page_icon="📈", layout="centered")
st.title("A₁")
st.subheader("To determine the impedance characteristics of an acoustic transducer.")


st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

df_raw = pd.DataFrame()

if input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
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
        
        c1 = col1.selectbox("Frequency", uploaded_cols)
        c2 = col2.selectbox("Pulse height across R₁", uploaded_cols)
        c3 = col3.selectbox('Total Pulse height', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "freq": df_raw[c1],
            "h1": df_raw[c2],
            'total' : df_raw[c3]
        })

else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    blank_template = pd.DataFrame(columns=["Frequency", "Pulse height across R₁", "Total Pulse height"])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True)




if not df_raw.empty and not df_raw.isna().all().all():
    st.divider()
    st.subheader("1. Raw Data")
    st.dataframe(df_raw, use_container_width=True)
    st.divider()
    st.subheader("Completed Data table")
    df = df_raw.copy()
    df['h2'] = df['total'] - df['h1']
    df['z'] = (df['h2'] / df['h1']) * 1000
    st.dataframe(df, use_container_width=True)

    st.subheader("2. Visualizer")
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots()
    ax.plot(df['freq'], df['z'], color='black', marker='o', markersize=4, linestyle='None')
    ax.plot(df['freq'], df['z'], color='blue', linewidth=.5)

    ax.set_title('Impedance as a function of frequency')
    ax.set_xlabel('Frequency, (KHz)')
    ax.set_ylabel('Impedance, Z(Ω)')
    ax.set_xticks(np.arange(0, 200, 20))
    ax.set_yticks(np.arange(0, 23000, 2000))
    st.pyplot(fig)
