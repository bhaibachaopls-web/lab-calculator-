import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression



# ====== VARIABLE =======
t = 18 * 10**(-6)

# ======== Button Setup ========
def reset_calc(table_id):
    """Resets the calculation state if the user edits the table data."""
    if table_id == "Table 1": st.session_state.calc_T1 = False
    if table_id == "Table 2": st.session_state.calc_T2 = False
    else :
        st.session_state.calc_T1 = False
        st.session_state.calc_T2 = False

def trigger_T1(): st.session_state.calc_T1 = True
def trigger_T2(): st.session_state.calc_T2 = True

# --- PAGE SETUP ---
st.set_page_config(page_title="Experiment B9", page_icon="📈", layout="centered")
st.title("Experiment B₉")
st.subheader("To determine the Hall coefficient of p-type and n-type Germanium.")

# --- MEMORY INITIALIZATION ---

# _____ Button Memory _____
if 'calc_T1' not in st.session_state: st.session_state.calc_T1 = False 
if 'calc_T2' not in st.session_state: st.session_state.calc_T2 = False 

# --- INPUT HELPER FUNCTION ---
def get_table_data(method, col_names, table_id, predefined_col1=None):
    if method == "Upload File":
        file = st.file_uploader(f"Upload CSV/Excel for {table_id}", type=["csv", "xlsx"], key=f"up_{table_id}", on_change=reset_calc, args=(table_id,))
        if file is not None:
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            st.write(f"Map columns for {table_id}:")
            
            # Dynamically create selectboxes based on the number of columns requested
            cols = st.columns(len(col_names))
            mapped_data = {}
            for i, col_name in enumerate(col_names):
                selected_col = cols[i].selectbox(col_name, df.columns, key=f"c{i}_{table_id}")
                mapped_data[col_name] = df[selected_col]
            
            return pd.DataFrame(mapped_data).dropna()
        return None
    else:
        st.write(f"Enter data for {table_id}:")
        
        if predefined_col1 is not None:
            initial_df = pd.DataFrame({col_names[0]: predefined_col1})
            for col in col_names[1:]:
                initial_df[col] = None
        else:
            initial_df = pd.DataFrame(columns=col_names)
            
        df = st.data_editor(initial_df, num_rows="dynamic", key=f"edit_{table_id}", use_container_width=True, on_change=reset_calc, args=(table_id,))
        
        if not df.empty and not df.isna().all().all():          
            return df.dropna()
        return None

# --- MAIN UI ---
st.divider()
st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

tab1, tab2 = st.tabs(["Table 1: Hall voltage for constant current", "Table 2: Hall voltage for constant magnetic field"])

# ==========================================
# TAB 1: Constant current
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(
        method=input_method,
        col_names=["magnetic_field", "on_voltage", 'off_voltage'],
        table_id="Table 1",
        predefined_col1=list(range(-300, 310, 50))[::-1] 
    )
    
    if st.session_state.df1 is not None:
        st.button("Calculate", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data:')
            st.dataframe(st.session_state.df1)
            
            # ----- Table Creation------

            df1_copy = st.session_state.df1.copy()
            for col in df1_copy.columns :
                df1_copy[col] = df1_copy[col].astype(float)
            
            df1_copy['hall_voltage'] = df1_copy['on_voltage'] - df1_copy['off_voltage']
            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df1_copy)

            X = df1_copy[['magnetic_field']]
            y = df1_copy[['hall_voltage']]

            xpv = df1_copy['magnetic_field']
            yp = df1_copy['hall_voltage']
            linreg = LinearRegression()
            linreg.fit(X, y)
            slope_1 = linreg.coef_.item()
            
            # ------ Graph-------

            st.divider()
            st.subheader('Graph')
            fig, ax = plt.subplots(figsize = (11,8))
            ax.plot(xpv, yp, marker = 'o', linestyle = 'None')
            ax.plot(xpv,linreg.predict(X))
            ax = plt.gca()
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            ax.set_xlabel('Magnetic field, B (mT)', fontsize = 13)
            ax.set_ylabel('Hall Voltage', fontsize = 13)
            ax.set_title('Hall voltage as a function of magnetic field', fontsize = 18)
            ax.xaxis.set_label_coords(.75, 0.4) 
            ax.yaxis.set_label_coords(0.45, .7) 
            st.pyplot(fig)

            # ----- Calculation ------

            st.divider()
            st.subheader('Calculation')
            I = st.number_input("Enter the constant current (A):", value=None, format="%.2f")
            if I is not None or 0 :
                rh_I = slope_1*10**(-2) * (t/I)
                st.write(f'#### The value of hall coefficient : {rh_I}')
            else :
                st.write('### Enter a valid value of the current')
            



with tab2:
    st.session_state.df2 = get_table_data(
        method=input_method,
        col_names=["Current", "on_voltage", 'off_voltage'],
        table_id="Table 2",
        predefined_col1=list(range(-8, 9, 2))[::-1]
    )
    
    if st.session_state.df2 is not None:
        st.button("Calculate", type="primary", on_click=trigger_T2, key="btn_t2")
        
        if st.session_state.calc_T2:
            st.subheader('Uploaded Data:')
            st.dataframe(st.session_state.df2)
            
            # ----- Table Creation------

            df2_copy = st.session_state.df2.copy()
            for col in df2_copy.columns :
                df2_copy[col] = df2_copy[col].astype(float)
            
            df2_copy['hall_voltage'] = df2_copy['on_voltage'] - df2_copy['off_voltage']
            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df2_copy)

            X = df2_copy[['Current']]
            y = df2_copy[['hall_voltage']]

            xpv = df2_copy['Current']
            yp = df2_copy['hall_voltage']
            linreg = LinearRegression()
            linreg.fit(X, y)
            slope_1 = linreg.coef_.item()
            
            # ------ Graph-------

            st.divider()
            st.subheader('Graph')
            fig, ax = plt.subplots(figsize = (11,8))
            ax.plot(xpv, yp, marker = 'o', linestyle = 'None')
            ax.plot(xpv,linreg.predict(X))
            ax = plt.gca()
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            ax.set_xlabel('Current', fontsize = 13)
            ax.set_ylabel('Hall Voltage', fontsize = 13)
            ax.set_title('Hall voltage as a function of Current', fontsize = 18)
            ax.xaxis.set_label_coords(.75, 0.4) 
            ax.yaxis.set_label_coords(0.45, .7) 
            st.pyplot(fig)

            # ----- Calculation ------

            st.divider()
            st.subheader('Calculation')
            b_field = st.number_input("Enter the constant magnetic field (mT):", value=None, format="%.2f")
            if b_field is not None or 0 :
                rh = slope_1 *10**(-2) * (t/b_field)
                st.write(f'#### The value of hall coefficient : {rh}')
            else :
                st.write('### Enter a valid value of the magnetic field')
            
            
