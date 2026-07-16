import streamlit as st
import yt_dlp
import os

# Configuração da página e ocultação de menus padrão do Streamlit
st.set_page_config(
    page_title="8K_DOWNLOAD",
    page_icon="📥",
    layout="centered"
)

# --- CUSTOMIZAÇÃO VISUAL COMPLETA (DESIGN PREMIUM DA FOTO) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #090815 0%, #151632 50%, #0d0f1d 100%) !important;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3, p, label, .stCaption {
        color: #FFFFFF !important;
    }
    .stTextInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"] {
        background-color: #121324 !important;
        border: 1px solid #23275b !important;
        border-radius: 14px !important;
        color: #FFFFFF !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #0072ff 0%, #7a00ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        height: 3.2em !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0px 4px 15px rgba(122, 0, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div.stDownloadButton > button {
        background-color: #1c1d3a !important;
        color: #38b6ff !important;
        border: 1px solid #38b6ff !important;
        border-radius: 14px !important;
        height: 3.2em !important;
        font-weight: bold !important;
        font-size: 16px !important;
        margin-top: 15px !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Inicialização das variáveis de estado (Session State)
if "dados_midia" not in st.session_state:
    st.session_state.dados_midia = None
if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = ""
if "titulo_video" not in st.session_state:
    st.session_state.titulo_video = ""


# Função de download em segundo plano com Autenticação Invisível
def baixar_conteudo_web(url, formato, progresso_bar, status_text):
    pasta_temp = "downloads_temp"
    os.makedirs(pasta_temp, exist_ok=True)
    template_destino = os.path.join(pasta_temp, '%(title)s.%(ext)s')

    def progress_callback(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            baixado = d.get('downloaded_bytes', 0)
            if total > 0:
                porcentagem = baixado / total
                progresso_bar.progress(porcentagem)
                status_text.text(f"Baixando: {int(porcentagem * 100)}%")
        elif d['status'] == 'finished':
            progresso_bar.progress(1.0)
            status_text.text("Concluído no servidor! Gerando arquivo...")

    ydl_opts = {
        'progress_hooks': [progress_callback],
        'outtmpl': template_destino,
        'extracted_flat': False,
        'nocheckcertificate': True,
        'quiet': True,
    }

    # --- LÓGICA DE CONTA BOT / TESTES INVISÍVEL ---
    # Se o arquivo cookies.txt da sua conta bot estiver no servidor, o app usa automaticamente
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

    if formato == "Áudio (MP3)":
        ydl_opts.update({'format': 'bestaudio'})
    else:
        ydl_opts['format'] = 'best[ext=mp4]/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        caminho_arquivo = ydl.prepare_filename(info)

        if not os.path.exists(caminho_arquivo):
            nome_base, _ = os.path.splitext(caminho_arquivo)
            for f in os.listdir(pasta_temp):
                if f.startswith(os.path.basename(nome_base)):
                    caminho_arquivo = os.path.join(pasta_temp, f)
                    break

        return caminho_arquivo, info.get('title', 'video')


# --- ESTRUTURA VISUAL DA INTERFACE ---

st.markdown('<h1 style="text-align: center; margin-bottom: 0px;">📥 DOWNLOAD EM 8K</h1>', unsafe_allow_html=True)
st.caption("Insira o link abaixo para baixar vídeos ou áudios direto no seu celular.")

# Elementos de entrada de dados (Sem campos extras de arquivos)
url_input = st.text_input("URL do Vídeo:", placeholder="Cole o link do YouTube, Instagram, etc...")
formato_input = st.selectbox("Selecione o formato:", ["Vídeo (MP4)", "Áudio (MP3)"])

# Espaço reservado para as mensagens de status e progresso
barra = st.empty()
status = st.empty()

# Botão principal de ação
if st.button("Processar Download", use_container_width=True):
    if not url_input:
        st.warning("Por favor, insira uma URL válida.")
    else:
        progresso_barra = barra.progress(0)
        status_texto = status.text("Iniciando conexão...")

        try:
            caminho_local, titulo = baixar_conteudo_web(url_input, formato_input, progresso_barra, status_texto)

            with open(caminho_local, "rb") as f:
                st.session_state.dados_midia = f.read()

            st.session_state.titulo_video = titulo
            st.session_state.nome_arquivo = os.path.basename(caminho_local)

            status_texto.text("")
            progresso_barra.empty()
            status.success(f"Pronto: {titulo}")

            os.remove(caminho_local)

        except Exception as e:
            status.error(f"Erro no processamento: {e}")

# --- EXIBIÇÃO NA MESMA TELA ---
if st.session_state.dados_midia is not None:
    st.download_button(
        label="➡️ SALVAR EM ARQUIVOS DO IPHONE ⬅️",
        data=st.session_state.dados_midia,
        file_name=st.session_state.nome_arquivo,
        mime="video/mp4" if st.session_state.nome_arquivo.endswith(".mp4") else "audio/mp3",
        use_container_width=True
    )
