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
    # Define valid usernames and passwords
    valid_credentials = {
        "admin": "tarikeren",
        "timrp": "psl401"
    }
    return valid_credentials.get(username) == password

# Create a login form with some styling
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

# Check if user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Add some styling for the login page
    st.markdown("""
        <style>
        .login-container {
            width: 300px;
            margin: 0 auto;
            padding: 20px;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    login()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Set page config
    st.set_page_config(page_title="RP Streamlit", layout="wide")

    # Title of the application
    st.title("RP Streamlit 📑 Sistem Pengumpulan Dokumen Mahasiswa")

    # Application description
    st.markdown("""
        **Deskripsi Aplikasi:**
        RP Streamlit adalah sistem pengecekan otomatis untuk pengumpulan dokumen mahasiswa. 
        Aplikasi ini memungkinkan dosen dan mahasiswa untuk mengupload dan memverifikasi 
        kelengkapan berkas yang diperlukan untuk proses bimbingan skripsi. 

        **Fitur Utama:**
        - Upload data mahasiswa dalam format Excel.
        - Upload bundle dokumen dalam format ZIP.
        - Sistem otomatis untuk memeriksa kelengkapan dokumen berdasarkan format yang ditentukan.
        - Laporan status pengumpulan dokumen yang dapat diunduh dalam format Excel.

        Aplikasi ini bertujuan untuk mempermudah proses pengumpulan dan verifikasi dokumen 
        sehingga dapat meningkatkan efisiensi dalam pengelolaan administrasi akademik.
    """)

    # Operating instructions
    st.markdown("""
        **Cara Pengoperasian Aplikasi:**
        1. **Upload Data Mahasiswa:**
           - Klik pada bagian "Upload Data" di sidebar.
           - Pilih file Excel yang berisi data mahasiswa dengan kolom 'KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', dan 'KodeDosenReviewer'.
           - Setelah diupload, aplikasi akan memverifikasi apakah file tersebut sesuai dengan format yang diharapkan.

        2. **Upload Bundle Dokumen:**
           - Setelah mengupload data mahasiswa, lanjutkan dengan mengupload bundle dokumen dalam format ZIP.
           - ZIP file harus berisi dokumen yang sesuai dengan format yang ditentukan untuk setiap mahasiswa.

        3. **Cek Kelengkapan Berkas Mahasiswa:**
           - Setelah kedua file diupload, klik tombol "Cek Kelengkapan Berkas Mahasiswa" di sidebar.
           - Aplikasi akan memproses dokumen yang diupload dan memeriksa kelengkapan serta kesesuaian format.
           - Jika ada dokumen yang kurang atau tidak sesuai format, aplikasi akan memberikan laporan yang jelas.

        4. **Unduh Laporan:**
           - Setelah proses pengecekan selesai, laporan status pengumpulan dokumen akan ditampilkan.
           - Anda dapat mengunduh laporan tersebut dalam format Excel dengan mengklik tombol "Unduh Laporan sebagai Excel".
    """)

    # Define expected filename formats as constants
    PROPOSAL_DOSEN_PEMBIMBING_FORMAT = "Kode Mahasiswa_KodeDosenPembimbing_DosenPembimbing.docx"
    PROPOSAL_DOSEN_REVIEWER_FORMAT = "KodeMahasiswa_KodeDosenReviewer_DosenReviewer.docx"
    LOGBOOK_FORMAT = "KodeMahasiswa_NamaLengkapMahasiswa_LembarPemantauanBimbingan.pdf"
    RENCANA_KERJA_FORMAT = "KodeMahasiswa_NamaLengkapMahasiswa_RencanaKerjaPenulisanSkripsi.pdf"

    # Function to validate filename
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

    # Directory where documents are stored
    BASE_UPLOAD_DIR = "uploads"
    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)  # Create directory if it doesn't exist

    # Upload student data from Excel
    uploaded_excel = st.file_uploader("Upload Data Mahasiswa (Excel)", type=["xlsx"])
    students_data = {}

    if uploaded_excel:
        if not check_file_size(uploaded_excel):
            st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
        else:
            try:
                df = pd.read_excel(uploaded_excel)
                # Validate required columns
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

    # Upload zip file containing documents
    uploaded_zip = st.file_uploader("Upload Bundle Dokumen (ZIP)", type=["zip"])

    if uploaded_zip:
        if not check_file_size(uploaded_zip):
            st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
        else:
            zip_path = os.path.join(BASE_UPLOAD_DIR, uploaded_zip.name)
            with open(zip_path, "wb") as f:
                f.write(uploaded_zip.getbuffer())
            
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(BASE_UPLOAD_DIR)

            st.success("Bundle dokumen berhasil diekstrak!")

    # Check completeness of student documents
    if st.button("Cek Kelengkapan Berkas Mahasiswa"):
        report = []  # List to hold report data
        selected_folder_path = BASE_UPLOAD_DIR  # Use the base upload directory since we extracted the ZIP here
        
        for student_code, student_info in students_data.items():
            # Initialize submission status
            submitted_status = {
                "proposal pembimbing": False,
                "proposal reviewer": False,
                "logbook": False,
                "rencana kerja": False
            }
            remarks = []  # List to hold remarks for errors
            
            # Get dosen codes from student data
            dosen_pembimbing_code = student_info['dosen_pembimbing']
            dosen_reviewer_code = student_info['dosen_reviewer']
            
            # Check for each expected document in the selected folder and its subfolders
            for dirpath, dirnames, filenames in os.walk(selected_folder_path):
                for filename in filenames:
                    # Ignore files that start with '._'
                    if filename.startswith('._'):
                        continue
                    
                    if student_code in filename:
                        # Determine expected folder names
                        expected_folder_pembimbing = f"Dosen {dosen_pembimbing_code}"
                        expected_folder_reviewer = f"Dosen {dosen_reviewer_code}"
                        
                        if "Dosen Pembimbing" in filename and expected_folder_pembimbing not in dirpath:
                            remarks.append(f"File '{filename}' diupload di folder yang salah. Seharusnya di folder '{expected_folder_pembimbing}'.")

                        if "Dosen Reviewer" in filename and expected_folder_reviewer not in dirpath:
                            remarks.append(f"File '{filename}' diupload di folder yang salah. Seharusnya di folder '{expected_folder_reviewer}'.")

                        if "Dosen Pembimbing" in filename:
                            if validate_filename(filename, PROPOSAL_DOSEN_PEMBIMBING_FORMAT):
                                submitted_status["proposal pembimbing"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: '{PROPOSAL_DOSEN_PEMBIMBING_FORMAT}'.")
                        elif "Dosen Reviewer" in filename:
                            if validate_filename(filename, PROPOSAL_DOSEN_REVIEWER_FORMAT):
                                submitted_status["proposal reviewer"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: '{PROPOSAL_DOSEN_REVIEWER_FORMAT}'.")
                        elif "Lembar Pemantauan Bimbingan" in filename:
                            if validate_filename(filename, LOGBOOK_FORMAT):
                                submitted_status["logbook"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: '{LOGBOOK_FORMAT}'.")
                        elif "Rencana Kerja Penulisan Skripsi" in filename:
                            if validate_filename(filename, RENCANA_KERJA_FORMAT):
                                submitted_status["rencana kerja"] = True
                            else:
                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: '{RENCANA_KERJA_FORMAT}'.")

            # Check for missing documents
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

        # Convert report to DataFrame
        report_df = pd.DataFrame(report)

        # Display report as a table
        if not report_df.empty:
            st.subheader("Laporan Status Pengumpulan Dokumen:")
            st.dataframe(report_df)

            # Provide option to download the report as an Excel file
            excel_file = "laporan_status_pengumpulan_rp.xlsx"
            report_df.to_excel(excel_file, index=False)
            with open(excel_file, "rb") as f:
                st.download_button("Unduh Laporan sebagai Excel", f, file_name=excel_file)


