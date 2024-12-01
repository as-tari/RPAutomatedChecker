import streamlit as st
from PIL import Image

# Customizing font style
# Load the CSS file
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

image = Image.open('logo.png')
st.sidebar.image(image, width=100)
st.sidebar.subheader("PSL 401 Rancangan Penelitian")

st.header("_Streamlit_ is :blue[cool] :sunglasses:")
st.subheader("This is a header with a divider", divider="gray")
st.subheader("These headers have rotating dividers", divider=True)
st.write("One", divider=True)
st.write("Two", divider=True)
st.write("Three", divider=True)
st.write("Four", divider=True)

def instructions_page():
    st.title("Operating Instructions")
    st.subheader("1. Upload Student Data (Unggah Data Mahasiswa)")
    st.write("• Click on the “Upload Data” section on the homepage.")
    st.write("• Select the Excel file containing student data.")
    
    st.subheader("2. Upload Document Bundle (Unggah Bundle Dokumen)")
    st.write("• After uploading the student data, upload the document bundle in ZIP format.")
    
    st.subheader("3. Check Document Completeness (Cek Kelengkapan Berkas Mahasiswa)")
    st.write("• Click the “Check Document Completeness” button after both files are uploaded.")
    
    st.subheader("4. Download Report (Unduh Laporan)")
    st.write("• After the verification process is complete, the document status report will be displayed.")
