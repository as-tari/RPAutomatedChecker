import streamlit as st
from PIL import Image

image = Image.open('logo.png')
st.sidebar.image(image, width=100)
st.sidebar.subheader("PSL 401 Rancangan Penelitian")
st.divider()

st.header("_Streamlit_ is :blue[cool] :sunglasses:")
st.header("This is a header with a divider", divider="gray")
st.header("These headers have rotating dividers", divider=True)
st.header("One", divider=True)
st.header("Two", divider=True)
st.header("Three", divider=True)
st.header("Four", divider=True)

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
