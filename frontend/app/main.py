import streamlit as st

st.title("Meu primeiro app com Streamlit")
st.write("Olá, mundo! 👋")

# Entrada de texto
nome = st.text_input("Digite seu nome:")

if nome:
    st.success(f"Bem-vindo, {nome}!")