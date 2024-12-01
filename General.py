import streamlit as st
import hashlib

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

st.header("RP Submission Review System")
