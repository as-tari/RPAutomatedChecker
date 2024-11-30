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

# Main application logic
def main():
    # Check if user is authenticated
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
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
        st.set_page_config(page_title="RP Automated Checker", layout="wide")
        
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Select Page", ["Home", "Upload & Report", "Operating Instructions", "How It Works"])

        if page == "Home":
            st.title("📑 RP Automated Checker")
            st.markdown("""
                RP Automated Checker is a web-based automation app designed to streamline and accelerate the document verification process for Rancangan Penelitian (RP) final submissions. It provides efficient, error-free document checks in bulk, minimizing the need for manual reviews.
            """)

        elif page == "Upload & Report":
            st.title("Upload Data dan Dokumen")

            # Define expected filename formats as constants
            PROPOSAL_DOSEN_PEMBIMBING_FORMAT = "Kode Mahasiswa_KodeDosenPembimbing_DosenPembimbing.docx"
            PROPOSAL_DOSEN_REVIEWER_FORMAT = "KodeMahasiswa_KodeDosenReviewer_DosenReviewer.docx"
            LOGBOOK_FORMAT = "KodeMahasiswa_NamaLengkapMahasiswa_LembarPemantauanBimbingan.pdf"
            RENCANA_KERJA_FORMAT = "KodeMahasiswa_NamaLengkapMahasiswa_RencanaKerjaPenulisanSkripsi.pdf"

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

            BASE_UPLOAD_DIR = "uploads"
            os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

            uploaded_excel = st.file_uploader("Upload Data Mahasiswa (Excel)", type=["xlsx"])
            students_data = {}

            if uploaded_excel:
                if not check_file_size(uploaded_excel):
                    st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
                else:
                    try:
                        df = pd.read_excel(uploaded_excel)
                        required_columns = ['KodeMahasiswa ', 'NamaMahasiswa', 'KodeDosenPembimbing', 'KodeDosenReviewer']
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

            uploaded_zip = st.file_uploader("Upload Bundle Dokumen (ZIP)", type=["zip"])

            if uploaded_zip:
                if not check_file_size(uploaded_zip):
                    st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {MAX_UPLOAD_SIZE_MB} MB.")
                else:
                    zip_path = os.path.join(BASE_UPLOAD_DIR, uploaded_zip.name)
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_zip.getbuffer())
                    
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(BASE_UPLOAD_DIR)
                        st.success("Bundle dokumen berhasil diekstrak!")
                    except zipfile.BadZipFile:
                        st.error("File ZIP yang diupload tidak valid.")

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

        elif page == "Operating Instructions":
            operating_instructions()

        elif page == "How It Works":
            how_it_works()

def operating_instructions():
    st.title("Operating Instructions (Instruksi Pengoperasian)")
    
    st.subheader("1. Upload Student Data (Unggah Data Mahasiswa)")
    st.write("• Click on the “Upload Data” section on the homepage. (Klik pada bagian “Upload Data” di halaman utama.)")
    st.write("• Select the Excel file containing student data with columns like ‘StudentID’, ‘StudentName’, ‘SupervisorCode’, and ‘ReviewerCode’. (Pilih file Excel yang berisi data mahasiswa dengan kolom yang sesuai seperti ‘KodeMahasiswa’, ‘NamaMahasiswa’, ‘KodeDosenPembimbing’, dan ‘KodeDosenReviewer’.)")
    st.write("• Once uploaded, the app will verify if the file matches the expected format. (Setelah diunggah, aplikasi akan memverifikasi apakah file tersebut sesuai dengan format yang diharapkan.)")
    
    st.subheader("2. Upload Document Bundle (Unggah Bundle Dokumen)")
    st.write("• After uploading the student data, proceed to upload the document bundle in ZIP format. (Setelah mengunggah data mahasiswa, lanjutkan dengan mengunggah bundle dokumen dalam format ZIP.)")
    st.write("• The ZIP file must contain the student documents organized in the correct folder structure. (ZIP file harus berisi dokumen mahasiswa yang sudah diorganisasi dengan struktur folder yang benar.)")
    
    st.subheader("3. Check Document Completeness (Cek Kelengkapan Berkas Mahasiswa)")
    st.write("• Click the “Check Document Completeness” button once both files are uploaded. (Klik tombol “Cek Kelengkapan Berkas Mahasiswa” setelah kedua file diunggah.)")
    st.write("• The app will process the uploaded documents, checking for completeness and format compliance. (Aplikasi akan memproses dokumen yang diunggah dan memeriksa kelengkapan serta kesesuaian format.)")
    st.write("• If any documents are missing or incorrectly formatted, the app will provide a clear report. (Jika ada dokumen yang hilang atau formatnya salah, aplikasi akan memberikan laporan yang jelas.)")
    
    st.subheader("4. Download Report (Unduh Laporan)")
    st.write("• After the verification process is complete, the document status report will be displayed. (Setelah pengecekan selesai, laporan status pengumpulan dokumen akan ditampilkan.)")
    st.write("• You can download the report in Excel format by clicking the “Download Report as Excel” button. (Anda dapat mengunduh laporan tersebut dalam format Excel dengan mengklik tombol “Unduh Laporan sebagai Excel.”)")

