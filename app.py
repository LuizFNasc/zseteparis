import streamlit as st
from PIL import Image
import openai
import base64
import io
import os
from utils import criar_banco
criar_banco()


# Defina sua chave da OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")


# ===================== FUNÇÕES ===================== #

# Carrega o resumo dos kits do .txt
@st.cache_data
def carregar_kits_txt(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

# Converte imagem para base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Chamada à OpenAI
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

# ===================== INTERFACE ===================== #

# Botão para reiniciar
if st.button("🔄 Nova análise"):
    for key in ["recomendacao", "nome", "email", "telefone", "tipo", "quimica", "problema", "objetivo", "imagem"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Cabeçalho
st.title("Descubra o Kit Ideal para seu Cabelo 💇‍♀️")

# Inicia recomendação na sessão
if "recomendacao" not in st.session_state:
    st.session_state.recomendacao = ""

# Upload de imagem
uploaded_image = st.file_uploader("Envie uma foto do seu cabelo", type=["jpg", "png"], key="imagem")

# Dados do usuário
st.subheader("Seus dados")
nome = st.text_input("Nome completo", key="nome")
email = st.text_input("E-mail", key="email")
telefone = st.text_input("Telefone com DDD", placeholder="Ex: (11) 91234-5678", key="telefone")

# Perfil capilar
st.subheader("Seu perfil capilar")
tipo = st.selectbox("Tipo de cabelo:", ["", "Liso", "Ondulado", "Cacheado", "Crespo"], key="tipo")
quimica = st.selectbox("Tem química?", ["", "Sim", "Não"], key="quimica")
problema = st.selectbox("Problema:", ["", "Oleosidade", "Ressecamento", "Frizz", "Quebra"], key="problema")
objetivo = st.selectbox("Objetivo:", ["", "Hidratação", "Reconstrução", "Crescimento", "Manutenção"], key="objetivo")

# Carrega catálogo de kits
catalogo = carregar_kits_txt("simples_descricao.txt")

# Botão de recomendação
if st.button("Ver recomendação"):
    if not nome or not email or not telefone:
        st.warning("Preencha seus dados pessoais.")
    elif "" in [tipo, quimica, problema, objetivo]:
        st.warning("Responda todo o formulário.")
    elif not uploaded_image:
        st.warning("Envie uma foto do seu cabelo.")
    else:
        with st.spinner("Analisando seu cabelo e suas respostas..."):
            image = Image.open(uploaded_image)
            image_b64 = image_to_base64(image)
            respostas = {
                "tipo": tipo,
                "quimica": quimica,
                "problema": problema,
                "objetivo": objetivo
            }
            resultado = consultar_openai(image_b64, respostas, catalogo)
            from utils import salvar_lead

            st.session_state.recomendacao = resultado
            salvar_lead(nome, email, telefone, tipo, quimica, problema, objetivo, resultado)


# Exibe resultado
if st.session_state.recomendacao:
    st.success("Produto ideal encontrado:")
    st.markdown(st.session_state.recomendacao)
    if uploaded_image:
        st.image(uploaded_image, caption="Sua foto enviada", use_container_width=True)
