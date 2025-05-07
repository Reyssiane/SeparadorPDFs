
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import zipfile
import io

st.set_page_config(page_title="Separador de PDFs por Lote", layout="centered")

st.markdown("""
<style>
.stDeployButton {display: none !important;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📂 Separador de PDFs por Lote")

st.markdown("""
<div style='padding: 15px; background-color: #f0f2f6; border-left: 5px solid #2c7be5; border-radius: 8px; margin-bottom: 20px;'>
    <h4 style='margin-top: 0;'>📋 Instruções:</h4>
    <ul>
        <li>Envie sua planilha Excel com as colunas <b>NFSe</b> e <b>Lote</b>.</li>
        <li>Selecione os arquivos PDF (pode escolher vários ao mesmo tempo).</li>
        <li>O sistema criará um arquivo .zip com os PDFs organizados em pastas.</li>
        <li>PDFs ausentes serão exibidos em uma tabela ao final, com seus respectivos lotes.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

planilha = st.file_uploader("📄 Envie a planilha Excel (.xlsx)", type=["xlsx"])
pdf_files = st.file_uploader("📂 Selecione os arquivos PDF", type=["pdf"], accept_multiple_files=True)

if planilha and pdf_files:
    try:
        df = pd.read_excel(planilha)
        faltando = []
        zip_buffer = io.BytesIO()
        pdf_dict = {pdf.name.lower(): pdf for pdf in pdf_files}
        total = len(df)
        progresso = st.progress(0, text="Iniciando separação dos arquivos...")

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            lotes = df["Lote"].astype(str).str.strip().unique()
            for lote in lotes:
                lote_folder = f"Lote {lote}"
                zipf.writestr(f"{lote_folder}/.keep", b"")

            for i, (_, row) in enumerate(df.iterrows(), start=1):
                nome_pdf = str(row["NFSe"]).strip() + ".pdf"
                lote = str(row["Lote"]).strip()
                lote_folder = f"Lote {lote}"

                pdf = pdf_dict.get(nome_pdf.lower())
                if pdf:
                    zipf.writestr(f"{lote_folder}/{nome_pdf}", pdf.read())
                else:
                    faltando.append({"Lote": lote, "NFSe": nome_pdf})

                progresso.progress(i / total, text=f"Processando arquivo {i} de {total}...")

        progresso.empty()
        st.success("✅ PDFs separados com sucesso!")
        st.download_button("📦 Baixar arquivos separados (.zip)", data=zip_buffer.getvalue(), file_name="pdfs_separados.zip")

        if faltando:
            st.warning(f"⚠️ {len(faltando)} arquivo(s) da planilha não foram encontrados entre os PDFs enviados:")
            st.dataframe(pd.DataFrame(faltando))
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
