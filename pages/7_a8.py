import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy.interpolate import PchipInterpolator
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit

def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp = False
def trigger_math():
    st.session_state.calc_exp = True


st.set_page_config(page_title="Experiment A8", page_icon="📈", layout="centered")
st.title("A₈")
st.subheader("Determination of the efficiency of a thermoelectric generator.")


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
        col1, col2, col3, col4, col5 = st.columns(5)
        
        c1 = col1.selectbox("time", uploaded_cols)
        c2 = col2.selectbox("high_temp", uploaded_cols)
        c3 = col3.selectbox('low_temp', uploaded_cols)
        c4 = col4.selectbox('voltage', uploaded_cols)
        c5 = col5.selectbox('current', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "time": df_raw[c1],
            "high_temp": df_raw[c2],
            'low_temp' : df_raw[c3],
            'voltage' : df_raw[c4],
            'current' : df_raw[c5]
        })
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    st.info('💡 Enter the $R_f$ value only in the first row for each new resistor. Leave the cells below it blank(if convenient); they will auto-fill.')
    blank_template = pd.DataFrame(columns=["time", "high_temp", "low_temp", 'voltage', 'current'])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=["time", "high_temp", "low_temp", 'voltage', 'current'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        # ====Table creating=====
        df = df_raw.copy()
        df['time'] = df['time'].astype(float)
        df['high_temp'] = df['high_temp'].astype(float)
        df['low_temp'] = df['low_temp'].astype(float)
        df['voltage'] = df['voltage'].astype(float)
        df['current'] = df['current'].astype(float)
        st.divider( )
        st.subheader('Uploaded data')
        st.dataframe(df)

        # ====Table calculation=====

        dt = df['high_temp'] - df['low_temp']
        df.insert(3, 'T', dt)
        df['power'] = df['voltage']*df['current']

        st.divider( )
        st.subheader('Completed Table')
        st.dataframe(df)

        # ====Graph processing=====

        linreg_v = LinearRegression()
        linreg_i = LinearRegression()
        X = df[['T']]
        y_v = df[['voltage']]
        y_i = df[['current']]
        
        linreg_v.fit(X, y_v)
        linreg_i.fit(X, y_i)

        # ====Graph plotting=====

        fig1, ax1 = plt.subplots(figsize=(11, 8))
        ax1.plot(X, y_v, marker='o', linestyle='None')
        ax1.plot(X, linreg_v.predict(X))
        ax1.axline((0, linreg_v.intercept_.item()), slope=linreg_v.coef_.item())
        ax1.set_xlabel('Temperature Difference (K)', fontsize  = 13)
        ax1.set_ylabel('Voltage (V)', fontsize  = 13)
        ax1.set_title('Voltage as a function of temperature difference', fontsize  = 18)
        text = f'Slope = {linreg_v.coef_.item()}'
        ax1.text(0.03, 0.965, text, 
                    transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                    fontsize=10, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(11, 8))
        ax2.plot(X, y_i, marker='o', linestyle='None')
        ax2.plot(X, linreg_i.predict(X))
        ax2.axline((0, linreg_i.intercept_.item()), slope=linreg_i.coef_.item())
        ax2.set_xlabel('Temperature Difference (K)', fontsize=13)
        ax2.set_ylabel('Current (A)', fontsize  = 13)
        ax2.set_title('Current as a function of temperature difference', fontsize = 18)
        text = f'Slope = {linreg_i.coef_.item()}'
        ax2.text(0.03, 0.965, text, 
                    transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                    fontsize=10, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))
        st.pyplot(fig2)


        # ==== Graph 3 =====
        time_data = df['time']
        delta_T_data = df['T']

        def cooling_model(t, A1, t1, y0):
            return A1 * np.exp(-t / t1) + y0

        y0_guess = delta_T_data.min()
        A1_guess = delta_T_data.max() - y0_guess
        t1_guess = time_data.max() / 3.0
        p0_generalized = [A1_guess, t1_guess, y0_guess]

        popt, _ = curve_fit(cooling_model, time_data, delta_T_data, p0=p0_generalized)
        A1_fit, t1_fit, y0_fit = popt

        def cooling_derivative(t, A1, t1):
            return -(A1 / t1) * np.exp(-t / t1)

        t_target = time_data.median()

        y_target = cooling_model(t_target, A1_fit, t1_fit, y0_fit)
        m = cooling_derivative(t_target, A1_fit, t1_fit)

        time_smooth = np.linspace(time_data.min(), time_data.max(), 100)
        temp_smooth = cooling_model(time_smooth, A1_fit, t1_fit, y0_fit)

        t_tangent = np.linspace(t_target - 10, t_target + 10, 200)
        y_tangent = m * (t_tangent - t_target) + y_target

        fig3, ax3 = plt.subplots(figsize=(11, 8))
        ax3.plot(time_data, delta_T_data, color='black', label='Raw Data (Delta T)', marker = 'o', linestyle = 'None')
        ax3.plot(time_smooth, temp_smooth, color='blue', label='Newtonian Cooling Fit')

        ax3.plot(t_tangent, y_tangent, color='red', linestyle='--', linewidth=2, 
                label=f'Slope at t={t_target} ({m:.3f})')
        
        ax3.set_ylabel('Temperature Difference (K)', fontsize  = 13)
        ax3.set_xlabel('Time (min)', fontsize  = 13)
        ax3.set_title('Temperature difference as a function of time curve', fontsize = 18)
        text = f'Slope = {m.item()}'
        ax3.text(0.72, 0.965, text, 
                    transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                    fontsize=10, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))
        st.pyplot(fig3)

        # ===== Graph 4 =====

        x_data = df['T']
        y_data = df['power']

        coefficients = np.polyfit(x_data, y_data, 2)
        poly_model = np.poly1d(coefficients)
        x_smooth = np.linspace(0, x_data.max(), 100)
        y_smooth = poly_model(x_smooth)


        fig4, ax4 = plt.subplots(figsize=(11, 8))
        ax4.plot(x_data, y_data, color='black', label='Calculated Power', marker = 'o', linestyle = 'None')
        ax4.plot(x_smooth, y_smooth, color='red', label='Quadratic Fit (numpy)')
        ax4.set_xlabel('Temperature Difference (K)', fontsize  = 13)
        ax4.set_ylabel('Electric Power (W)', fontsize  = 13)
        ax4.set_title('Electric Power as a function of temperature difference', fontsize = 18)
        ax4.set_xlim(left = 0)
        st.pyplot(fig4)