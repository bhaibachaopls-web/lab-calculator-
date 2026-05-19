import pandas as pd
import numpy as np
from scipy.interpolate import make_smoothing_spline
from scipy.interpolate import make_interp_spline
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import streamlit as st



# ====== Variable =======
vv = .015

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
st.set_page_config(page_title="Experiment B3", page_icon="📈", layout="centered")
st.title("Experiment B₃")
st.subheader("Measurement of β-particle energy spectra of Sr⁹⁰ by energy calibration of a given magnetic spectrometer.")

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

tab1, tab2 = st.tabs(["Table 1: Count rates", "Table 2: Energy calculation"])

# ==========================================
# TAB 1: Idk
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(
        method=input_method,
        col_names=["B (mT)", "Obs 1", 'Obs 2', 'Obs 3'],
        table_id="Table 1"
    )
    
    if st.session_state.df1 is not None:
        st.button("Calculate", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data:')
            st.dataframe(st.session_state.df1)
            
            # ----- Table Creation------

            df = st.session_state.df1.copy()
            for col in df.columns :
                df[col] = df[col].astype(float)
            counts = ['Obs 1', 'Obs 2', 'Obs 3']
            df['mean_counts'] = df[counts].mean(axis=1)
            bg_count = df['mean_counts'].iloc[0]
            df['corrected_counts'] = df['mean_counts'] - bg_count
            df['n/p'] = df['corrected_counts']/df['B (mT)']
            df_clean = df.dropna()

            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df)
            st.divider()
            st.subheader('Calculation Table')
            st.dataframe(df_clean)

            table_2 = pd.DataFrame()
            table_2['p'] = df_clean['B (mT)']
            m0c2 = .511
            table_2['E'] = np.sqrt((table_2['p'] * .015)**2 + ((m0c2)**2)) - m0c2
            table_2['n/p'] = df_clean['n/p']
            table_2['p/e'] = (table_2['E'] + m0c2)/(table_2['p']*.015)
            table_2['n/e'] = table_2['n/p'] * table_2['p/e']


            st.divider()
            st.subheader('Count rates for Sr⁹⁰ per unit energy interval')
            st.dataframe(table_2)

            # =====Graph Plotting ======

            st.divider()
            st.subheader('Graphs')
            x = table_2['p']
            y = table_2['n/p']

            x_smooth = np.linspace(x.min(), x.max(), 500)
            spline = make_smoothing_spline(x,y, lam = 500)
            y_smooth = spline(x_smooth)

            fig, ax = plt.subplots(figsize = (11,8))
            ax.plot(x_smooth, y_smooth)
            ax.plot(x,y, marker = 'o', linestyle = 'None')
            ax.set_title('Count rate per unit momentum interval as a function of Momentum', fontsize  = 18)
            ax.set_xlabel('Momentum (.015 x MeV/c)',fontsize  = 13)
            ax.set_ylabel('Count rate per unit momentum interval, Δn/Δp(MeV/c)⁻¹',fontsize  = 13)
            st.pyplot(fig)
            st.info('This graph is not the best. Just notice if your shape looks GAUSSIAN or not and plot it in origin properly!')

            st.divider()
            x = table_2['E']
            y = table_2['n/e']

            x_smooth = np.linspace(x.min(), x.max(), 5000)
            spline = make_interp_spline(x,y,3)
            y_smooth = spline(x_smooth)
            fig, ax = plt.subplots(figsize = (11,8))

            ax.plot(x_smooth, y_smooth)
            ax.plot(x,y, marker = 'o', linestyle = 'None')
            ax.set_title('Count rate per unit momentum interval as a function of Energy', fontsize  = 18)
            ax.set_xlabel('Energy (MeV/c))',fontsize  = 13)
            ax.set_ylabel('Count rate per unit momentum interval, Δn/Δp(MeV/c)⁻¹',fontsize  = 13)
            st.pyplot(fig)



# ==========================================
# TAB 2: Idk(2)
# ==========================================

with tab2 :
    

        st.session_state.df2 = get_table_data(
            method=input_method, 
            col_names=["magnetic field"], 
            table_id="Table 2"
        )
        
        if st.session_state.df2 is not None:
            st.button("Calculate the energy", type="primary", on_click=trigger_T2, key="btn_t2")
        
            if st.session_state.calc_T2:
                df2_copy = st.session_state.df2.copy()
                st.subheader('Uploaded data')
                st.dataframe(df2_copy)
                st.divider()

                for col in df2_copy.columns :
                    df2_copy[col] = df2_copy[col].astype(float)

                df2_copy['p'] = np.sqrt((15 * df2_copy['magnetic field'] * 10**(-3))**2 + m0c2**2) - m0c2
                st.subheader('Completed Table')
                st.dataframe(df2_copy)
                st.divider()

                linreg = LinearRegression()
                X = df2_copy[['magnetic field']]
                y = df2_copy[['p']]

                linreg.fit(X, y)

                st.subheader('Graph')

                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(figsize = (11,8))
                ax.plot(X, y, marker = 'o', linestyle = 'None')
                ax.plot(X, linreg.predict(X))
                slope = f'slope : {linreg.coef_.item()}'
                ax.text(0.05, 0.95, slope, 
                    transform=plt.gca().transAxes,  
                    fontsize=10, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))
                ax.set_title('Calibration curve of energy as a function of magnetic field', fontsize = 18)
                ax.set_xlabel('Magnetic Induction (mT)',fontsize = 13)
                ax.set_ylabel('Energy (MeV)',fontsize = 13)

                st.pyplot(fig)



                


