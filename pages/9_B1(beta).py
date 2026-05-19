import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.optimize import curve_fit


# ======== Button Setup ========
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
st.set_page_config(page_title="Experiment B1", page_icon="📈", layout="centered")
st.title("Experiment B₁")
st.subheader("To draw the plateau curve for a Geiger-Muller counter and to determine the range of β-particles by eye estimation from graph.")

# --- MEMORY INITIALIZATION ---
if 'operating_voltage' not in st.session_state: st.session_state.operating_voltage = None
if 'bg_count' not in st.session_state: st.session_state.bg_count = None
if 'bg_c' not in st.session_state: st.session_state.bg_c = None
if 'bg_uc' not in st.session_state: st.session_state.bg_uc = None
if 'df1' not in st.session_state: st.session_state.df1 = None
if 'df2' not in st.session_state: st.session_state.df2 = None
# _____ Button Memory_____
if 'calc_T1' not in st.session_state: st.session_state.calc_T1 = False 
if 'calc_T2' not in st.session_state: st.session_state.calc_T2 = False 
if 'calc_T3' not in st.session_state: st.session_state.calc_T3 = False

# --- INPUT HELPER FUNCTION ---
# --- INPUT HELPER FUNCTION ---
def get_table_data(method, col_names, table_id, predefined_col1=None):
    if method == "Upload File":
        file = st.file_uploader(f"Upload CSV/Excel for {table_id}", type=["csv", "xlsx"], key=f"up_{table_id}", on_change=reset_calc, args=(table_id,))
        if file is not None:
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            st.write(f"Map columns for {table_id}:")
            
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

# creating the tables
tab1, tab2, tab3 = st.tabs(["Table 1: Operating Voltage", "Table 2: Background Curve 🔒", "Table 3: ß-Decay 🔒"])

