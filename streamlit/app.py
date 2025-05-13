import streamlit as st
import requests

st.write("This is the todo app")

email = st.text_input("Email")
firstname = st.text_input("First Name")
lastname = st.text_input("Last Name")
username = st.text_input("Username")
password = st.text_input("Password")
data = {
    "firstname": firstname,
    "lastname": lastname,
    "username": username,
    "password": password,
    "email": email,
}
if st.button("Sign up"):
    data = requests.post("https://todoapi-qi3q.onrender.com/user/signup", json=data)
    st.write(data.json())

