
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt="GPT-4 Analysis:")  # תיקון כאן - אין צורך ב-f"" אם אין משתנים

# הוספת שורת דוגמה לתוכן
pdf.multi_cell(0, 10, txt="This is a sample result from GPT-4 analysis.")
pdf.output("/mnt/data/forensic_app_fixed/sample_output.pdf")
