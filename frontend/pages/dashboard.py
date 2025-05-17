import streamlit as st

if "token" not in st.session_state:
    st.write("You are not logged in.")
    st.page_link("pages/login.py", label="Log in", icon="🔓")
    st.write("Welcome to Your Dashboard.")