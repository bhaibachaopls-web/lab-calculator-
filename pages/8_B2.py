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
st.set_page_config(page_title="Experiment B2", page_icon="📈", layout="centered")
st.title("Experiment B₂")
st.subheader("To study the radioactivity of the artificial isotopes ¹⁰⁸Ag, ¹¹⁰Ag and determination of their half lives.")


# --- MEMORY INITIALIZATION ---
if 'lambda_1' not in st.session_state: st.session_state.lambda_1 = None
if 'df1' not in st.session_state: st.session_state.df1 = None
# _____ Button Memory_____
if 'calc_T1' not in st.session_state: st.session_state.calc_T1 = False 
if 'calc_T2' not in st.session_state: st.session_state.calc_T2 = False 

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
            
            return mapped_df.dropna()
        return None
    else:
        st.write(f"Enter data for {table_id}:")
        time_values = list(range(10, 410, 10))
        initial_df = pd.DataFrame({
            col_names[0]: time_values,
            col_names[1]: [None] * len(time_values) # Creates empty cells for the second column
        })
        df = st.data_editor(initial_df, num_rows="dynamic", key=f"edit_{table_id}", use_container_width=True, on_change=reset_calc, args=(table_id,))
        if not df.empty and not df.isna().all().all():          
                
            return df.dropna()
        return None

# --- MAIN UI ---
st.divider()
st.subheader("Data Input:")
input_method = st.radio("How do you want to input your data?", ["Upload File", "Manual Entry"])

# creating the tables
tab1, tab2 = st.tabs(["Table 1: Table for background count", "Table 2: Table for countrate with source 🔒"])

# ==========================================
# TAB 1: Bg count
# ==========================================
with tab1:
    st.session_state.df1 = get_table_data(input_method,
                                        ["Time", "Counts per 10s"],
                                        "Table 1")
    
    if st.session_state.df1 is not None:
        st.button("Calculate Background Count", type="primary", on_click=trigger_T1, key="btn_t1")
        
        if st.session_state.calc_T1:
            st.subheader('Uploaded Data :')
            st.dataframe(st.session_state.df1, use_container_width = True)
            
            df1_copy = st.session_state.df1.copy()
            df1_copy['Time'] = df1_copy['Time'].astype(float)
            df1_copy['Counts per 10s'] = df1_copy['Counts per 10s'].astype(float)
            df1_copy.sort_values(by= 'Time', inplace= True)
            bg_count = df1_copy['Counts per 10s'].mean().item()
            st.session_state.lambda_1 = bg_count
            st.write(f'#### Average background count : {bg_count}')
# ==========================================
# TAB 2: Counts with source
# ==========================================
with tab2:    
    if st.session_state.lambda_1 is not None :
        st.success("Background Count was calculated. You can now process table 2!.")

        df3 = get_table_data(input_method, ["Time", "Counts per 10s"], "Table 2")
        if df3 is not None:
            st.button("Calculate Counts with source", type="primary", on_click=trigger_T2, key="btn_t2")
        
            if st.session_state.calc_T2:
                st.info(f'Using background count = {bg_count:.2f}')
                # ====Fixing===
                df3['Time'] = df3['Time'].astype(float)
                df3['Counts per 10s'] = df3['Counts per 10s'].astype(float)
                df3.sort_values(by = 'Time', inplace= True)
                # ===Table Creation===
                df_2 = df3.copy()

                st.subheader('Uploaded Data')
                st.dataframe(df_2)
                st.info('The splits for the short lived isotope and the long lived isotope are [0,120], [130, 400/end] because in my experience this gives the best result')
                df_2.rename(columns={'Counts per 10s' : 'counts', 'Time' : 'time'}, inplace= True)
                df_2['corrected_counts'] = (df_2['counts']) - bg_count
                df_2['ln'] = np.log(df_2['corrected_counts'])
                df_long = df_2[df_2['time'] >= 130].copy()
                df_short = df_2[df_2['time']<= 120].copy()

                st.subheader('Completed Table')
                st.dataframe(df_2)
                st.divider()
                st.subheader('Extrapolation table (for short lived isotope)')

                # ====Exterpolating====
                X_long = df_long[['time']]
                y_long = df_long[['ln']]
                linreg_long = LinearRegression()
                linreg_long.fit(X_long, y_long)
                a_long = linreg_long.coef_.item()
                b_long = linreg_long.intercept_.item()


                df_short['pure_short'] = df_short['corrected_counts'] - np.exp((a_long * df_short['time']) + b_long)
                if (df_short['pure_short'] <= 0).any():
                    st.error("Mathematical Error: The extrapolated long-lived counts are greater than or equal to the total corrected counts for some short-lived data points. This creates zero or negative values, making the natural logarithm (ln) calculation impossible. Please verify your data points.")
                    st.stop()
                df_short['ln'] = np.log(df_short['pure_short'])
                df_short = df_short[['time', 'counts', 'corrected_counts', 'pure_short', 'ln']]
                st.dataframe(df_short)

                X_short = df_short[['time']]
                y_short = df_short[['ln']]
                linreg_short = LinearRegression()
                linreg_short.fit(X_short, y_short)
                a_short = linreg_short.coef_.item()
                b_short = linreg_short.intercept_.item()

                # ==== Graph ====
                st.divider()
                st.subheader('Visualization')

                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(figsize=(np.sqrt(200), 10))

                X_full = df_2[['time']]

                slopes = f'''Slope for the long lived isotope : {a_long:.4f}
Slope for the long lived isotope : {a_short:.4f}'''

                ax.plot(df_long['time'], df_long['ln'],marker = 'o', color='black', label='Mixed Data', linestyle = 'None')
                ax.plot(X_short, y_short, color='red', marker='x', label='Pure Short-Lived Data', linestyle = 'None')

                ax.plot(X_full, linreg_long.predict(X_full), color='black', linestyle='--', label='Long-Lived Extrapolation')
                ax.plot(X_short, linreg_short.predict(X_short), color='blue', label='Short-Lived Fit')

                ax.set_xticks(np.arange(0, df_2['time'].max() + 25, 25))
                ax.set_yticks(np.arange(0, df_2['ln'].max() + 1, .5))

                ax.text(0.016, 0.98, slopes, 
                            transform=plt.gca().transAxes,  # Tells Matplotlib to use relative axis coordinates (0 to 1)
                            fontsize=15, 
                            verticalalignment='top', 
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8))

                plt.title('ln(counts) as a function of time', fontsize = 18)
                ax.set_xlabel('Time (s)', fontsize = 15)
                ax.set_ylabel('ln(Counts)',fontsize = 15)
                ax.legend()
                st.pyplot(fig)


                st.divider()
                st.subheader('Result (λ = -ln(2)/slope)')

                s1 = -np.log(2)/a_short
                st.write(f"##### Half life of the short lived isotope ¹¹⁰Ag: {s1} s")

                s = -np.log(2)/a_long
                st.write(f"##### Half life of the long lived isotope ¹⁰⁸Ag: {s} s")

                st.divider()
                st.subheader('Error')

                st.write(f"##### Error for the the short lived isotope ¹¹⁰Ag: {abs(100*((24.6 - s1)/24.6)) :.4f} %")
                st.write(f"##### Error for the the long lived isotope ¹⁰⁸Ag: {abs(100*((142.2 - s)/142.2)) :.4f} %")
    
    else :
        st.info("🔒 Please calculate the Background count in Table 1 to unlock this section.")



