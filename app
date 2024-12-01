import streamlit as st

# Add custom CSS styles for the app
def add_custom_css():
    custom_css = '''
    <style>
        .stApp {
            background-color: #cadbf5;
            color: #ffffff;
        }
        h1, h2, h3 {
            background-color: #5c6bc0;
            color: #000000;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .stButton>button {
            background-color: #578ce4;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #7ea8e8;
        }
        .stCard {
            background-color: #9ab0d0;
            border: 1px solid #7ea8e8;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
    </style>
    '''
    st.markdown(custom_css, unsafe_allow_html=True)

# Call the function at the start of the app
add_custom_css()

import os
import re
import pandas as pd
import streamlit as st
import zipfile

# Define a constant for the maximum upload size (in MB)
MAX_UPLOAD_SIZE_MB = 5000  # 5GB

# Function to check file size
def check_file_size(file):
    return file.size <= MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Define a simple authentication function with multiple usernames and passwords
def authenticate(username, password):
    valid_credentials = {
        "admin": "tarikeren",
        "timrp": "psl401"
    }
    return valid_credentials.get(username) == password

# Create the login form
def login():
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["authenticated"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Validate filename against expected format
def validate_filename(filename, expected_format):
    pattern = expected_format.replace("KodeMahasiswa", r"\w{1,2}\d{5}") \
                             .replace("KodeDosenPembimbing", r"\w") \
                             .replace("DosenPembimbing", r"\w+(\s\w+)*") \
                             .replace("KodeDosenReviewer", r"\w") \
                             .replace("DosenReviewer", r"\w+(\s\w+)*") \
                             .replace("NamaLengkapMahasiswa", r"\w+(\s\w+)*") \
                             .replace("LembarPemantauanBimbingan", r"Lembar Pemantauan Bimbingan") \
                             .replace("RencanaKerjaPenulisanSkripsi", r"Rencana Kerja Penulisan Skripsi")
    return re.match(pattern, filename) is not None

# Main application logic
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        home_page()
        upload_page()
        instructions_page()

def home_page():
    st.title("📑 RP Automated Checker")
    st.markdown("RP Automated Checker is a web-based application designed to streamline the document verification process for Rancangan Penelitian (RP) final submissions.")
    st.markdown("Please proceed to upload your data and documents below.")

def upload_page():
    st.title("Upload Student Data and Documents")
    
    # Upload Data Mahasiswa (Excel)
    uploaded_excel = st.file_uploader("Upload Data Mahasiswa (Excel)", type=["xlsx"])
    students_data = {}

    if uploaded_excel:
        if not check_file_size(uploaded_excel):
            st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
        else:
            try:
                df = pd.read_excel(uploaded_excel)
                required_columns = ['KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', 'KodeDosenReviewer']
                if not all(col in df.columns for col in required_columns):
                    st.error("File Excel harus mengandung kolom 'KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', dan 'KodeDosenReviewer'.")
                else:
                    for index, row in df.iterrows():
                        students_data[row['KodeMahasiswa']] = {
                            "name": row['NamaMahasiswa'],
                            "dosen_pembimbing": row['KodeDosenPembimbing'],
                            "dosen_reviewer": row['KodeDosenReviewer']
                        }
                    st.success("Data mahasiswa berhasil diupload!")
            except Exception as e:
                st.error(f"Error saat membaca file Excel: {e}")

    # Upload Bundle Dokumen (ZIP)
uploaded_zip = st.file_uploader("Upload Bundle Dokumen (ZIP)", type=["zip"])

if uploaded_zip:
    if not check_file_size(uploaded_zip):
        st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
    else:
        BASE_UPLOAD_DIR = "uploads"
        os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)
        zip_path = os.path.join(BASE_UPLOAD_DIR, uploaded_zip.name)
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getbuffer())
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:  # Added the missing colon here
                zip_ref.extractall(BASE_UPLOAD_DIR)
            st.success("Bundle dokumen berhasil diekstrak!")
        except zipfile.BadZipFile:
            st.error("File ZIP yang diupload tidak valid.")

    # Process and validate uploaded data
    if students_data:
        report = []
        selected_folder_path = BASE_UPLOAD_DIR
        
        for student_code, student_info in students_data.items():
            submitted_status = {
                "proposal pembimbing": False,
                "proposal reviewer": False,
                "logbook": False,
                "rencana kerja": False
            }
            remarks = []
            dosen_pembimbing_code = student_info['dosen_pembimbing']
            dosen_reviewer_code = student_info['dosen_reviewer']
            
            for dirpath, dirnames, filenames in os.walk(selected_folder_path):
                for filename in filenames:
                    if filename.startswith('._'):
                        continue
                    
                    if student_code in filename:
                        expected_folder_pembimbing = f"Dosen {dosen_pembimbing_code}"
                        expected_folder_reviewer = f"Dosen {dosen_reviewer_code}"
                        
                        if "Dosen Pembimbing" in filename and expected_folder_pembimbing not in dirpath:
                            remarks.append(f"File '{filename}' diupload di folder yang salah. Seharusnya di folder '{expected_folder_pembimbing}'.")

                        if "Dosen Reviewer" in filename and expected_folder_reviewer not in dirpath:
                            remarks.append(f"File '{filename}' diupload di folder yang salah. Seharusnya di folder '{expected_folder_reviewer}'.")

                        if "Dosen Pembimbing" in filename:
                            if validate_filename(filename, "KodeMahasiswa_KodeDosenPembimbing_DosenPembimbing.docx"):
                                submitted_status["proposal pembimbing"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: 'KodeMahasiswa_KodeDosenPembimbing_DosenPembimbing.docx'.")
                        elif "Dosen Reviewer" in filename:
                            if validate_filename(filename, "KodeMahasiswa_KodeDosenReviewer_DosenReviewer.docx"):
                                submitted_status["proposal reviewer"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: 'KodeMahasiswa_KodeDosenReviewer_DosenReviewer.docx'.")
                        elif "Lembar Pemantauan Bimbingan" in filename:
                            if validate_filename(filename, "KodeMahasiswa_NamaLengkapMahasiswa_LembarPemantauanBimbingan.pdf"):
                                submitted_status["logbook"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: 'KodeMahasiswa_NamaLengkapMahasiswa_LembarPemantauanBimbingan.pdf'.")
                        elif "Rencana Kerja Penulisan Skripsi" in filename:
                            if validate_filename(filename, "KodeMahasiswa_NamaLengkapMahasiswa_RencanaKerjaPenulisanSkripsi.pdf"):
                                submitted_status["rencana kerja"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: 'KodeMahasiswa_NamaLengkapMahasiswa_RencanaKerjaPenulisanSkripsi.pdf'.")

            missing_documents = [doc for doc, submitted in submitted_status.items() if not submitted]
            if missing_documents or remarks:
                report.append({
                    "Nama": student_info['name'],
                    "KodeMahasiswa": student_code,
                    "KodeDosenPembimbing": dosen_pembimbing_code,
                    "KodeDosenReviewer": dosen_reviewer_code,
                    "Status": f"Belum mengumpulkan {', '.join(missing_documents)}" if missing_documents else "Semua dokumen sudah dikumpulkan",
                    "Remarks": "\n".join(remarks) if remarks else "-"
                })
            else:
                report.append({
                    "Nama": student_info['name'],
                    "KodeMahasiswa": student_code,
                    "KodeDosenPembimbing": dosen_pembimbing_code,
                    "KodeDosenReviewer": dosen_reviewer_code,
                    "Status": "Semua dokumen sudah dikumpulkan",
                    "Remarks": "-"
                })

        report_df = pd.DataFrame(report)

        if not report_df.empty:
            st.subheader("Laporan Status Pengumpulan Dokumen:")
            st.dataframe(report_df)

            excel_file = "laporan_status_pengumpulan_rp.xlsx"
            report_df.to_excel(excel_file, index=False)
            with open(excel_file, "rb") as f:
                st.download_button("Unduh Laporan sebagai Excel", f, file_name=excel_file)
        else:
            st.warning("Silakan upload data mahasiswa terlebih dahulu sebelum melihat laporan.")

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

if __name__ == "__main__":
    main()
