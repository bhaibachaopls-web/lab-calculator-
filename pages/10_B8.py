import pandas as pd 
import streamlit as st 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy.interpolate import PchipInterpolator
from sklearn.linear_model import LinearRegression


linreg = LinearRegression()

def reset_calc():
    # This forces the app to "forget" the button click
    st.session_state.calc_exp = False
def trigger_math():
    st.session_state.calc_exp = True


st.set_page_config(page_title="Experiment B8", page_icon="📈", layout="centered")
st.title("B₈")
st.subheader("""To study depletion capacitance of a given p-n junction with reverse bias voltage and hence to find the
            (i) contact potential V0 and 
            (ii) intrinsic capacitance C₀
            """)



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
        c2 = col2.selectbox("Reverse Voltage (V)", uploaded_cols)
        c3 = col3.selectbox('cap', uploaded_cols)

        
        df_raw = pd.DataFrame({
            "Frequency": df_raw[c1],
            "Reverse Voltage (V)": df_raw[c2],
            'cap' : df_raw[c3]
        })
        if df_raw['Frequency'].isna().any() :
            df_raw["Frequency"] = df_raw["Frequency"].ffill()
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    st.info('💡 Enter the Frequency value only in the first row for each new frequency. Leave the cells below it blank(if convenient); they will auto-fill.')
    blank_template = pd.DataFrame(columns=["Frequency", "Reverse Voltage (V)", "cap"])
    df_raw = st.data_editor(blank_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)
    df_raw["Frequency"] = df_raw["Frequency"].ffill()

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['Frequency', 'Reverse Voltage (V)', 'cap'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp' not in st.session_state:
    st.session_state.calc_exp = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)

    if st.session_state.calc_exp :
        df_testing = df_raw.copy()
        freq_lst = df_testing['Frequency'].unique()

        for freq in freq_lst :
            df_x = df_testing[df_testing['Frequency'] == freq]
            df_x['1/c²'] = 1/df_x['cap'] ** 2
            X = df_x[['Reverse Voltage (V)']]
            y = df_x[['1/c²']]
            st.dataframe(df_x)
            linreg.fit(X, y)
            slope_scalar = linreg.coef_.item()
            intercept_scalar = linreg.intercept_.item()
            xmax = df_x['Reverse Voltage (V)'].max()
            ymax = df_x['1/c²'].max()
            text_box_content = f"Slope (m): {slope_scalar:.8f}\nIntercept (c): {intercept_scalar:.8f}"
            
            fig, ax = plt.subplots(figsize=(11, 8))

            ax.plot(X, y, color = 'black')
            ax.plot(X, linreg.predict(X), color = 'black')

            ax.set_xticks(np.arange(-xmax - 1, xmax + 1, 1))
            ax.set_yticks(np.arange(0.001,ymax + .008 , .002))

            ax.text(0.05, 0.95, text_box_content, 
                    transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                    fontsize=10, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))

            plt.title(f'1/c² as a function of reverse voltage(frequency = {freq})')
            # plt.xlabel('Reverse Voltage(V)')
            plt.ticklabel_format(style='plain', axis='y')
            # plt.ylabel('1/c² (pF²)')
            ax = plt.gca()
            ax.set_xlabel('Reverse Voltage(V)')
            ax.set_ylabel('1/c² (pF²)')

            # (x, y) placement. Adjust the decimals to align exactly with your axes.
            ax.xaxis.set_label_coords(.7, 0.071) # 1.0 puts it on the far right
            ax.yaxis.set_label_coords(0.38, .6) # 1.0 puts it at the very top
            plt.axline((0, intercept_scalar), slope= slope_scalar, color = 'black')
            plt.xlim(-xmax - 1,xmax + 1)
            plt.ylim(-0.001,ymax + .008)
            ax = plt.gca()
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            plt.show()
            st.pyplot(fig)

            