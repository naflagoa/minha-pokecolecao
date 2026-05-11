import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Minha PokéColeção", page_icon="🍃", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# =========================
# CSS PERSONALIZADO (TEMA BULBASAUR)
# =========================
st.markdown("""
<style>
.stApp { background-color: #F0F9F6; }
header[data-testid="stHeader"] { background-color: #3E9A74 !important; }
header[data-testid="stHeader"] * { color: white !important; fill: white !important; }
[data-testid="stSidebar"] { background-color: #DDEEE6; }
h1, h2, h3, p, label, span, div.stMarkdown { color: black !important; font-family: Arial, sans-serif; }

/* ESTILO DOS INPUTS */
div[data-baseweb="input"] {
    background-color: #DDEEE6 !important;
    border: 2px solid #3E9A74 !important;
    border-radius: 10px !important;
    overflow: hidden;
}
div[data-baseweb="input"] input {
    background-color: #C8E6D8 !important;
    color: #1D5A4C !important;
    border-radius: 10px !important;
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
.stButton > button:hover {
    background-color: #73D2C6 !important;
    color: #1D5A4C !important;
    border: 2px solid #1D5A4C !important;
}

/* CARDS DAS CARTAS */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
    background-color: white;
    border: 2px solid #73D2C6 !important;
    border-radius: 12px !important;
    padding: 15px;
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
# FUNÇÕES DE DADOS E API
# =========================
def carregar_dados():
    try:
        # Lê os dados da planilha em tempo real
        df = conn.read(ttl=0)
        return df.to_dict('records')
    except:
        return []

def salvar_dados(dados_lista):
    # Converte a lista para DataFrame e atualiza o Google Sheets
    df = pd.DataFrame(dados_lista)
    conn.update(data=df)

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
# INTERFACE PRINCIPAL (LOGO E TÍTULO)
# =========================
col_e1, col_logo, col_e2 = st.columns([1, 2, 1])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/International_Pok%C3%A9mon_logo.svg", use_container_width=True)

st.markdown("<h3 style='text-align: center;'>🍃 Coleção de Cartinhas da Carol 🍃</h3>", unsafe_allow_html=True)

# =========================
# SIDEBAR (CADASTRO)
# =========================
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Desenvolvido para a coleção da Carol.")
    st.divider()
    
    st.subheader("🍃 Nova Carta")
    novo_nome = st.text_input("Nome da Carta (ex: Bulbasaur)")
    
    if st.button("Adicionar à Coleção"):
        novo_nome = novo_nome.strip()
        if novo_nome:
            cartas_existentes = [str(c.get('nome', '')).lower() for c in st.session_state.colecao]
            if novo_nome.lower() in cartas_existentes:
                st.warning("Esta carta já está na sua coleção!")
            else:
                url_img = buscar_imagem_pokemon(novo_nome)
                st.session_state.colecao.append({
                    "nome": novo_nome,
                    "concluido": False,
                    "imagem": url_img
                })
                salvar_dados(st.session_state.colecao)
                st.success(f"{novo_nome} adicionada!")
                st.rerun()
        else:
            st.error("Digite o nome da carta!")

# =========================
# EXIBIÇÃO DA COLEÇÃO (COM FILTROS)
# =========================
st.divider()

# Layout dos filtros
col_busca, col_status = st.columns([2, 1])

with col_busca:
    busca_nome = st.text_input("🔍 Buscar carta pelo nome...", "")

with col_status:
    filtro_status = st.selectbox("Mostrar:", ["Todas", "Obtidas", "Faltando"])

st.write("") 

if not st.session_state.colecao:
    st.warning("Sua coleção ainda está vazia! Adicione cartas na barra lateral.")
else:
    cols = st.columns(3)
    cartas_exibidas = 0 
    
    for index, carta in enumerate(st.session_state.colecao):
        # Lógica de Filtros
        if busca_nome.lower() not in str(carta.get('nome', '')).lower():
            continue
        
        if filtro_status == "Obtidas" and not carta.get('concluido'):
            continue
        if filtro_status == "Faltando" and carta.get('concluido'):
            continue
            
        # Renderização do Card
        with cols[cartas_exibidas % 3]:
            with st.container(border=True):
                img_url = carta.get('imagem', "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
                st.image(img_url, use_container_width=True)
                
                st.markdown(f"**{carta.get('nome', 'Sem nome')}**")
                
                status = st.checkbox("Tenho", value=bool(carta.get('concluido', False)), key=f"check_{index}")
                
                if status != carta.get('concluido'):
                    st.session_state.colecao[index]['concluido'] = status
                    salvar_dados(st.session_state.colecao)
                    st.rerun()

                if st.button("🗑️", key=f"del_{index}", use_container_width=True):
                    st.session_state.colecao.pop(index)
                    salvar_dados(st.session_state.colecao)
                    st.rerun()
                    
        cartas_exibidas += 1
        
    if cartas_exibidas == 0:
        st.info("Nenhuma carta encontrada com esses filtros. 🍃")

# =========================
# DASHBOARD / ANALYTICS
# =========================
st.divider()
st.subheader("📊 Analytics da PokéColeção")
df_metrica = pd.DataFrame(st.session_state.colecao)

if not df_metrica.empty:
    total = len(df_metrica)
    obtidas = len(df_metrica[df_metrica['concluido'] == True])
    falta = total - obtidas
    progresso = obtidas / total if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Cards", total)
    m2.metric("Na Pasta", obtidas)
    m3.metric("Faltando", falta)
    
    st.write(f"**Progresso Geral: {progresso*100:.1f}%**")
    st.progress(progresso)
