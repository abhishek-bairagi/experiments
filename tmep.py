import streamlit as st
st.title("💬 TechCare Caht")
st.caption("🚀 A Demo of Product Extraction ")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = prompt
    # msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content":response})
    st.chat_message("assistant").write(response)