# ==========================================
# TAB 1: Operating Voltage
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(input_method,
                                        ["avg_voltage", "count_1", 'count_2', 'count_3'],
                                        "Table 1")
    
    if st.session_state.df1 is not None:
        st.button("Calculate to find the operating voltage", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data :')
            st.dataframe(st.session_state.df1, use_container_width = True)
            
            df1_copy = st.session_state.df1.copy()
            
            cols = df1_copy.columns
            for col in cols :
                df1_copy[col] = df1_copy[col].astype(float)
            
            counts = ['count_1', 'count_2', 'count_3']
            cpm = df1_copy[counts].mean(axis=1)/2
            uc = np.sqrt(cpm/2)
            df1_copy['Mean Counts/min'] = cpm.round().astype(int).astype(str) + ' ± ' + uc.round(2).astype(str)

            st.divider()
            st.subheader('Completed Table')
            st.dataframe(df1_copy)

            # ====== Graph Calculation =======

            y_vals = cpm
            x_vals = df1_copy['avg_voltage']

            valid = y_vals > 0
            x_fit = x_vals[valid]
            y_fit = y_vals[valid]

            def exp_fit(x, y0, A, R0):
                return y0 + A * np.exp(R0 * x)

            guess_y0 = np.max(y_fit)
            guess_R0 = -0.05
            x_first = x_fit.iloc[0]
            y_first = y_fit.iloc[0]
            guess_A = (y_first - guess_y0) / np.exp(guess_R0 * x_first)
            p0_dynamic = [guess_y0, guess_A, guess_R0]
            popt, _ = curve_fit(exp_fit, x_fit, y_fit, p0=p0_dynamic, maxfev=10000)

            x_smooth = np.linspace(x_fit.min(), x_fit.max(), 100)
            y_smooth = exp_fit(x_smooth, *popt)

            dy_dx = np.gradient(y_smooth, x_smooth)
            flat_region = np.where(dy_dx < 1.5)[0]
            plateau_start = x_smooth[flat_region[0]]
            plateau_end = np.max(x_fit)
            op_v_exact = (plateau_start + plateau_end) / 2
            operating_voltage = round(op_v_exact / 25) * 25

            # ====== Visualization =======
            st.divider()
            st.subheader('Graph for finding the operating voltage')

            fig1, ax1 = plt.subplots(figsize = (11,8))
            # fig, ax = plt.subplots(figsize = (10,6))
            ax1.plot(x_fit, y_fit, color='black', label='Data points', marker = 'o', linestyle = 'None')
            ax1.plot(x_smooth, y_smooth, 'k-', linewidth=1, label='Exponential Fit')
            ax1.axvline(x=operating_voltage, color='black', linestyle='--', 
                        label=f'Operating Voltage ({int(operating_voltage)}V)')
            ax1.set_title('Mean Counts per min as a function of applied voltage', fontsize = 18)
            ax1.set_xlabel('Voltage', fontsize = 13)
            ax1.set_ylabel('Counts per minute', fontsize = 13)
            ax1.legend()
            st.pyplot(fig1)

            st.session_state.operating_voltage = operating_voltage
            st.success(f'Operating voltage is : {st.session_state.operating_voltage}')
            st.session_state.df1 = df1_copy.copy()

# ==========================================
# TAB 2: Background Count
# ==========================================

with tab2 :
    if st.session_state.operating_voltage is not None:
        st.success("Operating voltage has been calculated! You can now process Table 2.")
        st.info(f"Using V = **{st.session_state.operating_voltage:.4f} Ω**")

        st.session_state.df2 = get_table_data(
            method=input_method, 
            col_names=["thickness", "count_1", "count_2", 'count_3'], 
            table_id="Table 2",
            predefined_col1 = [st.session_state.operating_voltage]
        )
        
        if st.session_state.df2 is not None:
            st.button("Calculate The background count", type="primary", on_click=trigger_T2, key="btn_t2")
        
            if st.session_state.calc_T2:
                df2_copy = st.session_state.df2.copy()
                st.subheader('Uploaded data')
                st.dataframe(df2_copy)
                st.divider()

                for col in df2_copy.columns:
                    df2_copy[col] = df2_copy[col].astype(float)


                counts = ['count_1', 'count_2', 'count_3']
                mean = (df2_copy[counts]/2).mean(axis = 1)
                uc = np.sqrt(mean/(len(counts)*2))
                df2_copy['mean_counts/min'] = mean.round().astype(int).astype(str) + ' ± ' + uc.round(2).astype(str)
                bg_c = mean.iloc[0]
                bg_uc = uc.iloc[0]

                st.session_state.bg_c = bg_c
                st.session_state.bg_uc = bg_uc           
                st.subheader('Completed table')                
                st.dataframe(df2_copy)
    else:
        st.info("🔒 Please calculate the operating voltage in Table 1 to unlock this section.")

# ==========================================
# TAB 3: Counts
# ==========================================

with tab3 :
    if st.session_state.operating_voltage is not None and st.session_state.bg_c is not None and st.session_state.bg_uc is not None:
        st.success("Background count has been calculated! You can now process Table 3.")
        # st.info(f"Using V = **{st.session_state.operating_voltage:.4f} Ω**")

        st.session_state.df3 = get_table_data(
            method=input_method, 
            col_names=["thickness", "count_1", "count_2", 'count_3'], 
            table_id="Table 3"
        )
        
        if st.session_state.df3 is not None:
            st.button("Calculate the count rates", type="primary", on_click=trigger_T3, key="btn_t3")
        
            if st.session_state.calc_T3:
                df3_copy = st.session_state.df3.copy()
                st.subheader('Uploaded data')
                st.dataframe(df3_copy)
                st.divider()

                for col in df3_copy.columns:
                    df3_copy[col] = df3_copy[col].astype(float)

                counts = ['count_1', 'count_2', 'count_3']
                mean = (df3_copy[counts]).mean(axis = 1)/2
                corrected = mean - st.session_state.bg_c
                raw_uc = np.sqrt((mean / 6) + st.session_state.bg_uc**2)

                df3_copy['mean_counts/min'] = corrected.round().astype(int).astype(str) + ' ± ' + raw_uc.round(2).astype(str)
                st.subheader('Completed Table')
                st.dataframe(df3_copy)
                st.divider()


                x_data = df3_copy['thickness'].astype(float).values
                y_data = corrected.clip(lower=0).values 

                def decay_fit(x, y0, A1, t1):
                    return A1 * np.exp(-x / t1) + y0

                guess_y0 = np.min(y_data)
                guess_A1 = np.max(y_data) - guess_y0

                target_y = np.max(y_data) / np.e
                idx = np.argmin(np.abs(y_data - target_y))
                guess_t1 = x_data[idx] 
                if guess_t1 == 0: guess_t1 = 200 

                p0_dynamic = [guess_y0, guess_A1, guess_t1]

                bounds_positive = ([0, 0, 0], [np.inf, np.inf, np.inf])

                popt, _ = curve_fit(decay_fit, x_data, y_data, p0=p0_dynamic, bounds=bounds_positive, maxfev=10000)
                y0_fit, A1_fit, t1_fit = popt

                x_smooth = np.linspace(0, np.max(x_data) * 1.1, 200)
                y_smooth = decay_fit(x_smooth, *popt)


                slope_tangent = -A1_fit / t1_fit
                intercept_tangent = A1_fit + y0_fit

                range_R = t1_fit 
                intersection_y = y0_fit

                # --- 6. PLOTTING ---
                
                st.subheader('Graph')
                fig,ax = plt.subplots(figsize=(11, 8))

                ax.plot(x_data, y_data, 'ko', label='Corrected counts')
                ax.plot(x_smooth, y_smooth, 'k-', linewidth=1.5, label='Exponential Fit')

                x_steep = np.array([0, range_R * 1.2])
                y_steep = slope_tangent * x_steep + intercept_tangent
                ax.plot(x_steep, y_steep, 'k-', linewidth=0.8, alpha=0.7)


                x_tail = np.array([range_R * 0.5, np.max(x_data) * 1.1])
                y_tail = np.full_like(x_tail, y0_fit)
                ax.plot(x_tail, y_tail, 'k-', linewidth=0.8, alpha=0.7)

                ax.plot(range_R, intersection_y, 'k|', markersize=15)
                ax.annotate(f'R = {range_R:.1f} $mg~cm^{{-2}}$', 
                            xy=(range_R, intersection_y), 
                            xytext=(range_R + 50, intersection_y + 200),
                            arrowprops=dict(arrowstyle="->", color='black'), fontsize=12)

                ax.set_xlabel('Thickness ($mg~cm^{-2}$)', fontsize=14)
                ax.set_ylabel('Corrected counts per min', fontsize=14)
                ax.set_title('Decay of $\\beta$-particle emission rate from $^{90}Sr$\nas a function of absorber thickness', fontsize=16)

                ax.set_xlim(-50, 1000)
                ax.set_ylim(-30, np.max(y_data) * 1.1)

                ax.legend()
                st.pyplot(fig)
                st.error('I recommend not using the value of intersection you got in this graph. We use "Eye estimation" in lab and i do not know how to code "eye estimation". If I get ever find a better approach, i will update it')

                
    else:
        st.info("🔒 Please calculate the Table 1 and Table 2 to unlock this section.")

