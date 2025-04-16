import streamlit as st
import pandas as pd
import zipfile
import os
from pathlib import Path
import shutil

st.title("Separador de PDFs por Lote")

st.write("Faça upload da planilha (Excel) e dos arquivos PDF que deseja organizar.")

planilha = st.file_uploader("📄 Upload da planilha (.xlsx)", type=["xlsx"])
pdfs = st.file_uploader("📎 Upload dos arquivos PDF", type=["pdf"], accept_multiple_files=True)

if planilha and pdfs:
    df = pd.read_excel(planilha, sheet_name=0)
    
    if not {'NFSe', 'Lote'}.issubset(df.columns):
        st.error("A planilha precisa ter as colunas 'NFSe' e 'Lote'.")
    else:
        temp_dir = Path("saida_pdfs")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        for _, row in df.iterrows():
            nome_pdf = str(row['NFSe']) + ".pdf"
            lote = f"Lote {int(row['Lote']):02d}"
            lote_path = temp_dir / lote
            lote_path.mkdir(exist_ok=True)

            for arquivo in pdfs:
                if arquivo.name == nome_pdf:
                    with open(lote_path / nome_pdf, "wb") as f:
                        f.write(arquivo.getbuffer())
        
        # Compacta os arquivos
        zip_path = "arquivos_separados.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for foldername, subfolders, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    zipf.write(file_path, os.path.relpath(file_path, temp_dir))

        with open(zip_path, "rb") as f:
            st.download_button("📦 Baixar pastas organizadas (.zip)", f, file_name="arquivos_separados.zip")

        shutil.rmtree(temp_dir)
