import streamlit as st
import requests

st.header("TODO APP")
st.subheader("You can log in or sign up here.")

sign_up, login = st.columns(2)


def signup():
    with sign_up:
        email = st.text_input("Email", value="email@example.com")
        firstname = st.text_input("First Name", value="John")
        lastname = st.text_input("Last Name", value="Doe")
        username = st.text_input("Username", value="JohnDoe23")
        password = st.text_input("Password", key="signup", type="password")

        if st.button("Sign up"):
            payload = {
                "firstname": firstname,
                "lastname": lastname,
                "username": username,
                "password": password,
                "email": email,
            }
            empty = False
            for key, value in payload.items():
                if value == "":
                    empty = True
                    st.warning(f"Please enter your {key}")
            if empty:
                log_in()
                st.stop()
            data = requests.post("https://todoapi-qi3q.onrender.com/user/signup", json=payload)
            if data.status_code != 201:
                if data.status_code == 422:
                    message = data.json()["detail"][0]["msg"]
                    st.error(data.json())
                elif data.status_code == 226:
                    st.error(data.json()["detail"])
                else:
                    st.error("something went wrong")
            else:
                st.success("Signed up successfully log in here")


def log_in():
    with login:
        username = st.text_input("Username")
        password = st.text_input("Password", key="login", type="password")

        if st.button("Login"):
            empty = False
            payload = {
                "username": username,
                "password": password,
            }
            for key, value in payload.items():
                if value == "":
                    empty = True
                    st.warning(f"Please enter your {key}")
            if empty:
                st.stop()
            data = requests.post("https://todoapi-qi3q.onrender.com/user/login", json=data)
            if data.status_code != 202:
                st.error(data.json())
            else:
                st.success("Login successfully")


signup()
log_in()
