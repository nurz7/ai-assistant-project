import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")
API_CONNECT_TIMEOUT_SECONDS = 5
API_READ_TIMEOUT_SECONDS = 70

st.set_page_config(
    page_title="AI/GIS Copilot for Reservoir Monitoring",
    page_icon=":material/water_drop:",
    layout="centered",
)

st.title("AI/GIS Copilot for Reservoir Monitoring")
st.write("Assistant prototype for reservoir monitoring methodology and demo workflows.")

user_message = st.text_area(
    "Enter your question:",
    placeholder="Example: What is MNDWI used for in water surface detection?",
)

if st.button("Send"):
    if not user_message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            response = requests.post(
                API_URL,
                json={"message": user_message},
                timeout=(API_CONNECT_TIMEOUT_SECONDS, API_READ_TIMEOUT_SECONDS),
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Assistant answer")
                st.write(data["answer"])
                st.caption(f"Response mode: {data['mode']}")
                st.caption(f"Intent: {data.get('intent', 'unknown')}")

                if data.get("reservoir"):
                    st.subheader("Reservoir")
                    st.write(data["reservoir"])

                if data.get("calculation_result"):
                    st.subheader("Calculation")
                    st.write(data["calculation_result"])

                if data.get("sources"):
                    st.subheader("Sources")
                    for source in data["sources"]:
                        st.write(
                            f"- {source['document']} — {source['section']} "
                            f"(`{source['chunk_id']}`)"
                        )

                for warning in data.get("warnings", []):
                    st.warning(warning)

                st.subheader("User message")
                st.write(data["user_message"])
            else:
                st.error(f"API error: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.Timeout:
            st.error("Backend response timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Backend is not running. Start FastAPI first.")
        except Exception as error:
            st.error(f"Unexpected error: {error}")
