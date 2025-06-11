
import streamlit as st
from PIL import Image
import openai
import base64
import io
import sqlite3
import os

# Chave da OpenAI (via secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ========= FUNÇÕES ========= #

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            tipo TEXT,
            quimica TEXT,
            problema TEXT,
            objetivo TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_lead(nome, email, telefone, tipo, quimica, problema, objetivo):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leads (nome, email, telefone, tipo, quimica, problema, objetivo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (nome, email, telefone, tipo, quimica, problema, objetivo))
    conn.commit()
    conn.close()

def carregar_kits_txt(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def consultar_openai(imagem_b64, respostas, catalogo):
    prompt = f"""
Sou especialista em cuidados capilares. Com base nas informações abaixo, indique o melhor kit da lista e explique brevemente.

Tipo: {respostas['tipo']}
Química: {respostas['quimica']}
Problema: {respostas['problema']}
Objetivo: {respostas['objetivo']}

Kits disponíveis:
{catalogo}

Informe o nome do kit ideal e uma explicação curta.
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{imagem_b64}"}}
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

# ========= INTERFACE ========= #
init_db()

st.title("Descubra o Kit Ideal para seu Cabelo 💇‍♀️")

if st.button("🔄 Nova análise"):
    for key in st.session_state.keys():
        st.session_state[key] = ""
    st.rerun()

if "recomendacao" not in st.session_state:
    st.session_state.recomendacao = ""

uploaded_image = st.file_uploader("Envie uma foto do seu cabelo", type=["jpg", "png"])

st.subheader("Seus dados")
nome = st.text_input("Nome completo")
email = st.text_input("E-mail")
telefone = st.text_input("Telefone com DDD", placeholder="Ex: (11) 91234-5678")

st.subheader("Seu perfil capilar")
tipo = st.selectbox("Tipo de cabelo:", ["", "Liso", "Ondulado", "Cacheado", "Crespo"])
quimica = st.selectbox("Tem química?", ["", "Sim", "Não"])
problema = st.selectbox("Problema:", ["", "Oleosidade", "Ressecamento", "Frizz", "Quebra"])
objetivo = st.selectbox("Objetivo:", ["", "Hidratação", "Reconstrução", "Crescimento", "Manutenção"])

catalogo = carregar_kits_txt("simples_descricao.txt")

if st.button("Ver recomendação"):
    if not nome or not email or not telefone:
        st.warning("Preencha seus dados pessoais.")
    elif "" in [tipo, quimica, problema, objetivo]:
        st.warning("Responda todo o formulário.")
    elif not uploaded_image:
        st.warning("Envie uma foto do seu cabelo.")
    else:
        with st.spinner("Analisando..."):
            image = Image.open(uploaded_image)
            image_b64 = image_to_base64(image)
            respostas = {"tipo": tipo, "quimica": quimica, "problema": problema, "objetivo": objetivo}
            resultado = consultar_openai(image_b64, respostas, catalogo)
            st.session_state.recomendacao = resultado
            salvar_lead(nome, email, telefone, tipo, quimica, problema, objetivo)

if st.session_state.recomendacao:
    st.success("Produto ideal encontrado:")
    st.markdown(st.session_state.recomendacao)
    if uploaded_image:
        st.image(uploaded_image, caption="Sua foto enviada", use_container_width=True)
