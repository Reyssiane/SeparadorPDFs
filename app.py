
import streamlit as st
import pandas as pd
import zipfile
import tempfile
from pathlib import Path

st.set_page_config(page_title="Separador de PDFs por Lote", layout="centered")
st.title("📂 Separador de PDFs por Lote")
st.write("Suba sua planilha e os PDFs, e faremos a separação por pastas!")

# Upload da planilha
planilha = st.file_uploader("📊 Envie a planilha Excel com as colunas 'NFSe' e 'Lote':", type=[".xlsx"])

# Upload dos PDFs
pdfs = st.file_uploader("📄 Envie os arquivos PDF:", type=[".pdf"], accept_multiple_files=True)

if planilha and pdfs:
    df = pd.read_excel(planilha)

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)

        for _, row in df.iterrows():
            nome_pdf = str(row['NFSe']).strip() + ".pdf"
            lote = f"Lote {str(row['Lote']).strip()}"
            lote_path = temp_dir / lote
            lote_path.mkdir(exist_ok=True)

            for arquivo in pdfs:
                if arquivo.name.strip().lower() == nome_pdf.strip().lower():
                    output_path = lote_path / arquivo.name
                    with open(output_path, "wb") as f:
                        f.write(arquivo.read())

        # Criação do ZIP
        zip_path = temp_dir / "arquivos_separados.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for pasta in temp_dir.glob("Lote*/**/*.pdf"):
                zipf.write(pasta, pasta.relative_to(temp_dir))

        with open(zip_path, "rb") as f:
            st.success("✅ Separação finalizada! Baixe abaixo:")
            st.download_button("📥 Baixar ZIP com pastas", f, file_name="pdfs_separados.zip")
