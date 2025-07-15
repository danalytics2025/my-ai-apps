from fpdf import FPDF

def generate_pdf_report(filename, metadata, score, gpt_analysis=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="מסמך ניתוח פורנזי לתמונה", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"שם קובץ: {filename}", ln=True)
    for k, v in metadata.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"ציון אמינות: {score}/100", ln=True)
    result = "🟢 אותנטית מאוד" if score > 85 else "🟡 חשד מסוים" if score > 65 else "🔴 ייתכן זיוף"
    pdf.cell(200, 10, txt=f"סיווג: {result}", ln=True)
    if gpt_analysis:
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"ניתוח תוכן GPT:
{gpt_analysis}")
    return pdf.output(dest='S').encode('latin1')
