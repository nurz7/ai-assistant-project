import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="AI Operations Assistant",
    layout="centered"
)

st.title("AI Operations Assistant")
st.write("Internal AI assistant for business workflow automation.")

user_message = st.text_area(
    "Enter your question:",
    placeholder="Example: What can this assistant do?"
)

if st.button("Send"):
    if not user_message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            response = requests.post(
                API_URL,
                json={"message": user_message},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Assistant answer")
                st.write(data["answer"])

                st.subheader("User message")
                st.write(data["user_message"])
            else:
                st.error(f"API error: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("Backend is not running. Start FastAPI first.")
        except Exception as error:
            st.error(f"Unexpected error: {error}")
