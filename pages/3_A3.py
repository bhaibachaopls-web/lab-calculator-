import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks


# ======== Button Setup ========
# def reset_calc():
#     st.session_state.calc_exp2 = False
# def trigger_math():
#     st.session_state.calc_exp2 = True
def reset_calc(table_id):
    """Resets the calculation state if the user edits the table data."""
    if table_id == "Table 1": st.session_state.calc_T1 = False
    if table_id == "Table 2": st.session_state.calc_T2 = False
    if table_id == "Table 3": st.session_state.calc_T3 = False
    else :
        st.session_state.calc_T1 = False
        st.session_state.calc_T2 = False
        st.session_state.calc_T3 = False

def trigger_T1(): st.session_state.calc_T1 = True
def trigger_T2(): st.session_state.calc_T2 = True
def trigger_T3(): st.session_state.calc_T3 = True

# --- PAGE SETUP ---
st.set_page_config(page_title="Experiment A3", page_icon="📈", layout="centered")
st.title("Experiment A₃")
st.subheader("""Using microwave radiation investigation of:             
 i) Interference pattern by a double slit setup.
 ii) Determination of wavelength by Fabry-Perot Interferometer
 iii) Determination of spacing between two crystal planes by Bragg diffraction.
""")

# --- MEMORY INITIALIZATION ---
if 'lambda_1' not in st.session_state: st.session_state.lambda_1 = None
if 'lambda_2' not in st.session_state: st.session_state.lambda_2 = None
if 'df1' not in st.session_state: st.session_state.df1 = None
if 'df2' not in st.session_state: st.session_state.df2 = None
# _____ Button Memory_____
if 'calc_T1' not in st.session_state: st.session_state.calc_T1 = False 
if 'calc_T2' not in st.session_state: st.session_state.calc_T2 = False 
if 'calc_T3' not in st.session_state: st.session_state.calc_T3 = False

# --- INPUT HELPER FUNCTION ---
# --- INPUT HELPER FUNCTION ---
def get_table_data(method, col_names, table_id, ffill_col=None):
    if method == "Upload File":
        file = st.file_uploader(f"Upload CSV/Excel for {table_id}", type=["csv", "xlsx"], key=f"up_{table_id}", on_change=reset_calc, args=(table_id,))
        if file is not None:
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            st.write(f"Map columns for {table_id}:")
            c1, c2 = st.columns(2)
            col1 = c1.selectbox(col_names[0], df.columns, key=f"c1_{table_id}")
            col2 = c2.selectbox(col_names[1], df.columns, key=f"c2_{table_id}")
            
            # Build the mapped dataframe
            mapped_df = pd.DataFrame({col_names[0]: df[col1], col_names[1]: df[col2]})
            
            # Apply Forward Fill if requested, BEFORE dropping NA
            if ffill_col: mapped_df[ffill_col] = mapped_df[ffill_col].ffill()
            
            return mapped_df.dropna()
        return None
    else:
        st.write(f"Enter data for {table_id}:")
        df = st.data_editor(pd.DataFrame(columns=col_names), num_rows="dynamic", key=f"edit_{table_id}", use_container_width=True, on_change=reset_calc, args=(table_id,))
        if not df.empty and not df.isna().all().all():
            
            # Apply Forward Fill if requested, BEFORE dropping NA
            if ffill_col: df[ffill_col] = df[ffill_col].ffill()
                
            return df.dropna()
        return None

# --- MAIN UI ---
st.divider()
st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

# creating the tables
tab1, tab2, tab3 = st.tabs(["Table 1: Double Slit", "Table 2: Fabry-Perot", "Table 3: Bragg Diffraction 🔒"])

