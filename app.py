import streamlit as st
import pandas as pd
import zipfile
from pathlib import Path
import tempfile

st.set_page_config(page_title="Separador de PDFs", layout="centered")

# Mensagem informativa no topo
with st.container():
    st.markdown(
        '''<div style='padding: 20px; background-color: #f0f2f6; border-left: 5px solid #2c7be5; border-radius: 5px; margin-bottom: 20px;'>
            <h4 style='margin: 0;'>📄 Como usar:</h4>
            <ul style='margin-top: 10px; padding-left: 20px;'>
                <li>Escolha a planilha que possui as colunas <b>NFSe</b> e <b>Lote</b>.</li>
                <li>Selecione a pasta onde estão os arquivos PDF.</li>
                <li>Os PDFs serão separados automaticamente por pastas de acordo com o lote.</li>
                <li>Se houver notas na planilha sem o PDF correspondente, elas serão exibidas no final.</li>
            </ul>
        </div>''',
        unsafe_allow_html=True
    )

# Upload da planilha
planilha = st.file_uploader("📋 Envie a planilha (Excel):", type=["xlsx"])

# Upload da pasta zip com os PDFs
pdf_zip = st.file_uploader("🗂 Envie um arquivo .zip com os PDFs:", type=["zip"])

if planilha and pdf_zip:
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # Salvar planilha e ler
        planilha_path = temp_dir / "planilha.xlsx"
        with open(planilha_path, "wb") as f:
            f.write(planilha.read())

        df = pd.read_excel(planilha_path)

        # Salvar e extrair os PDFs
        zip_path = temp_dir / "pdfs.zip"
        with open(zip_path, "wb") as f:
            f.write(pdf_zip.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir / "pdfs")

        pdf_folder = temp_dir / "pdfs"
        arquivos_pdf = {f.name for f in pdf_folder.glob("*.pdf")}

        # Cria subpastas por lote e move arquivos
        output_zip_path = temp_dir / "pdfs_separados.zip"
        faltando = []
        with zipfile.ZipFile(output_zip_path, "w") as saida_zip:
            for _, row in df.iterrows():
                nome_pdf = str(row["NFSe"]) + ".pdf"
                lote = str(row["Lote"]).strip()
                lote_path = Path(f"Lote {lote}")

                pdf_path = pdf_folder / nome_pdf
                if pdf_path.exists():
                    saida_zip.write(pdf_path, arcname=lote_path / nome_pdf)
                else:
                    faltando.append(nome_pdf)

        st.success("✅ PDFs separados por lote!")
        st.download_button("📦 Baixar arquivos separados", data=open(output_zip_path, "rb"), file_name="pdfs_separados.zip")

        # Mostrar arquivos ausentes
        if faltando:
            st.warning("⚠️ Alguns arquivos da planilha não foram encontrados na pasta de PDFs:")
            for nome in faltando:
                st.text(f"• {nome}")