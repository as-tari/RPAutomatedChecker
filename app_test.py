import streamlit as st
from PIL import Image
import hashlib
import os
import re
import pandas as pd
import zipfile
import time

st.set_page_config(
    page_title="Log in | e-RP Assistant System"
)

# Display the logo in the sidebar
try:
    image = Image.open('images/logo.png')
    st.sidebar.image(image, width=100, output_format="PNG", clamp=True)
except Exception as e:
    st.error(f"Error loading logo: {e}")

st.sidebar.subheader("PSL 401 Rancangan Penelitian")
st.title("📑 e-RP Assistant System (Beta)")

# Set the maximum upload size for Streamlit
STREAMLIT_SERVER_MAX_UPLOAD_SIZE_MB = 1000 

def check_file_size(uploaded_file):
    if uploaded_file is not None:
        # Check the size of the uploaded file
        return uploaded_file.size <= (STREAMLIT_SERVER_MAX_UPLOAD_SIZE_MB * 1024 * 1024)  # Convert MB to bytes
    return False

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Create a dialog for login requirement
@st.dialog("Log in required")
def dialog(item):
    st.warning(":warning: Login is required to access the system. Click the button if you wish to proceed.")
    if st.button("Proceed to log in"):
        # Add your login logic here
        st.success("Redirecting to login...")

if "dialog" not in st.session_state:
    st.write("Vote for your favorite")
    if st.button("A"):
        vote("A")
    if st.button("B"):
        vote("B")
else:
    f"You voted for {st.session_state.vote['item']} because {st.session_state.vote['reason']}"
        
# Initialize session state for logged in status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Login function
def login():
    if st.session_state["logged_in"]:
        return  # Prevent re-rendering login UI if already logged in

    email = st.sidebar.text_input("Email :red[*]", key="login_email")
    password = st.sidebar.text_input("Password :red[*]", type='password', key="login_password")
    st.warning(":warning: Login is required to access the system. If you are unable to proceed, please refresh the page and try logging in again.")

    if st.sidebar.button("Login"):
        if email == "rp.fpuaj@gmail.com" and check_hashes(password, make_hashes("rp.fpuaj@gmail.com")):
            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            show_protected_content()
        else:
            st.sidebar.warning("Incorrect email or password")

        # Check if both email and password are empty
        if not email.strip() and not password.strip():
            st.warning("Both email and password are required to log in.")
        elif not email.strip():
            st.warning("Email is required.")
        elif not password.strip():
            st.warning("Password is required.")

def show_protected_content():
    st.markdown("**Selamat datang di sistem e-RP!** Aplikasi ini dirancang untuk mempermudah pengecekan kelengkapan dokumen proposal mahasiswa.")
    if st.sidebar.button("Logout"):  # Logout button
        st.session_state["logged_in"] = False
        st.success("Logged out successfully!")
    else:
        tab1, tab2 = st.tabs(["Cek Kelengkapan", "Fitur Lainnya"])
        with tab1:
            st.write("Langkah 1")
            st.caption("Silakan unduh file ZIP dari folder 'Pengumpulan Proposal Skripsi' terlebih dahulu. Pastikan komputer atau perangkat Anda memiliki ruang penyimpanan yang memadai.")
            st.link_button("Klik tombol ini untuk mengunduh ZIP File dari Teams :red[*]", "https://studentatmajayaac.sharepoint.com/:f:/r/sites/PSL401RPGanjil2425/Shared%20Documents/Pengumpulan%20Proposal%20Skripsi?csf=1&web=1&e=oiF5Qt")
            st.caption("Setelah tautan dibuka, Anda akan diarahkan ke folder OneDrive Atma Jaya: PSL 401 RP Ganjil 24/25 > Documents > Pengumpulan Proposal Skripsi. Di bagian atas halaman, terdapat toolbar dengan tombol **Download**. Klik tombol **Download** untuk menyimpan file tersebut, yang akan otomatis terunduh dalam format ZIP.")
            st.divider()
            st.write("Langkah 2")
            
            # Unggah Data Mahasiswa RP (Excel)
            uploaded_excel = st.file_uploader("Unggah Data Mahasiswa RP :red[*]", type=["xlsx"])
            st.caption("Unggah file dengan format Excel (.xlsx). :warning: File Excel harus memiliki kolom 'KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', dan 'KodeDosenReviewer'.")
            students_data = {}
    
            if uploaded_excel:
                if not check_file_size(uploaded_excel):
                    st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {STREAMLIT_SERVER_MAX_UPLOAD_SIZE_MB} MB.")
                else:
                    try:
                        start_time = time.time()
                        df = pd.read_excel(uploaded_excel)
                        end_time = time.time()
                        st.write(f"Waktu untuk membaca file Excel: {end_time - start_time} detik")
                        from time import sleep                
    
                        required_columns = ['KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', 'KodeDosenReviewer']
                        if not all(col in df.columns for col in required_columns):
                            st.error("File Excel harus memiliki kolom 'KodeMahasiswa', 'NamaMahasiswa', 'KodeDosenPembimbing', dan 'KodeDosenReviewer'.")
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
            st.divider()
            st.write("Langkah 3")
            
            # Upload Folder Pengumpulan Proposal Skripsi (ZIP)
            uploaded_zip = st.file_uploader("Upload Files > Pengumpulan Proposal Skripsi (ZIP) :red[*]", type=["zip"])
            st.divider()
            st.warning(":warning: Laporan akan dihasilkan secara otomatis. Pastikan file yang Anda unggah sudah benar dan sesuai format yang diminta.")
            if uploaded_zip:
                if not check_file_size(uploaded_zip):
                    st.error(f"Ukuran file terlalu besar! Maksimal ukuran file adalah {STREAMLIT_SERVER_MAX_UPLOAD_SIZE_MB} MB.")
                else:
                    BASE_UPLOAD_DIR = "uploads"
                    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)
                    zip_path = os.path.join(BASE_UPLOAD_DIR, uploaded_zip.name)
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_zip.getbuffer())
                    with st.spinner("Uploading..."):
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(BASE_UPLOAD_DIR)
                        st.success("File ZIP berhasil diekstrak!")
    
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
                                                remarks.append(f"Nama file '{filename}' tidak sesuai format. Seharusnya mengikuti format: 'KodeMahasiswa_NamaLengkapMahasiswa_Lembar PemantauanBimbingan.pdf'.")
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
                            st.subheader("Laporan Hasil Cek Pengumpulan Proposal Skripsi:")
                            st.dataframe(report_df)
    
                            excel_file = "Laporan_Hasil_Cek_Pengumpulan_Proposal_Skripsi.xlsx"
                            report_df.to_excel(excel_file, index=False)
                            with open(excel_file, "rb") as f:
                                st.download_button("Unduh Laporan (.xlsx)", f, file_name=excel_file)
                        else:
                            st.warning("Pembuatan laporan gagal. Silakan mengunggah dokumen kembali.")
    
            @st.cache_data
            def uploaded_excel(x):
                return x**2
            
            @st.cache_data
            def uploaded_zip(x):
                return x**3
            
            if st.button("Clear All"):
                # Clear values from *all* all in-memory and on-disk data caches:
                # i.e. clear values from both square and cube
                st.cache_data.clear()
    
        
        with tab2:
            st.info("More features coming soon")
        
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

def main():
    if not st.session_state["logged_in"]:
        login()  # Call the login function if not logged in
    else:
        show_protected_content()

if __name__ == "__main__":
    main()
