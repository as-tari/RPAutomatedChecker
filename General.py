import streamlit as st
from PIL import Image
import hashlib

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
        else:
            st.warning("Incorrect email or password")

def register():
    st.subheader("Register")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    
    if st.button("Signup"):
        st.success("User  registered successfully!")

if st.session_state["logged_in"]:
    st.title("Welcome to the Protected Page")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.success("Logged out successfully!")
else:
    login()

image = Image.open('logo.png')
st.sidebar.image(image, width=100)
st.sidebar.subheader("PSL 401 Rancangan Penelitian")

st.header("RP _Submission Review System_ (Beta)")
st.subheader("RP Submission Review System (Beta)", divider="gray")
st.write("This is a RP Submission Review System (Beta)
