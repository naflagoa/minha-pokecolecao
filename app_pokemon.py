import streamlit as st
import json
import pandas as pd
import random

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Minha PokéColeção",
    page_icon="🍃",
    layout="centered"
)

# =========================
# CSS PERSONALIZADO
# =========================
st.markdown("""
<style>
/* FUNDO GERAL */
.stApp { background-color: #F0F9F6; }

/* TOPO DO STREAMLIT */
header[data-testid="stHeader"] { background-color: #3E9A74 !important; }

/* TEXOS E ÍCONES DO TOPO */
header[data-testid="stHeader"] * { color: white !important; fill: white !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #DDEEE6; }

/* TEXTOS */
h1, h2, h3, p, label, span, div.stMarkdown {
    color: black !important;
    font-family: Arial, sans-serif;
}

/* INPUTS */
div[data-baseweb="input"] {
    background-color: #DDEEE6 !important;
    border: 2px solid #3E9A74 !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* FUNDO INTERNO DO INPUT */
div[data-baseweb="input"] input {
    background-color: #C8E6D8 !important;
    color: #1D5A4C !important;
    border-radius: 10px !important;
}

/* QUANDO CLICA */
div[data-baseweb="input"]:focus-within {
    border: 2px solid #73D2C6 !important;
    box-shadow: 0 0 8px #73D2C6 !important;
}

/* BOTÕES */
.stButton > button {
    background-color: #3E9A74 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 2px solid #1D5A4C !important;
    font-weight: bold !important;
    transition: 0.3s !important;
}

/* HOVER BOTÃO */
.stButton > button:hover {
    background-color: #73D2C6 !important;
    color: #1D5A4C !important;
    border: 2px solid #1D5A4C !important;
}

/* CARDS */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
    background-color: white;
    border: 2px solid #73D2C6 !important;
    border-radius: 12px !important;
    padding: 10px;
}

/* CHECKBOX */
.stCheckbox label {
    color: #1D5A4C !important;
    font-weight: bold;
}

/* MÉTRICAS */
[data-testid="metric-container"] {
    background-color: #DDEEE6;
    border: 2px solid #73D2C6;
    padding: 10px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
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

# =========================
# SESSION STATE
# =========================
if 'colecao' not in st.session_state:
    st.session_state.colecao = carregar_dados()

# =========================
# GIFS
# =========================
gifs_fofos = {
    "Bulbasaur": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/1.gif",
    "Pikachu": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/25.gif",
    "Eevee": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/133.gif",
    "Squirtle": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/7.gif",
    "Charmander": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/4.gif"
}

# =========================
# TÍTULO
# =========================
st.markdown("## 🍃 Coleção de Cartinhas Pokémon 🍃")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    nome_poke, link_gif = random.choice(list(gifs_fofos.items()))
    st.image(link_gif, caption=f"Um {nome_poke} selvagem apareceu!")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Desenvolvido para a coleção da Carol.")
    st.divider()
    
    st.subheader("🍃 Nova Carta")
    novo_nome = st.text_input("Nome da Carta (ex: Charizard ex)")
    
    if st.button("Adicionar à Coleção"):
        novo_nome = novo_nome.strip() # Remove espaços vazios no início e fim
        
        if novo_nome:
            # Verifica se a carta já existe na coleção
            cartas_existentes = [carta['nome'].lower() for carta in st.session_state.colecao]
            
            if novo_nome.lower() in cartas_existentes:
                st.warning("Esta carta já está na sua coleção!")
            else:
                st.session_state.colecao.append({
                    "nome": novo_nome,
                    "concluido": False
                })
                salvar_dados(st.session_state.colecao)
                st.success(f"{novo_nome} adicionada!")
                st.rerun()
        else:
            st.error("Digite o nome da carta!")

# =========================
# COLEÇÃO
# =========================
st.subheader("🍃 Minha Coleção")

if not st.session_state.colecao:
    st.warning("Sua coleção ainda está vazia!")
else:
    cols = st.columns(3)
    
    for index, carta in enumerate(st.session_state.colecao):
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"### {carta['nome']}")
                
                status = st.checkbox("Tenho na coleção", value=carta['concluido'], key=f"check_{index}")
                
                if status != carta['concluido']:
                    st.session_state.colecao[index]['concluido'] = status
                    salvar_dados(st.session_state.colecao)
                    st.rerun()

                if st.button("🗑️ Remover", key=f"del_{index}", use_container_width=True):
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