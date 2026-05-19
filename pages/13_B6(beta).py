import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression

# ====== Variable =======
kb = 1.38 * 10 ** (-23)

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
st.set_page_config(page_title="Experiment B6", page_icon="📈", layout="centered")
st.title("Experiment B₆")
st.subheader("To determine the intrinsic energy gap of a given specimen of semiconducting material.")

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

tab1, tab2 = st.tabs(["Table 1: Increasing temperature", "Table 2: Decreasing Temperature"])

# ==========================================
# TAB 1: Constant current
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(
        method=input_method,
        col_names=["Temperature (C)", "Voltage (V)", 'Current I(mA)'],
        table_id="Table 1"
    )
    
    if st.session_state.df1 is not None:
        st.button("Calculate", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data:')
            st.dataframe(st.session_state.df1)
            
            # ----- Table Creation------

            df_inc = st.session_state.df1.copy()
            for col in df_inc.columns :
                df_inc[col] = df_inc[col].astype(float)
            
            temp_k = df_inc['Temperature (C)'] + 273
            df_inc.insert(1, 'Temp(K)', temp_k)
            one_by_t = 1 / df_inc['Temp(K)']
            df_inc.insert(1, '1/T', one_by_t)
            df_inc['R'] = df_inc['Voltage (V)'] / df_inc['Current I(mA)']
            df_inc['lnR'] = np.log(df_inc['R'] * 10**(3))
            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df_inc)
            
            # ------ Graph-------

            st.divider()
            st.subheader('Graph')

            X = df_inc[['1/T']]
            y = df_inc[['lnR']]

            linreg = LinearRegression()
            linreg.fit(X, y)

            fig, ax = plt.subplots(figsize = (11,8))
            
            ax.plot(X, y, marker = 'o', linestyle = 'None')
            ax.plot(X, linreg.predict(X))
            ax.set_xlabel ('1/T')
            ax.set_ylabel ('lnR')
            ax.set_title('lnR vs 1/T (Increasing Temperature)')
            st.pyplot(fig)

            # ----- Calculation ------

            st.divider()
            st.subheader('Calculation : 2Kb * slope')
            slope = linreg.coef_.item()
            bg = 2 * kb * slope
            st.write(f'### Slope : {slope}')
            st.write(f'#### Band Gap : {bg / (1.6 * 10 ** (-19))} eV')


            
with tab2:
    st.session_state.df2 = get_table_data(
        method=input_method,
        col_names=["Temperature (C)", "Voltage (V)", 'Current I(mA)'],
        table_id="Table 2"
    )
    
    if st.session_state.df2 is not None:
        st.button("Calculate", type="primary", on_click=trigger_T2, key="btn_t2")
        
        if st.session_state.calc_T2:
            st.subheader('Uploaded Data:')
            st.dataframe(st.session_state.df2)
            
            # ----- Table Creation------

            df_dec = st.session_state.df2.copy()
            for col in df_dec.columns :
                df_dec[col] = df_dec[col].astype(float)
            
            temp_k = df_dec['Temperature (C)'] + 273
            df_dec.insert(1, 'Temp(K)', temp_k)
            one_by_t = 1 / df_dec['Temp(K)']
            df_dec.insert(1, '1/T', one_by_t)
            df_dec['R'] = df_dec['Voltage (V)'] / df_dec['Current I(mA)']
            df_dec['lnR'] = np.log(df_dec['R'] * 10**(3))
            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df_dec)
            
            # ------ Graph-------

            X = df_dec[['1/T']]
            y = df_dec[['lnR']]

            linreg = LinearRegression()
            linreg.fit(X, y)

            fig, ax = plt.subplots(figsize = (11,8))
            
            ax.plot(X, y, marker = 'o', linestyle = 'None')
            ax.plot(X, linreg.predict(X))
            ax.set_xlabel ('1/T')
            ax.set_ylabel ('lnR')
            ax.set_title('lnR vs 1/T (Decreasing Temperature)')
            st.pyplot(fig)

            # ----- Calculation ------

            st.divider()
            st.subheader('Calculation : 2Kb * slope')
            slope = linreg.coef_.item()
            st.write(f'### Slope : {slope}')
            bg = 2 * kb * slope
            st.write(f'#### Band Gap : {bg / (1.6 * 10 ** (-19))} eV')



