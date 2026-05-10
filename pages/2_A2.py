import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks



def reset_calc():
    st.session_state.calc_exp2 = False
def trigger_math():
    st.session_state.calc_exp2 = True


st.set_page_config(page_title="Experiment A2", page_icon="📈", layout="centered")
st.title("A₂")
st.subheader("To determine the velocity of sound under room conditions using two transducers and compare it with the theoretically calculated value.")


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
        col1, col2 = st.columns(2)
        c1 = col1.selectbox("Distance", uploaded_cols)
        c2 = col2.selectbox("Pulse height", uploaded_cols)

        df_raw = pd.DataFrame({
            "distance": df_raw[c1],
            "pulse_height": df_raw[c2]
        })
else: 
    st.write("Type your data directly into the table below. Click the bottom row to add more.")
    distance_values = list(range(0,51))
    empty_pulse_values = [None] * 51
    prefilled_template = pd.DataFrame({
        "distance": distance_values,
        "pulse_height": empty_pulse_values
    })
    df_raw = st.data_editor(prefilled_template, num_rows="dynamic", use_container_width=True, on_change=reset_calc)

if not df_raw.empty:
    df_clean = df_raw.dropna(subset=['distance', 'pulse_height'])
else:
    df_clean = pd.DataFrame()
if 'calc_exp2' not in st.session_state:
    st.session_state.calc_exp2 = False
if not df_clean.empty:
    st.button("Start Calculation", type="primary", on_click = trigger_math)
    

    if st.session_state.calc_exp2 :
        if len(df_clean) < 3:
            st.info("💡 Please enter at least 3 rows of data to calculate the spline curve.")
        else:    
            st.divider()
            st.subheader("Completed Data Table")
            st.dataframe(df_raw, use_container_width=True)
            # st.divider()
            # st.subheader("Completed Data table")
            df = df_clean.copy()
            # df['h2'] = df['total'] - df['h1']
            # df['z'] = (df['h2'] / df['h1']) * 1000
            # st.dataframe(df, use_container_width=True)

            #math for graph smoothening
            df['distance'] = df['distance'].astype(float)
            df['pulse_height'] = df['pulse_height'].astype(float)
            df = df.sort_values(by='distance')
            x = df['distance'].to_numpy()
            y = df['pulse_height'].to_numpy()
            x_smooth = np.linspace(x.min(), x.max(), 500)
            spline = make_interp_spline(x,y,2)
            y_smooth = spline(x_smooth)

            peak_indices, properties = find_peaks(y_smooth, prominence=0.1)
            peak_distances = x_smooth[peak_indices]
            peak_height = y_smooth[peak_indices]
            if len(peak_distances) < 3:
                st.error(f"Not enough peaks found in the data! The mathematical model for this experiment requires at least 5 wave peaks. Found: {len(peak_distances)}")
                st.info("Make sure you are entering actual oscillating experimental data, not linear test data.")
            else:
                st.subheader("Visualizer")
                # plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots()
                ax.plot(x_smooth, y_smooth,
                    color = 'blue',
                    linewidth = .59,)
                ax.plot(df['distance'], df['pulse_height'],
                    color = 'black',
                    marker= 'o',
                    markersize = 4,
                    linestyle = 'None')
                # plt.plot(df['distance'], df['pulse_height'])

                ax.set_title("Pulse height as a function of transducers' distances")
                ax.set_xlabel('Distance (mm)')
                ax.set_ylabel('Pulse height(Volt)')
                ax.set_xlim(left= 0)
                ax.set_xticks(np.arange(0,max(x) + 5, step= 5))
                ax.set_yticks(np.arange(1,max(y) + .55,.5))

                ax.annotate(
                text = 'n = 0',
                xy = (peak_distances[0], peak_height[0]),
                xytext=(peak_distances[0], peak_height[0] + 0.09)
                )

                for i in range (3) :
                    ax.annotate(
                    text = f'n = {i + 2}',
                    xy = (peak_distances[i + 2], peak_height[i + 2]),
                    xytext=(peak_distances[i + 2], peak_height[i + 2] + 0.09)
                )
                ax.grid(False)

                st.pyplot(fig)


                st.subheader("Results")

                L = []
                for i in range (3) :
                    L.append(peak_distances[2 + i].item() - peak_distances[0].item())

                j = 1
                st.write('##### From the graph [ L = n(high) - n(0) ]')
                for i in L :
                    st.write(f'L{j} : {i} mm')
                    j += 1

                st.write('##### λ = 2L/n')

                lmd = []
                j = 0
                for i in L :
                    lmd.append((2 * i) / (2 + j))
                    j += 1
                j = 1
                for i in lmd :
                    st.write(f'λ{j} : {i} mm')
                    j += 1

                st.write('##### Velocity (frequency is 40Khz)')
                Wvl = []
                for i in lmd :
                    Wvl.append(i * 10**-3 * 40*10**3)
                
                j = 1
                for i in Wvl :
                    st.write(f'v{j} : {i} ms⁻¹')
                    j += 1

                mean_v = sum(Wvl)/len(Wvl)
                st.write(f'##### Mean velocity : {mean_v} ms⁻¹')

                st.write(f'Theoritical value of velocity: 348.204ms⁻¹ (assuming T = 300K)')
                error = abs((348.204 - mean_v)/348.204) * 100
                st.write(f'##### Error in your data: {error}%')
