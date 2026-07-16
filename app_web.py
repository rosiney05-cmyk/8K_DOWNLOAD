import streamlit as st
import yt_dlp
import os
import io

# Configuração da página Web (Visual Moderno e Responsivo)
st.set_page_config(
    page_title="8K_DOWNLOAD",
    page_icon="📥",
    layout="centered"
)

# Estilização CSS customizada para deixar os botões com cara de aplicativo iOS
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
    }
    div[data-testid="stNotification"] {
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True) # <-- CORRIGIDO: Parâmetro corrigido para evitar o TypeError

# Inicializa variáveis de estado da tela se elas não existirem
if "download_concluido" not in st.session_state:
    st.session_state.download_concluido = False
if "titulo_video" not in st.session_state:
    st.session_state.titulo_video = ""
if "dados_midia" not in st.session_state:
    st.session_state.dados_midia = None
if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = ""


# Função para resetar o estado e voltar para a tela de inputs
def voltar_ao_inicio():
    st.session_state.download_concluido = False
    st.session_state.titulo_video = ""
    st.session_state.dados_midia = None
    st.session_state.nome_arquivo = ""


# Função de download otimizada para o ambiente do Servidor Web
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
                status_text.text(f"Baixando para o servidor... {int(porcentagem * 100)}%")
        elif d['status'] == 'finished':
            progresso_bar.progress(1.0)
            status_text.text("Download concluído no servidor! Preparando arquivo...")

    ydl_opts = {
        'progress_hooks': [progress_callback],
        'outtmpl': template_destino,
        'extracted_flat': False,
        'nocheckcertificate': True,
        'quiet': True,
    }

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


# --- FLUXO DE TELAS DA INTERFACE ---

# TELA 2: Executada após o download terminar no servidor (Evita a tela preta do Safari)
if st.session_state.download_concluido:
    st.title("✅ Arquivo Pronto!")
    st.subheader(st.session_state.titulo_video)

    # Exibe o player inline correspondente ao formato
    if st.session_state.nome_arquivo.endswith(".mp4"):
        st.video(st.session_state.dados_midia)
        st.info("💡 Toque e segure sobre o vídeo acima (ou clique no ícone do player) para salvá-lo na Galeria.")
    else:
        st.audio(st.session_state.dados_midia)
        st.info("💡 Clique nos três pontinhos do player de áudio para fazer o download.")

    st.write("---")

    # BOTÃO PEDIDO: Retorna para o painel inicial limpando a memória
    if st.button("🔄 Voltar para a Tela Inicial", use_container_width=True):
        voltar_ao_inicio()
        st.rerun()

# TELA 1: Tela padrão de inputs e processamento inicial
else:
    st.title("📥 8K_DOWNLOAD")
    st.write("Insira o link abaixo para baixar vídeos ou áudios direto no seu celular.")

    url_input = st.text_input("URL do Vídeo:", placeholder="Cole o link do YouTube, Instagram, etc. aqui...")
    formato_input = st.selectbox("Selecione o formato:", ["Vídeo (MP4)", "Áudio (MP3)"])

    if st.button("Processar Download", use_container_width=True):
        if not url_input:
            st.warning("Por favor, insira uma URL válida.")
        else:
            barra = st.progress(0)
            status = st.empty()
            status.text("Iniciando conexão...")

            try:
                caminho_local, titulo = baixar_conteudo_web(url_input, formato_input, barra, status)

                # Transfere o arquivo físico para a memória do estado da sessão
                with open(caminho_local, "rb") as f:
                    st.session_state.dados_midia = f.read()

                st.session_state.titulo_video = titulo
                st.session_state.nome_arquivo = os.path.basename(caminho_local)
                st.session_state.download_concluido = True

                # Limpa o arquivo temporário físico do disco do servidor
                os.remove(caminho_local)

                # Recarrega a interface aplicando a mudança para a Tela 2
                st.rerun()

            except Exception as e:
                status.error(f"Ocorreu um erro no processamento: {e}")
