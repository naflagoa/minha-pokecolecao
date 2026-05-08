import streamlit as st
import json
import pandas as pd
import requests

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Minha PokéColeção", page_icon="🍃", layout="centered")

# =========================
# CSS PERSONALIZADO 
# =========================
st.markdown("""
<style>
.stApp { background-color: #F0F9F6; }
header[data-testid="stHeader"] { background-color: #3E9A74 !important; }
header[data-testid="stHeader"] * { color: white !important; fill: white !important; }
[data-testid="stSidebar"] { background-color: #DDEEE6; }
h1, h2, h3, p, label, span, div.stMarkdown { color: black !important; font-family: Arial, sans-serif; }
div[data-baseweb="input"] { background-color: #DDEEE6 !important; border: 2px solid #3E9A74 !important; border-radius: 10px !important; overflow: hidden; }
div[data-baseweb="input"] input { background-color: #C8E6D8 !important; color: #1D5A4C !important; border-radius: 10px !important; }
div[data-baseweb="input"]:focus-within { border: 2px solid #73D2C6 !important; box-shadow: 0 0 8px #73D2C6 !important; }
.stButton > button { background-color: #3E9A74 !important; color: white !important; border-radius: 10px !important; border: 2px solid #1D5A4C !important; font-weight: bold !important; transition: 0.3s !important; }
.stButton > button:hover { background-color: #73D2C6 !important; color: #1D5A4C !important; border: 2px solid #1D5A4C !important; }
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] { background-color: white; border: 2px solid #73D2C6 !important; border-radius: 12px !important; padding: 10px; }
.stCheckbox label { color: #1D5A4C !important; font-weight: bold; }
[data-testid="metric-container"] { background-color: #DDEEE6; border: 2px solid #73D2C6; padding: 10px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES DE DADOS E API
# =========================
def carregar_dados():
    try:
        with open("portfolio_pokemon.json", "r") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_dados(dados):
    with open("portfolio_pokemon.json", "w") as arquivo:
        json.dump(dados, arquivo, indent=4)

def buscar_imagem_pokemon(nome_carta):
    try:
        nome_base = nome_carta.split()[0].lower()
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_base}"
        
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            return dados['sprites']['other']['official-artwork']['front_default']
    except:
        pass
    return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"

# =========================
# SESSION STATE
# =========================
if 'colecao' not in st.session_state:
    st.session_state.colecao = carregar_dados()

# =========================
# INTERFACE PRINCIPAL (LOGO)
# =========================
# Usando colunas para deixar o logo bem centralizado na tela
col_espaco1, col_logo, col_espaco2 = st.columns([1, 2, 1])

with col_logo:
    # URL do logo oficial com fundo transparente
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/International_Pok%C3%A9mon_logo.svg", use_container_width=True)

st.markdown("<h3 style='text-align: center;'>🍃 Coleção de Cartinhas 🍃</h3>", unsafe_allow_html=True)
st.write("") # Dá um espacinho antes de começar as cartas

# =========================
# SIDEBAR (NOVA CARTA)
# =========================
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Desenvolvido para a coleção da Carol.")
    st.divider()
    
    st.subheader("🍃 Nova Carta")
    novo_nome = st.text_input("Nome da Carta (ex: Charizard ex)")
    
    if st.button("Adicionar à Coleção"):
        novo_nome = novo_nome.strip()
        
        if novo_nome:
            cartas_existentes = [carta['nome'].lower() for carta in st.session_state.colecao]
            
            if novo_nome.lower() in cartas_existentes:
                st.warning("Esta carta já está na sua coleção!")
            else:
                url_imagem = buscar_imagem_pokemon(novo_nome)
                
                st.session_state.colecao.append({
                    "nome": novo_nome,
                    "concluido": False,
                    "imagem": url_imagem
                })
                salvar_dados(st.session_state.colecao)
                st.success(f"{novo_nome} adicionada!")
                st.rerun()
        else:
            st.error("Digite o nome da carta!")

# =========================
# EXIBIÇÃO DAS CARTAS
# =========================
st.subheader("🍃 Minha Coleção")

if not st.session_state.colecao:
    st.warning("Sua coleção ainda está vazia!")
else:
    cols = st.columns(3)
    
    for index, carta in enumerate(st.session_state.colecao):
        with cols[index % 3]:
            with st.container(border=True):
                img_url = carta.get('imagem', "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
                st.image(img_url, use_container_width=True)
                
                st.markdown(f"### {carta['nome']}")
                status = st.checkbox("Tenho na coleção", value=carta['concluido'], key=f"check_{index}")
                
                if status != carta['concluido']:
                    st.session_state.colecao[index]['concluido'] = status
                    salvar_dados(st.session_state.colecao)
                    st.rerun()

                if st.button("🗑️", key=f"del_{index}", use_container_width=True):
                    st.session_state.colecao.pop(index)
                    salvar_dados(st.session_state.colecao)
                    st.rerun()

# =========================
# DASHBOARD
# =========================
st.divider()
st.subheader("🍃 Analytics da PokéColeção")

df = pd.DataFrame(st.session_state.colecao)

if not df.empty:
    total = len(df)
    obtidas = df[df['concluido'] == True].shape[0]
    falta = total - obtidas
    progresso = obtidas / total if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Cards", total)
    m2.metric("Na Pasta", obtidas)
    m3.metric("Faltando", falta)
    
    st.write(f"### Progresso Geral: {progresso*100:.1f}%")
    st.progress(progresso)
else:
    st.write("Adicione cartas para visualizar as métricas.")
