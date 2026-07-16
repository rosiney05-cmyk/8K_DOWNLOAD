import streamlit as st
import yt_dlp
import os
import io

# Configuração da página Web (Visual e responsividade)
st.set_page_config(
    page_title="Downloader Universal Web",
    page_icon="📥",
    layout="centered"
)

# Título da Interface Web
st.title("📥 8K_DOWNLOAD")
st.write("Insira o link abaixo para baixar vídeos ou áudios direto no seu celular.")


# Função de download otimizada para o ambiente do Servidor Web
def baixar_conteudo_web(url, formato, progresso_bar, status_text):
    # O arquivo será salvo temporariamente na pasta do servidor
    pasta_temp = "downloads_temp"
    os.makedirs(pasta_temp, exist_ok=True)
    template_destino = os.path.join(pasta_temp, '%(title)s.%(ext)s')

    def progress_callback(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            baixado = d.get('downloaded_bytes', 0)
            if total > 0:
                porcentagem = baixado / total
                # Atualiza a barra de progresso da página web em tempo real
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
        # Retorna o caminho exato do arquivo gerado no servidor e o título
        caminho_arquivo = ydl.prepare_filename(info)

        # Caso o formato mude a extensão real do arquivo (como em áudios), ajustamos:
        if not os.path.exists(caminho_arquivo):
            nome_base, _ = os.path.splitext(caminho_arquivo)
            for f in os.listdir(pasta_temp):
                if f.startswith(os.path.basename(nome_base)):
                    caminho_arquivo = os.path.join(pasta_temp, f)
                    break

        return caminho_arquivo, info.get('title', 'video')


# --- COMPONENTES DA INTERFACE WEB ---
url_input = st.text_input("URL do Vídeo:", placeholder="Cole o link do YouTube, Instagram, etc. aqui...")
formato_input = st.selectbox("Selecione o formato:", ["Vídeo (MP4)", "Áudio (MP3)"])

if st.button("Processar Download", use_container_width=True):
    if not url_input:
        st.warning("Por favor, insira uma URL válida.")
    else:
        # Cria os elementos visuais de carregamento
        barra = st.progress(0)
        status = st.empty()
        status.text("Iniciando conexão...")

        try:
            # Baixa o arquivo para o servidor onde o Python está rodando
            caminho_local, titulo = baixar_conteudo_web(url_input, formato_input, barra, status)

            # Carrega o arquivo na memória para disponibilizar o botão de download no iPhone
            with open(caminho_local, "rb") as f:
                dados_arquivo = f.read()

            status.success(f"Pronto! Próximo passo abaixo: {titulo}")

            # Botão oficial do navegador para transferir do servidor para a galeria/arquivos do iPhone
            st.download_button(
                label="➡️ CLIQUE AQUI PARA SALVAR O ARQUIVO ⬅️",
                data=dados_arquivo,
                file_name=os.path.basename(caminho_local),
                mime="video/mp4" if formato_input == "Vídeo (MP4)" else "audio/mp3",
                use_container_width=True
            )

            # Limpa o arquivo temporário do servidor após o carregamento
            os.remove(caminho_local)

        except Exception as e:
            status.error(f"Ocorreu um erro no processamento: {e}")
