
# קוד חלקי בלבד לשם הדגמה של תיקון השגיאה בשורת f-string
# חלק מלא אמור לכלול את כל הפונקציות הקודמות

# בתוך הפונקציה generate_pdf_report(...):

    if gpt_analysis:
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"ניתוח תוכן GPT:\n{gpt_analysis}")
    return pdf.output(dest='S').encode('latin1')
