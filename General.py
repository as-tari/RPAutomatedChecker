import streamlit as st
from PIL import Image
import hashlib

# Custom CSS to add logo at the top of the sidebar
st.markdown("""
    <style>
    .sidebar .logo {
        position: fixed;
        top: 10px;  /* Adjusted this value as needed */
        left: 10px; /* Adjusted this value as needed */
        z-index: 1000; /* Ensured it stays above other elements */
    }
    .sidebar .sidebar-content {
        margin-top: 100px; /* Adjusted this value to create space for the logo */
    }
    </style>
""", unsafe_allow_html=True)

# Display the logo in the sidebar
image = Image.open('logo.png')
st.sidebar.image(image, width=100, use_column_width=100, output_format="PNG", clamp=True)
st.sidebar.subheader("PSL 401 Rancangan Penelitian",divider="gray")

# General page content
st.title("RP Submission Review System (Beta)")
st.write("Welcome, Tim RP!")

# Customizing font style
# Load the CSS file
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if email == "rp.fpuaj@gmail.com" and check_hashes(password, make_hashes("rp.fpuaj@gmail.com")):
            st.session_state["logged_in"] = True
            st.success("Logged in successfully!")
            # Call the function to display the protected content
            show_protected_content()
        else:
            st.warning("Incorrect email or password")

def show_protected_content():
    st.title("Welcome to the Protected Page")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.success("Logged out successfully!")

# Main logic
if st.session_state["logged_in"]:
    show_protected_content()
else:
    login()
