import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import streamlit as st


def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp = False
def trigger_math():
    st.session_state.calc_exp = True


st.set_page_config(page_title="Experiment B7", page_icon="📈", layout="centered")
st.title("B₇")
st.subheader("To study the temperature dependence of reverse saturation current of a p-n junction diode and hence determine the intrinsic forbidden energygap (E/) of the semiconductor material.")


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
        
        c1 = col1.selectbox("Temperature", uploaded_cols)
        c2 = col2.selectbox("Voltage", uploaded_cols)
        c3 = col3.selectbox('Current', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "Temperature": df_raw[c1],
            "Voltage": df_raw[c2],
            'Current' : df_raw[c3]
        })
        
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    # st.info('💡 Enter the Capacitance value only in the first row for each new resistor. Leave the cells below it blank(if convenient); they will auto-fill.')
    blank_template = pd.DataFrame(columns=["Temperature", "Voltage", "Current"])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)
    if df_raw['Temperature'].isna().any() :
            df_raw["Temperature"] = df_raw["Temperature"].ffill()

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['Temperature', 'Voltage', 'Current'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        df = df_clean.copy()

        st.subheader('Uploaded Data')
        st.dataframe(df)

        df['Temperature'] = df['Temperature'].astype(float)
        df['Voltage'] = df['Voltage'].astype(float)
        df['Current'] = df['Current'].astype(float)
        df.rename(columns={'Temperature' : 'temperature', 'Current' : 'current'}, inplace= True)
        df['I0'] = df.groupby('temperature')['current'].transform('mean')
        temp = 1/(df['temperature'] + 273)
        df['lnI0'] = np.log(df['I0'])
        df.insert(1,'1/T', temp)
        df['1/T²'] = df['1/T'] ** 2
        df = df[['temperature', '1/T', 'Voltage', 'current', 'I0', 'lnI0', '1/T²']]

        df_reg = df[['1/T', 'lnI0']].drop_duplicates()

        df_reg = df[['1/T', 'lnI0']].drop_duplicates()

        X_up = df_reg[['1/T']] * 1000
        y_up = df_reg[['lnI0']]

        linreg = LinearRegression()
        linreg.fit(X_up, y_up)

        st.divider()
        st.subheader('Completed Table')
        st.dataframe(df)

        st.divider()
        st.subheader('Visualization')

        plt.style.use('seaborn-v0_8-whitegrid')
        
        # --- First Graph: I-V Characteristics ---

        st.subheader('Graph: I-V Characteristics')

        fig1, ax1 = plt.subplots(figsize=(11, 8))
        temps = df['temperature'].unique()

        for temp in temps:
            df_x = df[df['temperature'] == temp]
            x = [0] + df_x['Voltage'].tolist()
            y = [0] + df_x['current'].tolist()
            
            ax1.plot(df_x['Voltage'], df_x['current'], marker='o', linestyle='None')
            ax1.plot(x, y, label=f'{temp}℃')

        ax1.set_xlabel('Reverse voltage, V')
        ax1.set_ylabel('Reverse current (µA)')
        ax1.legend()
        
        st.pyplot(fig1)


        # --- Second Graph: Linear Regression ---
        st.subheader('Graph: For Bandgap')

        fig2, ax2 = plt.subplots(figsize=(11, 8))

        slope_inc = linreg.coef_.item()
        box = 'slope = ' + str(round(slope_inc, 4)) 
        
        ax2.scatter(X_up, y_up, color='black')
        ax2.plot(X_up, linreg.predict(X_up), color='black')
        
        # Use correct object-oriented setter methods
        ax2.set_title('lnI0 as a function of 1/T (for increasing temperature)')
        ax2.set_xlabel('1/T x 10⁻³ (K⁻¹)')
        ax2.set_ylabel('lnI0 (µA)')
        
        # Anchor text to the correct axis (ax2)
        ax2.text(0.55, 0.95, box,
                transform=ax2.transAxes,  
                fontsize=10, 
                verticalalignment='top', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))
        
        # Render the second figure
        st.pyplot(fig2)
        st.divider()
        st.subheader('Calculation : Eg = -(slope*1000 * k)/1eV')
        slope = -linreg.coef_.item()
        eg = slope * 1000 * (1.38*10**(-23))
        st.write(f'##### Band-gap : {eg/(1.6 * 10**-19)}')