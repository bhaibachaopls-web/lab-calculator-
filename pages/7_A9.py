import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression

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
st.set_page_config(page_title="Experiment B11", page_icon="📈", layout="centered")
st.title("Experiment A₉")
st.subheader("Experimentally verify the Stefan-Boltzmann's Law of radiation and determine Stefan-Boltzmann constant.")

# --- MEMORY INITIALIZATION ---
if 'avg_resistance' not in st.session_state: st.session_state.avg_resistance = None
if 'df1' not in st.session_state: st.session_state.df1 = None
if 'df2' not in st.session_state: st.session_state.df2 = None

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
        
        # If we passed predefined constants (like 50, 100 for Table 1), pre-fill them!
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

# creating the tables
tab1, tab2 = st.tabs(["Table 1: Room Temp Resistance", "Table 2: Thermopile Voltage & Temperature 🔒"])

# ==========================================
# TAB 1: ROOM TEMP RESISTANCE
# ==========================================
with tab1:
    # Notice we pass [50, 100] as the predefined_col1 argument to lock in the currents
    st.session_state.df1 = get_table_data(
        method=input_method,
        col_names=["Current I (mA)", "Voltage V (V)"],
        table_id="Table 1",
        predefined_col1=[50, 100] 
    )
    
    if st.session_state.df1 is not None:
        st.button("Calculate Room Temp Resistance", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data:')
            
            df1_copy = st.session_state.df1.copy()
            df1_copy['Current I (mA)'] = df1_copy['Current I (mA)'].astype(float)
            df1_copy['Voltage V (V)'] = df1_copy['Voltage V (V)'].astype(float)
            df1_copy.rename(columns={'Voltage V (V)' : 'Voltage', 'Current I (mA)' : 'I'}, inplace= True)
            
            df1_copy['Voltage'] = df1_copy['Voltage']/ (2 * np.sqrt(2))
            df1_copy['Resistance'] = df1_copy['Voltage']/(df1_copy['I']/1000)
            
            st.dataframe(df1_copy, use_container_width=True)
            
            calculated_avg_R = df1_copy['Resistance'].mean()
            
            # --- 2. SAVE TO MEMORY FOR TAB 2 ---
            st.session_state.avg_resistance = calculated_avg_R
            
            st.success(f"Average Room Temp Resistance ($R(t_r)$): **{st.session_state.avg_resistance:.4f} Ω**")

# ==========================================
# TAB 2: THERMOPILE & TEMPERATURE
# ==========================================
with tab2:    
    # GATEKEEPER: Checks if Table 1's math is finished
    if st.session_state.avg_resistance is not None:
        st.success("Room Temp Resistance calculated! You can now process Table 2.")
        st.info(f"Using $R(t_r)$ = **{st.session_state.avg_resistance:.4f} Ω**")

        # Table 2 has 3 input columns, and no predefined constants
        st.session_state.df2 = get_table_data(
            method=input_method, 
            col_names=["I ", "Voltage", "Utherm"], 
            table_id="Table 2"
        )
        
        if st.session_state.df2 is not None:
            st.info("⚠️ DON'T convert Utherm into mV. Keep it as it is" )
            st.button("Calculate Stefan-Boltzmann Data", type="primary", on_click=trigger_T2, key="btn_t2")
        
            if st.session_state.calc_T2:
                df2_copy = st.session_state.df2.copy()
                
                # Clean strings to floats
                for col in df2_copy.columns:
                    df2_copy[col] = df2_copy[col].astype(float)
                
                df2_copy['Voltage'] = df2_copy['Voltage']/ (2 * np.sqrt(2))
                R = df2_copy['Voltage']/(df2_copy['I '])
                df2_copy.insert(2, 'Resistance', R)
                t = 273 + (1 / (2 * 6.76e-7)) * (np.sqrt((4.82e-3)**2 + 4 * 6.76e-7 * ((df2_copy['Resistance']/calculated_avg_R) - 1)) - 4.82e-3)
                df2_copy.insert(3, 'T', t)
                lg = np.log(df2_copy['T'])
                df2_copy.insert(4, 'lnT', lg)
                df2_copy['Utherm'] = df2_copy['Utherm'] * 1000
                df2_copy['ln_Utherm']= np.log(df2_copy['Utherm'])
                        
               
                st.subheader('Processed Data Table')
                st.dataframe(df2_copy, use_container_width=True)

                linreg = LinearRegression()
                linreg.fit(df2_copy[['lnT']], df2_copy[['ln_Utherm']])
                X = df2_copy[['lnT']]
                
                # --- 4. INSERT YOUR GRAPH AND LINEAR REGRESSION HERE ---
                
                st.subheader('Visualization')
                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(figsize=(11, 8))
                
                ax.plot(X, linreg.predict(X), color = 'black')
                ax.scatter(X, df2_copy['ln_Utherm'],color = 'black')
                ax.set_xticks(np.arange(df2_copy['lnT'].min() - .1, df2_copy['lnT'].max() + .1, .1 ))
                ax.set_yticks(np.arange(df2_copy['ln_Utherm'].min() - .29, df2_copy['ln_Utherm'].max() + .45, .3 ))

                plt.title('Energy flux as a function of temperature',fontsize = 18)
                ax.set_xlabel('LnT', fontsize = 13)
                ax.set_ylabel('ln (Utherm)',fontsize = 13)
                slope = f'Slope : {linreg.coef_.item()}'
                plt.text(0.025, 0.96, slope, 
                            transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                            fontsize=15, 
                            verticalalignment='top', 
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))

                st.pyplot(fig)
                
                st.divider()
                st.subheader('Result')
                st.write(f"##### Slope: {linreg.coef_.item() : .4f}")
                # st.write(f"Stefan-Boltzmann Constant: ...")

    else:
        st.info("🔒 Please calculate the Room Temp Resistance in Table 1 to unlock this section.")