# ==========================================
# TAB 1: DOUBLE SLIT
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(input_method,
                                        ["Angle", "Meter Reading"],
                                        "Table 1")
    
    if st.session_state.df1 is not None:
        st.button("Calculate Double Slit", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data :')
            st.dataframe(st.session_state.df1, use_container_width = True)
            
            df1_copy = st.session_state.df1.copy()
            df1_copy['Angle'] = df1_copy['Angle'].astype(float)
            df1_copy['Meter Reading'] = df1_copy['Meter Reading'].astype(float)
            df1_copy['meter_reading_norm'] = df1_copy['Meter Reading']/df1_copy['Meter Reading'].max()
            
            st.subheader('Completed Data table for Double Slit')
            st.dataframe(df1_copy, use_container_width = True)

            # ====== Calculation =======

            x_1 = df1_copy['Angle']
            y_1 = df1_copy['meter_reading_norm']

            x_smooth_1 = np.linspace(x_1.min(), x_1.max(), 500)
            spline_1 = make_interp_spline(x_1,y_1, 3)
            y_smooth_1 = spline_1(x_smooth_1)
            peak_indices_1, properties_1 = find_peaks(y_smooth_1, prominence=0.1)

            peak_distances_1 = x_smooth_1[peak_indices_1]
            peak_height_1 = y_smooth_1[peak_indices_1]
            
            # --- SAVE & DISPLAY ---


            st.subheader('Graph for double slit')
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize = (10,6))
            ax.set_title("Normalized meter reading as a function of angle")
            ax.set_xlabel('Angle (degrees)')
            ax.set_ylabel('Normalized meter reading')
            ax.plot(x_1,y_1,
                    marker = 'o',
                    markersize = 4,
                    linestyle = 'None')
            ax.plot(x_smooth_1, y_smooth_1, color = 'Blue')
            ax.annotate(
                text = 'First maxima, n = 1',
                xy = (peak_distances_1[0], peak_height_1[0]),
                xytext=(peak_distances_1[0], peak_height_1[0] + 0.03)
            )
            ax.annotate(
                text = 'Second maxima, n = 2',
                xy = (peak_distances_1[1], peak_height_1[1]),
                xytext=(peak_distances_1[1], peak_height_1[1] + 0.03)
            )
            ax.set_xlim(left = 0)
            ax.set_yticks(np.arange(0,max(y_1) + .3,.2))
            st.pyplot(fig)
            # plt.ylim(bottom = 0)
            st.subheader('Calculation( ($\lambda_1$) = dsin(θ)/n')
            wvl = []
            for i in range(2) :
                wvl.append((8 * np.sin(np.radians(peak_distances_1[i]))) / (i + 1))
            j = 0
            for i in wvl :
                st.write(f'λ{j + 1}: {i}')
                print(f'λ{j + 1}: {i}')
                j += 1
            avg = sum(wvl)/len(wvl)
            st.write(f'λ: {avg}')
            calculated_lambda_1 = avg

            st.session_state.lambda_1 = calculated_lambda_1
            st.success(f"Double Slit Wavelength ($\lambda_1$): **{st.session_state.lambda_1:.4f} cm**")

            # =====Error======

            st.subheader('Error in Fabry Perot setup')
            error = (2.85 - calculated_lambda_1)/2.85
            st.write(f'Error: {abs(error)}%')
# ==========================================
# TAB 2: FABRY-PEROT
# ==========================================
# ==========================================
# TAB 2: FABRY-PEROT
# ==========================================
with tab2:    
    st.info('💡 In the d1 tab, writing only one value would still work. no need to fill all the cells for d1!')
    st.session_state.df2 = get_table_data(
        method=input_method, 
        col_names=["Position of second plate d2 (cm)", "Position of first plate d1 (cm)"], 
        table_id="Table 2",
        ffill_col="Position of first plate d1 (cm)"
    )
    
    if st.session_state.df2 is not None:
        st.button("Calculate Fabry Perot", type="primary", on_click=trigger_T2, key="btn_t2")
        
        if st.session_state.calc_T2:
            df2_copy = st.session_state.df2.copy()
            
            st.subheader("Input Table")
            st.dataframe(df2_copy, use_container_width=True)
            df2_copy['Position of second plate d2 (cm)'] = df2_copy['Position of second plate d2 (cm)'].astype(float)
            df2_copy["Position of first plate d1 (cm)"] = df2_copy["Position of first plate d1 (cm)"].astype(float)

            
            df2_copy['d2 - d1'] = df2_copy['Position of second plate d2 (cm)'] - df2_copy["Position of first plate d1 (cm)"]
            df2_copy['D(consecutive distance)'] = df2_copy['d2 - d1'].diff()
            df2_copy['ለ'] = df2_copy['D(consecutive distance)'] * 2
            df2_copy['ለ_avg'] = df2_copy['ለ'].mean()

            st.subheader('Completed Data table for the Febry Perot setup')
            st.dataframe(df2_copy, use_container_width=True)
            
            calculated_lambda_2 = df2_copy['ለ_avg'].iloc[0]
            
            # --- SAVE & DISPLAY ---
            st.session_state.lambda_2 = calculated_lambda_2
            st.success(f"Fabry-Perot Wavelength ($\lambda_2$): **{st.session_state.lambda_2:.4f} cm**")

            # =====Calculation=======
            st.subheader('Error in Fabry Perot setup')
            error_2 = (2.85 - calculated_lambda_2)/2.85
            st.write(f'Error: {abs(error_2)}%')
