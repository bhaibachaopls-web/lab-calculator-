import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 


def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp2 = False
def trigger_math():
    st.session_state.calc_exp2 = True


st.set_page_config(page_title="Experiment A1", page_icon="📈", layout="centered")
st.title("A₁")
st.subheader("To determine the impedance characteristics of an acoustic transducer.")


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
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)
    df_raw = df_raw.rename(columns={
        "Frequency": "freq", 
        "Pulse height across R₁": "h1", 
        "Total Pulse height": "total"
    })

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['freq', 'h1', 'total'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp2' not in st.session_state:
    st.session_state.calc_exp2 = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click=trigger_math)
    if st.session_state.calc_exp2 :
        if len(df_clean) < 3:
            st.info("💡 Please enter at least 3 rows of data to calculate the spline curve.")
        else:    
            st.divider()
            st.subheader("1. Raw Data")
            st.dataframe(df_raw, use_container_width=True)
            st.divider()
            st.subheader("Completed Data table")
            df = df_clean.copy()
            df['freq'] = df['freq'].astype(float)
            df['h1'] = df['h1'].astype(float)
            df['total'] = df['total'].astype(float)
            df.sort_values(by= 'freq', inplace= True)
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
            ax.set_xticks(np.arange(0, max(df['freq']) + 20, 20))
            ax.set_yticks(np.arange(0, max(df['z']) + 3000, 2000))
            st.pyplot(fig)
