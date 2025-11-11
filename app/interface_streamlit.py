# app/interface_streamlit.py
import streamlit as st
from Aula1.core.chatbot.rag import rag_pipeline

st.set_page_config(page_title="Fitbit Insights", page_icon="💪", layout="centered")

st.title("💪 Fitbit Insights – Pergunte aos Dados")

question = st.text_input("Faça uma pergunta sobre os usuários, passos ou calorias:")

if st.button("Analisar"):
    if question.strip():
        with st.spinner("Analisando..."):
            resposta = rag_pipeline(question)
            st.markdown(resposta)
    else:
        st.warning("Digite uma pergunta antes de continuar.")
