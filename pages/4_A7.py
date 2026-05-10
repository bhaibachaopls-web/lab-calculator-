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


st.set_page_config(page_title="Experiment A7", page_icon="📈", layout="centered")
st.title("A₇")
st.subheader("Design and construction of a summing amplifier using OP-AMP.")


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
        
        c1 = col1.selectbox("Rf(KΩ)", uploaded_cols)
        c2 = col2.selectbox("V₁", uploaded_cols)
        c3 = col3.selectbox('Measured_Vout', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "Rf(KΩ)": df_raw[c1],
            "V₁": df_raw[c2],
            'Measured_Vout' : df_raw[c3]
        })
        if df_raw['Rf(KΩ)'].isna().any() :
            df_raw["Rf(KΩ)"] = df_raw["Rf(KΩ)"].ffill()
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    st.info('💡 Enter the $R_f$ value only in the first row for each new resistor. Leave the cells below it blank; they will auto-fill.)')
    blank_template = pd.DataFrame(columns=["Rf(KΩ)", "V₁", "Measured_Vout"])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)
    df_raw["Rf(KΩ)"] = df_raw["Rf(KΩ)"].ffill()

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['Rf(KΩ)', 'V₁', 'Measured_Vout'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        df = df_raw.copy()
        av = df['Rf(KΩ)'] / 10
        df.insert(1,'Av', value= av)
        V2 = df['V₁']
        df.insert(3, 'V₂', value= V2)
        added = df['V₁'] + df['V₂'] 
        df.insert(4,'V₁ + V₂', value= added)
        expected = df['Av'] * df['V₁ + V₂']
        df.insert(5, 'V0', value= expected)
        df['Error'] = df['V0'] - df['Measured_Vout']
        resistances = (df['Rf(KΩ)'].unique())
        def create_table_and_graph(df_x) :
            not_smoothened_list = []
            smoothened_list = []
            for resistance in resistances :
                df_x = df[df['Rf(KΩ)'] == resistance]
                df_x.sort_values(by= 'V₁', inplace= True)
                st.subheader(f'Table for Rf = {resistance}KΩ')
                st.dataframe(df_x)
                # =====Calculation for graph======
                X = df_x['V₁ + V₂'].to_numpy()
                y = df_x['Measured_Vout'].to_numpy()
                not_smoothened_coords = (X,y)
                not_smoothened_list.append(not_smoothened_coords)
                x_smooth = np.linspace(0, X.max(), 500)
                spline = PchipInterpolator(X,y)
                y_smooth = spline(x_smooth)
                smoothened_coords = (x_smooth, y_smooth, resistance)
                smoothened_list.append(smoothened_coords)
            #=====Plotting Graph=====
            st.subheader('Graph')
            fig, ax = plt.subplots(figsize=(11, 8))
            ax.set_xticks(np.arange(0, max(df['V₁ + V₂']) + 4, 1))
            ax.set_yticks(np.arange(0, max(df['Measured_Vout']) + 3, 1))
            ax.set_xlim(0,max(df['V₁ + V₂']) + 1)
            ax.set_ylim(0,max(df['Measured_Vout']) + .8)
            for x_ns, y_ns in not_smoothened_list :
                ax.plot(x_ns, y_ns, marker = 'o', markersize = 4, linestyle = 'None')
            for x_s, y_s, res in smoothened_list :
                ax.plot(x_s,y_s, label = f'{res}Ω')
            ax.set_title(r'Measured voltage as a function of $V_1 + V_2$')
            ax.set_xlabel(r'$V_1 + V_2$ (V)')
            ax.set_ylabel('Measured voltage (V)')
            ax.legend()
            st.pyplot(fig)
            st.info('📝 Note that the lines might not always look the best(sometimes they show up kinda squiggly with inaccurate data.) (Basically the spline/PchipInterpolator are not the best functions for this specific graph. I am just too lazy to code it properly🙄)')
        create_table_and_graph(df)