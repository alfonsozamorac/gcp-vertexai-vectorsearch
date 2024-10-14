import os
import streamlit as st
import requests
import subprocess


def get_gcp_token():
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"],
            universal_newlines=True
        ).strip()
        return token
    except subprocess.CalledProcessError as e:
        st.error(f"Error getting the GCP token: {e}")
        return None


CLOUDRUN_URI = os.getenv("CLOUDRUN_URI")
CHATBOT_URI = f"{CLOUDRUN_URI}/chatbot"
UPDATEINDEX_URI = f"{CLOUDRUN_URI}/update_index"


token = get_gcp_token()


if token:
    headers = {"Authorization": f"Bearer {token}"}

    st.title("Confluence Chatbot")
    st.header("Update index")

    with st.form("Update Index"):
        numbers = st.text_input(
            "Enter Confluence page IDs separated by commas")
        complete_overwrite = st.selectbox(
            "Is complete overwrite", ("false", "true"))
        submit_numbers = st.form_submit_button("Send")

        if submit_numbers:
            try:
                number_list = [int(x.strip()) for x in numbers.split(",")]
                response = requests.post(UPDATEINDEX_URI, json={
                                         "page_ids": number_list, "is_complete_overwrite": complete_overwrite}, headers=headers)

                if response.status_code == 200:
                    api_response = response.json().get("result", "No response")
                    st.success(api_response)
                else:
                    st.error("Error sending the page ids. Response code:",
                             response.status_code)
            except Exception as e:
                st.error(f"Error index update: {e}")

    st.header("Chat")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    with st.form("Chat Form"):
        user_message = st.text_input("Write your message")
        submit_message = st.form_submit_button("Send")

        if submit_message and user_message:
            try:
                response = requests.post(
                    CHATBOT_URI, json={"question": user_message}, headers=headers)
                if response.status_code == 200:
                    api_response = response.json().get("result", "No response")
                    st.session_state['chat_history'].append(
                        {"question": user_message, "response": api_response})
                else:
                    st.session_state['chat_history'].append(
                        {"question": user_message, "response": f"API Error: {response.status_code}"})
            except Exception as e:
                st.session_state['chat_history'].append(
                    {"question": user_message, "response": f"API Error: {response.status_code}"})

st.subheader("Chat History")

st.markdown("""
    <style>
    .user-message {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        text-align: right;
        color: black;
    }
    .bot-message {
        background-color: #f1f0f0;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        text-align: left;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

for entry in reversed(st.session_state['chat_history']):
    st.markdown(
        f'<div class="user-message"> {entry["question"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="bot-message"> {entry["response"]}</div>', unsafe_allow_html=True)
    st.divider()
