import streamlit as st
import requests

st.header(":rainbow[Todo App] :white_check_mark:", anchor=False)

sign_up, login = st.columns(2)


def signup():
    with sign_up:
        st.subheader(":blue[Sign Up]", anchor=False)
        st.write("")
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
            try:
                request = requests.post("https://todoapi-qi3q.onrender.com/user/signup", json=payload)
            except requests.exceptions.RequestException as e:
                log_in()
                st.error("Failed to Signup... Ensure you are connected to the internet and try again.")
                st.stop()
            if request.status_code != 201:
                if request.status_code == 500:
                    st.error("Something went wrong on our side.")
                    log_in()
                    st.stop()
                elif request.status_code == 422:
                    message = request.json()["detail"][0]["msg"]
                    st.error(message)
                elif request.status_code == 226:
                    st.error(request.json()["detail"])
                else:
                    st.error("something went wrong")
            else:
                st.success("Signed up successfully log in here")


def log_in():
    with login:
        st.subheader(":violet[Log In]", anchor=False)
        st.write("")
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
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            try:
                request = requests.post("https://todoapi-qi3q.onrender.com/user/login", data=payload, headers=headers)
            except requests.exceptions.RequestException as e:
                st.error("Failed to Login... Ensure you are connected to the internet and try again.")
                st.stop()
            if request.status_code != 202:
                if request.status_code == 500:
                    st.error("Something went wrong on our side.")
                    st.stop()
                message = request.json()["detail"]
                st.error(message)
            else:
                st.success("Login successfully")


signup()
log_in()
