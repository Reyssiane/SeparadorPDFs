
import streamlit as st
import pandas as pd
import shutil
from pathlib import Path
import tempfile

st.set_page_config(page_title="Separador de PDFs", layout="centered")
st.title("📁 Separador de PDFs por Lote")
st.write("Selecione a planilha, a pasta com os PDFs e a pasta onde deseja salvar os arquivos separados.")

xlsx_file = st.file_uploader("📄 Envie a planilha Excel", type=["xlsx"])
pdf_folder = st.directory_picker("📁 Selecione a pasta com os PDFs")
output_folder = st.directory_picker("📁 Selecione a pasta de destino")

if xlsx_file and pdf_folder and output_folder:
    df = pd.read_excel(xlsx_file, sheet_name=0)
    missing_pdfs = []

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)

        for _, row in df.iterrows():
            nome_pdf = str(row['NFSe']) + ".pdf"
            lote_valor = str(row['Lote']).strip()

            if lote_valor.replace(" ", "").upper().startswith("LOTE"):
                lote = lote_valor
            elif lote_valor.isdigit():
                lote = f"Lote {int(lote_valor):02d}"
            else:
                lote = f"Lote {lote_valor}"

            lote_path = temp_dir / lote
            lote_path.mkdir(exist_ok=True)

            origem = Path(pdf_folder) / nome_pdf
            destino = lote_path / nome_pdf

            if origem.exists():
                shutil.copy2(origem, destino)
            else:
                missing_pdfs.append(nome_pdf)

        for pasta in temp_dir.iterdir():
            destino_final = Path(output_folder) / pasta.name
            destino_final.mkdir(exist_ok=True)
            for arquivo in pasta.iterdir():
                shutil.copy2(arquivo, destino_final / arquivo.name)

    st.success("✅ PDFs separados com sucesso!")
    if missing_pdfs:
        st.error("❌ NFS-e não encontradas na pasta:")
        for nf in missing_pdfs:
            st.write(f"- {nf}")
