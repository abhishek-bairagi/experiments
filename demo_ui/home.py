import streamlit as st
import requests

st.set_page_config(layout="wide")
user_details = {
          "id": "user11",
          "name": "Abhishek Bairagi",
          "email": "abhishek.bairagi@example.com",
          "location": "India",
          "band": 30,
          "team": "DW"
        }

device_details = {
      "id": "dev11",
      "os": "macos",
      "lastupdate": "2025-06-10",
      "os_version": "14.3",
      "ram": 16,
      "storage": 512,
      "model": "MacBook Pro M2",
      "issued_on": "2025-06-09",
      "pending_updates": ["audio driver - mac", "slack"]
      }
# Sidebar with heading and user/device details
st.sidebar.title("🚀 TechCare: Powered by KG")

# User details section
st.sidebar.header("👤 User Details")
st.sidebar.markdown(f"**Name:** {user_details['name']}")
st.sidebar.markdown(f"**Location:** {user_details['location']}")
st.sidebar.markdown(f"**Band:** {user_details['band']}")
st.sidebar.markdown(f"**Team:** {user_details['team']}")

# Device details section
st.sidebar.header("💻 Device Details")
st.sidebar.markdown(f"**Device:** Mac")
st.sidebar.markdown(f"**OS:** macOS")
# Expander for detailed device information
with st.sidebar.expander("💡 More Device Info"):
    st.markdown(f"**Model:** {device_details['model']}")
    st.markdown(f"**OS Version:** {device_details['os_version']}")
    st.markdown(f"**RAM:** {device_details['ram']} GB")
    st.markdown(f"**Storage:** {device_details['storage']} GB")
    st.markdown(f"**Issued On:** {device_details['issued_on']}")
    st.markdown(f"**Last Update:** {device_details['lastupdate']}")
    st.markdown("**Pending Updates:**")
    for update in device_details["pending_updates"]:
        st.markdown(f"- {update}")

# Define functions for search
def typical_rag_search(query):
    try:
        response = requests.post(
            "http://0.0.0.0:8003/generate_results/rag",
            params={"query": query, "user_id": user_details["id"]},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def kg_rag_search(query):
    try:
        response = requests.post(
            "http://0.0.0.0:8003/generate_results/kg",
            params={"query": query, "user_id":  user_details["id"]},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Initialize session state for responses
if "typical_rag_response" not in st.session_state:
    st.session_state.typical_rag_response = {}

if "kg_rag_response" not in st.session_state:
    st.session_state.kg_rag_response = {}

# Main layout
# st.title("TechCare Chatbot - Enhanced")

# Create two columns with a vertical line in between

def vertical_padding(n):
    for _ in range(n):
        st.write("")

# Single query input and button
col1, col2 = st.columns([0.9,0.1])
with col1:
    query = st.text_input("Enter your query:")
with col2:
    vertical_padding(2)
    button = st.button("Send")
if button and query:
    st.session_state.typical_rag_response = typical_rag_search(query)
    st.session_state.kg_rag_response = kg_rag_search(query)

col1, spacer, col2 = st.columns([1, 0.05, 1])
# Column 1: Typical RAG
with col1:
    st.markdown(
        "<h2 style='text-align: center; font-family: Arial, sans-serif;'>📊 Typical RAG</h2>",
        unsafe_allow_html=True,
    )
    if st.session_state.typical_rag_response:
        response = st.session_state.typical_rag_response
        if "error" in response:
            st.error(response["error"])
        else:
            with st.expander("RAG Response"):
                st.write(response.get("vanilla_response", "No response"))
            with st.expander("Retrieved Articles"):
                st.markdown(response.get("retrieved_articles", "No articles"))

# Spacer: Vertical line
with spacer:
    st.markdown(
        """
        <div style="border-left: 1px solid #ccc; height: 100vh;"></div>
        """,
        unsafe_allow_html=True,
    )

# Column 2: KG+RAG
with col2:
    st.markdown(
        "<h2 style='text-align: center; font-family: Arial, sans-serif;'>🔍 KG+RAG</h2>",
        unsafe_allow_html=True,
    )
    if st.session_state.kg_rag_response:
        response = st.session_state.kg_rag_response
        if "error" in response:
            st.error(response["error"])
        else:
            with st.expander("KG Response"):
                st.write(response.get("kg_response", "No response"))
            with st.expander("Retrieved Articles"):
                
                st.markdown(response.get("retrieved_articles", "No articles"))
            with st.expander("Structured KG Output"):
                print(response.get("structured_kg_output", "No structured output"))
                st.text(response.get("structured_kg_output", "No structured output"))