import streamlit as st


st.set_page_config(
    page_title = 'Automated Physics Lab Calculator',
    page_icon = '☢️',
    layout = 'centered'
)


st.title('4th Year Lab Helper')
st.write("Welcome to the automated lab calculator. This tool is designed to standardize our lab reporting, handle raw data ingestion, and automate standard visualizations.")

st.subheader("How to Use This Tool")
st.write("Watch this quick tutorial to see how to format your raw data and use the web app.")
tutorial = 'https://youtu.be/mEV2L9B9TLM'
st.video(tutorial)
st.success('##### This web app works on pc/laptop as well as phones!')
st.divider()




st.subheader("📥 Download Lab Templates")
st.write("Grab the pre-formatted Excel templates to format your raw data before uploading:")

col1, col2 = st.columns(2)
with col1:
    st.link_button("Lab tutorials (From 98)", "https://drive.google.com/file/d/1p7AZajVGHYxQcwbADA-UGJMoyOV2pV3V/view?usp=drive_link", type="secondary", use_container_width=True)
with col2:
    st.link_button("Sample data", "https://drive.google.com/drive/folders/1S52F8qhHTXApbKmsjmqlUgzlPRUchSkA?usp=sharing", type="secondary", use_container_width=True)

st.divider()

st.info('#### This is NOT a Origin/drawing by hand substitute. Please do not use it like that😀')
st.caption("ONLY FOR 4TH YEAR LAB| Automated Lab Calculation Project")
st.caption('Deepro Diganto')