def how_it_works():
    st.title("How It Works (Cara Kerja Aplikasi)")
    
    st.subheader("1. Input Validation (Validasi Input)")
    st.write("• Before starting the verification, the app checks the uploaded files to ensure they match the expected format. (Sebelum memulai verifikasi, aplikasi memeriksa file yang diunggah agar sesuai dengan format yang diharapkan.)")
    st.write("• If the Excel file is missing required columns or the ZIP format is incorrect, the app will provide a warning. (Jika file Excel tidak memiliki kolom yang tepat atau format ZIP tidak sesuai, aplikasi akan memberikan peringatan.)")
    
    st.subheader("2. Upload Data and Documents (Unggah Data dan Dokumen)")
    st.write("• The user uploads two files: the Excel file containing student data and the ZIP file containing student documents. (Pengguna mengunggah dua file: file Excel yang berisi data mahasiswa dan file ZIP yang berisi dokumen mahasiswa.)")
    st.write("• Once uploaded, the app verifies the received data and documents. (Setelah diunggah, aplikasi akan memverifikasi data dan dokumen yang diterima.)")
    
    st.subheader("3. Automated Verification (Verifikasi Otomatis)")
    st.write("• The app starts the automated verification process, which includes: (Aplikasi memulai proses verifikasi otomatis, yang mencakup:)")
    st.write("  • Completeness: Ensures all required documents are present. (Kelengkapan: Memastikan semua dokumen yang diperlukan ada.)")
    st.write("  • Format Compliance: Checks if the files have the correct format and naming convention. (Kesesuaian Format: Memeriksa apakah file memiliki format dan penamaan yang benar.)")
    st.write("  • Folder Structure: Ensures files are placed in the correct folders. (Struktur Folder: Memastikan file diunggah dalam folder yang sesuai.)")
    
    st.subheader("4. Batch Processing and Multi-Threading (Proses Batch dan Multi-Threading)")
    st.write("• Verification is done in batches, processing many documents at once. (Verifikasi dilakukan dalam batch, memproses banyak dokumen sekaligus.)")
    st.write("• With multi-threading, the app verifies multiple files simultaneously, speeding up the overall process. (Dengan multi-threading, aplikasi dapat memverifikasi banyak file secara bersamaan, mempercepat keseluruhan proses.)")
    
    st.subheader("5. Error Handling (Penanganan Kesalahan)")
    st.write("• If a file is corrupted or unreadable, the app provides a clear error message and allows the user to re-upload the correct document. (Jika ada file yang rusak atau tidak terbaca, aplikasi memberikan pesan kesalahan yang jelas dan memungkinkan pengguna untuk mengunggah ulang dokumen yang benar.)")
    
    st.subheader("6. Review Results (Tinjau Hasil Verifikasi)")
    st.write("• After the verification process is completed, the app displays the verification status, including missing documents, incorrect formats, or folder structure errors. (Setelah proses verifikasi selesai, aplikasi menampilkan status verifikasi yang mencakup dokumen yang hilang, format yang salah, atau kesalahan dalam struktur folder.)")
    
    st.subheader("7. Generate Reports (Menghasilkan Laporan)")
    st.write("• Users can download the verification results in an Excel report, which includes detailed information about the issues found. (Pengguna dapat mengunduh laporan hasil verifikasi dalam format Excel, yang meny ertakan detail tentang masalah yang ditemukan.)")

if __name__ == "__main__":
    main()
