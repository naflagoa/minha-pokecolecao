import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Minha PokéColeção", page_icon="🍃", layout="wide")

# Conexão com a Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Customização Completa com CSS Avançado
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

/* APLICAÇÃO GLOBAL DA FONTE POPPINS (Sem quebrar os ícones) */
html, body {
    font-family: 'Poppins', sans-serif !important;
}

h1, h2, h3, h4, h5, h6, p, label, li, span, div.stMarkdown, input, button {
    font-family: 'Poppins', sans-serif;
}

/* PROTEÇÃO PARA OS ÍCONES NATIVOS DO STREAMLIT */
span[class*="material-symbols"], 
i, 
.material-icons, 
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

/* FUNDO DO APLICATIVO MODERNO E LIMPO */
.stApp { background-color: #F8FAF9 !important; }

/* BARRA SUPERIOR (HEADER) */
header[data-testid="stHeader"] { background-color: #3E9A74 !important; }
header[data-testid="stHeader"] * { color: white !important; fill: white !important; }

/* BARRA LATERAL (SIDEBAR) SUAVE */
[data-testid="stSidebar"] { background-color: #EBF2EE !important; }

/* PADRONIZAÇÃO DE TEXTOS PRINCIPAIS */
h1, h2, h3, h4, h5, h6, p, label, span, div.stMarkdown { color: #1E293B !important; }

/* CAIXAS DE INPUT DE TEXTO */
div[data-baseweb="input"], div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 2px 4px !important;
    transition: all 0.2s ease-in-out !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #3E9A74 !important;
    box-shadow: 0 0 0 3px rgba(62, 154, 116, 0.15) !important;
}
div[data-baseweb="input"] input { background-color: #FFFFFF !important; color: #334155 !important; -webkit-text-fill-color: #334155 !important; }

/* CAIXA DE SELEÇÃO (SELECTBOX) */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    transition: all 0.2s ease-in-out !important;
}
div[data-baseweb="select"]:focus-within { border-color: #3E9A74 !important; }
div[data-baseweb="select"] * { color: #334155 !important; }

/* MENU DO SELECTBOX (POPOVER) */
div[data-baseweb="popover"] > div, ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
}
li[role="option"] { color: #334155 !important; background-color: transparent !important; padding: 10px 14px !important; }
li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #E6F4EA !important; color: #1D5A4C !important; }

/* BOTÕES ERGONÓMICOS */
.stButton > button {
    background-color: #3E9A74 !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
}
.stButton > button:hover {
    background-color: #2D7A59 !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* CARDS DAS CARTAS */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 15px !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.025) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.07) !important;
}

/* CARDS DE MÉTRICAS */
[data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    padding: 16px !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.01) !important;
}
</style>
""", unsafe_allow_html=True)

# Funções de manipulação de dados
def carregar_dados():
    try:
        df = conn.read(ttl=0)
        if df.empty: return []
        registros = df.to_dict('records')
        
        for carta in registros:
            for campo in ['concluido', 'favorito']:
                val = carta.get(campo, False)
                if pd.isna(val) or str(val).strip().lower() in ['false', '0', '', 'nan', 'none']:
                    carta[campo] = False
                else:
                    carta[campo] = bool(val)
        return registros
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha. Não faça alterações! Detalhe: {e}")
        st.stop() 

def salvar_dados(dados_lista):
    if not dados_lista:
         df = pd.DataFrame(columns=["nome", "concluido", "imagem", "favorito"])
    else:
         df = pd.DataFrame(dados_lista)
    try:
        conn.update(data=df)
    except Exception as e:
        st.error(f"Falha ao tentar salvar na planilha: {e}")

def buscar_imagem_pokemon(nome_carta):
    try:
        nome_base = nome_carta.split()[0].lower()
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_base}"
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            return dados['sprites']['other']['official-artwork']['front_default']
    except: pass
    return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"

# Inicialização do estado
if 'colecao' not in st.session_state:
    st.session_state.colecao = carregar_dados()

# Topo do Site
col_e1, col_logo, col_e2 = st.columns([1, 1.8, 1])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/98/International_Pok%C3%A9mon_logo.svg", use_container_width=True)

st.markdown("<h2 style='text-align: center; font-weight: 700; margin-top: 10px; margin-bottom: 25px;'>🍃 Coleção de Cartinhas da Carol 🍃</h2>", unsafe_allow_html=True)

# Barra Lateral
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
                    "nome": novo_nome, "concluido": False, "imagem": url_img, "favorito": False
                })
                salvar_dados(st.session_state.colecao)
                st.success(f"{novo_nome} adicionada!")
                st.rerun()
        else:
            st.error("Digite o nome da carta!")

st.divider()

# Filtros
col_busca, col_status = st.columns([2, 1])
with col_busca:
    busca_nome = st.text_input("🔍 Buscar carta pelo nome...", "")
with col_status:
    filtro_status = st.selectbox("Mostrar:", ["Todas", "Obtidas", "Faltando"])

st.write("") 

# Preparando a visualização em 2 blocos separados
if not st.session_state.colecao:
    st.warning("Sua coleção ainda está vazia! Adicione cartas na barra lateral.")
else:
    cartas_favoritas = []
    cartas_outras = []

    # Aplica os filtros e divide a lista em duas
    for carta in st.session_state.colecao:
        if busca_nome.lower() not in str(carta.get('nome', '')).lower():
            continue
        if filtro_status == "Obtidas" and not carta.get('concluido'):
            continue
        if filtro_status == "Faltando" and carta.get('concluido'):
            continue
            
        if carta.get('favorito', False):
            cartas_favoritas.append(carta)
        else:
            cartas_outras.append(carta)

    # Função auxiliar para desenhar a grade de cartas
    def exibir_grade_cartas(lista_cartas):
        num_colunas = 5
        cols = st.columns(num_colunas)
        for i, carta in enumerate(lista_cartas):
            index_original = st.session_state.colecao.index(carta)
            with cols[i % num_colunas]:
                with st.container(border=True):
                    img_url = carta.get('imagem', "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
                    st.image(img_url, use_container_width=True)
                    
                    estrela = "⭐ " if carta.get('favorito', False) else ""
                    st.markdown(f"<p style='font-weight: 600; font-size: 14px; margin-bottom: 2px; text-align: center;'>{estrela}{carta.get('nome', 'Sem nome')}</p>", unsafe_allow_html=True)
                    
                    status = st.checkbox("Tenho", value=bool(carta.get('concluido', False)), key=f"check_{index_original}")
                    
                    if status != carta.get('concluido'):
                        st.session_state.colecao[index_original]['concluido'] = status
                        salvar_dados(st.session_state.colecao)
                        st.rerun()

                    col_fav, col_del = st.columns(2)
                    with col_fav:
                        label_estrela = "⭐" if carta.get('favorito', False) else "☆"
                        if st.button(label_estrela, key=f"fav_{index_original}", use_container_width=True):
                            st.session_state.colecao[index_original]['favorito'] = not carta.get('favorito', False)
                            salvar_dados(st.session_state.colecao)
                            st.rerun()

                    with col_del:
                        if st.button("🗑️", key=f"del_{index_original}", use_container_width=True):
                            st.session_state.colecao.pop(index_original)
                            salvar_dados(st.session_state.colecao)
                            st.rerun()

    # Exibindo os Favoritos
    if cartas_favoritas:
        st.markdown("### ⭐ Meus Favoritos")
        exibir_grade_cartas(cartas_favoritas)

    # Adiciona um divisor somente se existirem cartas nos dois grupos
    if cartas_favoritas and cartas_outras:
        st.divider()

    # Exibindo o restante da coleção
    if cartas_outras:
        st.markdown("### 🍃 Outros Pokémon")
        exibir_grade_cartas(cartas_outras)

    if not cartas_favoritas and not cartas_outras:
        st.info("Nenhuma carta encontrada com esses filtros. 🍃")

# Analytics
st.divider()
st.subheader("📊 Analytics da PokéColeção")
df_metrica = pd.DataFrame(st.session_state.colecao)

if not df_metrica.empty:
    total = len(df_metrica)
    obtidas = len(df_metrica[df_metrica['concluido'] == True] if 'concluido' in df_metrica.columns else [])
    falta = total - obtidas
    progresso = obtidas / total if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Cards", total)
    m2.metric("Na Pasta", obtidas)
    m3.metric("Faltando", falta)
    
    st.write(f"**Progresso Geral: {progresso*100:.1f}%**")
    st.progress(progresso)
