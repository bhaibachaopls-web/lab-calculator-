import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks

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

# --- INPUT HELPER FUNCTION ---
def get_table_data(method, col_names, table_id):
    """Handles both file uploading and manual data entry cleanly."""
    if method == "Upload File":
        file = st.file_uploader(f"Upload CSV/Excel for {table_id}", type=["csv", "xlsx"], key=f"up_{table_id}")
        if file is not None:
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            st.write(f"Map columns for {table_id}:")
            c1, c2 = st.columns(2)
            col1 = c1.selectbox(col_names[0], df.columns, key=f"c1_{table_id}")
            col2 = c2.selectbox(col_names[1], df.columns, key=f"c2_{table_id}")
            return pd.DataFrame({col_names[0]: df[col1], col_names[1]: df[col2]}).dropna()
        return None
    else:
        st.write(f"Enter data for {table_id}:")
        df = st.data_editor(pd.DataFrame(columns=col_names), num_rows="dynamic", key=f"edit_{table_id}", use_container_width=True)
        if not df.empty and not df.isna().all().all():
            return df.dropna()
        return None

# --- MAIN UI ---
st.divider()
st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

# Create the three tabs
tab1, tab2, tab3 = st.tabs(["Table 1: Double Slit", "Table 2: Fabry-Perot", "Table 3: Bragg Diffraction 🔒"])

# ==========================================
# TAB 1: DOUBLE SLIT
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(input_method, ["Angle (deg)", "Meter Reading (mA)"], "Table 1")
    
    if st.session_state.df1 is not None:
        
        # --- 1. DO YOUR TAB 1 MATH HERE ---
        # Extract variables from st.session_state.df1 and calculate lambda
        
        calculated_lambda_1 = 2.782 # REPLACE this hardcoded value with your actual variable
        
        # --- 2. SAVE & DISPLAY ---
        st.session_state.lambda_1 = calculated_lambda_1
        st.success(f"Double Slit Wavelength ($\lambda_1$): **{st.session_state.lambda_1:.4f} cm**")

# ==========================================
# TAB 2: FABRY-PEROT
# ==========================================
with tab2:
    st.session_state.df2 = get_table_data(input_method, ["Plate Position d2 (cm)", "Consecutive Maxima D (cm)"], "Table 2")
    
    if st.session_state.df2 is not None:
        
        # --- 1. DO YOUR TAB 2 MATH HERE ---
        # Extract variables from st.session_state.df2 and calculate lambda
        
        calculated_lambda_2 = 2.815 # REPLACE this hardcoded value with your actual variable
        
        # --- 2. SAVE & DISPLAY ---
        st.session_state.lambda_2 = calculated_lambda_2
        st.success(f"Fabry-Perot Wavelength ($\lambda_2$): **{st.session_state.lambda_2:.4f} cm**")

# ==========================================
# TAB 3: BRAGG DIFFRACTION (LOCKED)
# ==========================================
with tab3:
    # Gatekeeper: Ensures Table 1 and 2 are done first
    if st.session_state.df1 is not None and st.session_state.df2 is not None:
        st.success("Tables 1 and 2 confirmed! You can now process Table 3.")
        
        # Calculate and display the combined average wavelength
        avg_lambda = (st.session_state.lambda_1 + st.session_state.lambda_2) / 2
        st.info(f"Using combined average wavelength ($\lambda$): **{avg_lambda:.4f} cm**")
        
        df3 = get_table_data(input_method, ["Angle (deg)", "Meter Reading (mA)"], "Table 3")
        
        if df3 is not None:
            # Extract data columns as numpy arrays for SciPy
            x = df3["Angle (deg)"].to_numpy()
            y = df3["Meter Reading (mA)"].to_numpy()
            
            # --- 1. SMOOTHING (From your Notebook) ---
            # Replace this with your exact spline code if different
            x_smooth_1 = np.linspace(x.min(), x.max(), 300)
            spline = make_interp_spline(x, y, k=3)
            y_smooth_1 = spline(x_smooth_1)
            
            # --- 2. PEAK FINDING (From your Screenshot) ---
            peak_indices_1, properties_1 = find_peaks(y_smooth_1, prominence=0.1)
            peak_distances_1 = x_smooth_1[peak_indices_1]
            peak_height_1 = y_smooth_1[peak_indices_1]
            
            # --- 3. PHYSICS CALCULATIONS ---
            # Ensure we found at least 2 peaks before doing math to avoid index errors
            if len(peak_distances_1) >= 2:
                # Math fix applied from previous discussion
                d1 = (1 * avg_lambda) / (2 * np.sin(np.radians(peak_distances_1[0])))
                d2 = (2 * avg_lambda) / (2 * np.sin(np.radians(peak_distances_1[1])))
                final_d = (d1 + d2) / 2
                
                # --- 4. DISPLAY RESULTS ---
                st.subheader("Bragg Diffraction Results")
                st.write(f"First Maxima ($n=1$) at {peak_distances_1[0]:.2f}° -> $d_1$ = {d1:.3f} cm")
                st.write(f"Second Maxima ($n=2$) at {peak_distances_1[1]:.2f}° -> $d_2$ = {d2:.3f} cm")
                st.success(f"**Calculated Interplanar Spacing ($d$): {final_d:.3f} cm**")
                
                # --- 5. VISUALIZER ---
                st.subheader("Intensity vs Angle")
                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(figsize=(8, 5))
                
                ax.plot(x, y, 'o', color='#2E86AB', label='Raw Data')
                ax.plot(x_smooth_1, y_smooth_1, '-', color='#2E86AB', alpha=0.7, label='Smoothed Curve')
                ax.plot(peak_distances_1, peak_height_1, "x", color='red', markersize=8, label='Detected Peaks')
                
                ax.set_title('Intensity as a function of angle', fontsize=14, pad=15)
                ax.set_xlabel('Angle (degrees)', fontsize=12)
                ax.set_ylabel('Intensity (mA)', fontsize=12)
                ax.legend()
                
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                st.pyplot(fig)
            else:
                st.error("Could not detect two distinct peaks. Adjust your prominence value or check your data.")
                
    else:
        st.info("🔒 Please complete data entry for both Table 1 and Table 2 to unlock this section.")