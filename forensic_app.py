
import streamlit as st
from fpdf import FPDF

st.title("📄 ניתוח GPT-4 Vision")

gpt_analysis = "זוהי דוגמת טקסט מניתוח GPT-4..."

if gpt_analysis:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="GPT ניתוח התוכן:")
    pdf.multi_cell(0, 10, txt=gpt_analysis)
    pdf_output = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="📄 הורד מסמך PDF",
        data=pdf_output,
        file_name="gpt_analysis.pdf",
        mime="application/pdf"
    )