# ==========================================
# TAB 3: BRAGG DIFFRACTION (LOCKED)
# ==========================================
with tab3:
    # Gatekeeper: Ensures Table 1 and 2 are done first
    if st.session_state.lambda_1 is not None and st.session_state.lambda_2 is not None:
        st.success("Wavelengths calculated from Tables 1 and 2! You can now process Table 3.")
        
        # Calculate and display the combined average wavelength
        avg_lambda = (st.session_state.lambda_1 + st.session_state.lambda_2) / 2
        st.info(f"Using combined average wavelength ($\lambda$): **{avg_lambda:.4f} cm**")
        
        df3 = get_table_data(input_method, ["Angle (deg)", "Meter Reading (mA)"], "Table 3")
        
        if df3 is not None:
            # Extract data columns as numpy arrays for SciPy
            x = df3["Angle (deg)"].to_numpy()
            y = df3["Meter Reading (mA)"].to_numpy()
            

            x_smooth = np.linspace(x.min(), x.max(), 300)
            spline = make_interp_spline(x, y, k=3)
            y_smooth = spline(x_smooth)
            
            # --- 2. PEAK FINDING (From your Screenshot) ---
            peak_indices, properties = find_peaks(y_smooth, prominence=0.04)
            peak_distances = x_smooth[peak_indices]
            peak_height = y_smooth[peak_indices]
            
            # --- 3. PHYSICS CALCULATIONS ---
            first_peak = np.argmax(peak_height).item()
            remaining_values = peak_height[first_peak + 1:]

            if len(remaining_values) == 0 :
                st.write("Your second maxima is too small.Redo the last part for a better data")
            else :
                second_peak = np.argmax(remaining_values).item()
                second_peak = first_peak + 1 + second_peak
            
            # --- 5. VISUALIZER ---
            st.subheader("Graph for Bragg diffraction")
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize=(8, 5))
            
            ax.plot(x, y, 'o', color='#343ff3')
            ax.plot(x_smooth, y_smooth, '-', color='green')
            ax.annotate(
                text = 'First maxima',
                xy = (peak_distances[first_peak], peak_height[first_peak]),
                xytext=(peak_distances[first_peak], peak_height[first_peak] + 0.03)
            )
            ax.annotate(
                text = 'Second maxima',
                xy = (peak_distances[second_peak], peak_height[second_peak]),
                xytext=(peak_distances[second_peak], peak_height[second_peak] + 0.03)
            )
            
            ax.set_title('Intensity as a function of angle', fontsize=14, pad=15)
            ax.set_xlabel('Angle (degrees)', fontsize=12)
            ax.set_ylabel('Intensity (mA)', fontsize=12)
            ax.set_xticks(np.arange(0,max(x) + 3,5))
            ax.set_yticks(np.arange(0,max(y) + .1, .05))
            
            st.pyplot(fig)
            
            # ====== Calculation =======
            st.subheader('Calculation for Bragg Diffraction')
            st.write(f'Using ($\lambda$): **{avg_lambda:.4f} cm**')
            st.write('d = nλ/2sinθ')
            d1 = avg_lambda / (2 *np.sin(np.radians(peak_distances[first_peak])))
            d2 = (2 *avg_lambda) / (2 *np.sin(np.radians(peak_distances[second_peak])))
            st.write(f'd1: {d1}')
            st.write(f'd2: {d2}')
            st.write(f'Average d : {(d1 + d2)/2}')


    else:
        st.info("🔒 Please click the Calculate buttons in both Table 1 and Table 2 to unlock this section.")