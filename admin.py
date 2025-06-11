import streamlit as st
import pandas as pd
import sqlite3
from utils import carregar_leads, autenticar

st.title("🔒 Acesso ao Dashboard")

# Login
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if autenticar(usuario, senha):
        st.session_state.autenticado = True
    else:
        st.error("Usuário ou senha inválidos")

if st.session_state.get("autenticado", False):
    st.success("Bem-vindo ao painel de leads!")

    # Carregar leads do SQLite
    conn = sqlite3.connect("leads.db")
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY data_hora DESC", conn)
    conn.close()

    st.dataframe(df)
    st.metric("Total de Leads", len(df))
    st.download_button("📥 Baixar como CSV", df.to_csv(index=False), "leads.csv", "text/csv")
