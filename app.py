
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import zipfile

st.set_page_config(page_title="Separador de PDFs por Lote", layout="centered")
st.title("📂 Separador de PDFs por Lote")

st.markdown("""
<div style='padding: 15px; background-color: #f0f2f6; border-left: 5px solid #2c7be5; border-radius: 8px; margin-bottom: 20px;'>
    <h4 style='margin-top: 0;'>📋 Instruções:</h4>
    <ul>
        <li>Envie sua planilha Excel contendo as colunas <b>NFSe</b> e <b>Lote</b>.</li>
        <li>Selecione os arquivos PDF correspondentes (pode selecionar vários).</li>
        <li>Os PDFs serão separados automaticamente em pastas por lote.</li>
        <li>Se algum arquivo estiver ausente, ele será listado no final.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Upload da planilha
planilha = st.file_uploader("📄 Envie a planilha Excel (.xlsx)", type=["xlsx"])

# Upload dos arquivos PDF (múltiplos)
pdf_files = st.file_uploader("📂 Selecione os arquivos PDF (vários arquivos)", type=["pdf"], accept_multiple_files=True)

if planilha and pdf_files:
    df = pd.read_excel(planilha)
    faltando = []

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)

        for _, row in df.iterrows():
            nome_pdf = str(row["NFSe"]).strip() + ".pdf"
            lote = str(row["Lote"]).strip()
            lote_path = temp_dir / f"Lote {lote}"
            lote_path.mkdir(parents=True, exist_ok=True)

            encontrado = False
            for pdf in pdf_files:
                if pdf.name.strip().lower() == nome_pdf.lower():
                    with open(lote_path / nome_pdf, "wb") as f:
                        f.write(pdf.read())
                    encontrado = True
                    break

            if not encontrado:
                faltando.append(nome_pdf)

        zip_path = temp_dir / "pdfs_separados.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in temp_dir.rglob("*.pdf"):
                zipf.write(file, file.relative_to(temp_dir))

        with open(zip_path, "rb") as f:
            st.success("✅ Separação concluída! Baixe os arquivos organizados abaixo.")
            st.download_button("📦 Baixar arquivos separados (.zip)", f, file_name="pdfs_separados.zip")

        if faltando:
            st.warning(f"⚠️ {len(faltando)} arquivo(s) da planilha não foram encontrados entre os PDFs enviados:")
            for nome in faltando:
                st.text(f"• {nome}")
