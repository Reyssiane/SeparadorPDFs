
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import shutil

st.set_page_config(page_title="Separador de PDFs", page_icon="📂")
st.title("📂 Separador de PDFs por Lote")
"""
    <div style='background-color:#fff3cd; padding:10px; border-radius:5px; border:1px solid #ffeeba; margin-bottom:20px;'>
        <strong>📌 Como usar:</strong><br>
        1. Faça o upload da planilha (.xlsx) contendo os dados das NFS-e.<br>
        2. Selecione os arquivos PDF correspondentes.<br>
        3. O sistema criará pastas por Lote com os PDFs separados.<br>
        4. NFS-e que estiverem na planilha mas não tiverem PDF serão listadas.<br>
    </div>
    """,
excel_file = st.file_uploader("📄 Selecione a planilha Excel (.xlsx)", type=["xlsx"])
pdf_files = st.file_uploader("📁 Selecione os arquivos PDF (segure Ctrl para múltiplos)", type=["pdf"], accept_multiple_files=True)

if excel_file and pdf_files:
    df = pd.read_excel(excel_file, sheet_name=0)
    missing_files = []
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)
        
        for _, row in df.iterrows():
            nome_pdf = str(row['NFSe']) + ".pdf"
            lote_valor = str(row['Lote']).strip()

            if lote_valor.isdigit():
                lote = f"Lote {int(lote_valor):02d}"
            else:
                lote = f"Lote {lote_valor}"

            lote_path = temp_dir / lote
            lote_path.mkdir(exist_ok=True)

            matched = [f for f in pdf_files if f.name == nome_pdf]

            if matched:
                file_path = lote_path / nome_pdf
                with open(file_path, "wb") as out_file:
                    out_file.write(matched[0].getbuffer())
            else:
                missing_files.append(nome_pdf)

        # Criar ZIP com os arquivos separados
        zip_path = temp_dir / "pdfs_separados.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', temp_dir)
        
        st.success("✅ PDFs separados com sucesso!")
        with open(zip_path, "rb") as f:
            st.download_button("📦 Baixar arquivos organizados (.zip)", f, file_name="pdfs_separados.zip")

        if missing_files:
            st.warning("⚠️ Os seguintes arquivos PDF não foram encontrados:")
            for file in missing_files:
                st.text(f"• {file}")
