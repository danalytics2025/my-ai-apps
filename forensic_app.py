
# אפליקציה פורנזית מבוססת Web לזיהוי אותנטיות של תמונות היסטוריות בשחור-לבן
import streamlit as st
import numpy as np
from PIL import Image, ExifTags
import cv2
import matplotlib.pyplot as plt
import io
import base64
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="זיהוי פורנזי לתמונות היסטוריות", layout="centered")
st.title("🔍 אפליקציה פורנזית לזיהוי תמונות היסטוריות בשחור-לבן")

if 'history' not in st.session_state:
    st.session_state.history = []

def extract_metadata(image):
    exif_dict = {}
    try:
        if hasattr(image, 'getexif'):
            exif_data = image.getexif()
            if exif_data and hasattr(exif_data, 'items'):
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_dict[tag] = value
    except Exception as e:
        st.warning(f"⚠️ לא ניתן היה לחלץ Metadata: {str(e)}")
    return {
        "Make": exif_dict.get("Make", "N/A"),
        "Model": exif_dict.get("Model", "N/A"),
        "Software": exif_dict.get("Software", "N/A"),
        "DateTime": exif_dict.get("DateTime", "N/A"),
    }

def error_level_analysis(image):
    buf = io.BytesIO()
    image.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    resaved = Image.open(buf)
    ela_image = Image.fromarray(np.abs(np.array(image, dtype=np.int16) - np.array(resaved, dtype=np.int16)).astype(np.uint8))
    return ela_image

def compute_noise_map(image):
    gray = image.convert('L')
    image_np = np.array(gray, dtype=np.float32)
    blurred = cv2.GaussianBlur(image_np, (5, 5), 0)
    noise_map = np.abs(image_np - blurred)
    return noise_map

def detect_pixel_anomalies(image, window_size=7):
    gray = image.convert('L')
    img_np = np.array(gray, dtype=np.float32)
    local_mean = cv2.blur(img_np, (window_size, window_size))
    squared_diff = (img_np - local_mean) ** 2
    local_var = cv2.blur(squared_diff, (window_size, window_size))
    local_std = np.sqrt(local_var)
    return local_std

def show_image(title, array, cmap=None):
    fig, ax = plt.subplots()
    ax.imshow(array, cmap=cmap)
    ax.set_title(title)
    ax.axis('off')
    st.pyplot(fig)

def calculate_score(metadata, ela_img, noise_map, anomaly_map):
    score = 100
    if metadata['Software'] != 'N/A' and any(x in metadata['Software'].lower() for x in ['photoshop', 'ai', 'dalle', 'diffusion']):
        score -= 30
    if metadata['DateTime'] != 'N/A' and '20' in metadata['DateTime'][:2]:
        score -= 20
    if np.std(ela_img) > 40:
        score -= 15
    if np.mean(noise_map) < 2:
        score -= 15
    if np.max(anomaly_map) > 50:
        score -= 20
    return max(0, score)

def analyze_with_openai_vision(image_pil):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    buffered = io.BytesIO()
    image_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "אתה מומחה לזיהוי פורנזי של תמונות היסטוריות. נתח את התמונה וכתוב אם יש סימנים לזיוף, AI, או עיבוד דיגיטלי מתקדם."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}"
                        }
                    }
                ]
            }
        ],
        max_tokens=600
    )
    return response.choices[0].message.content

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
        pdf.multi_cell(0, 10, txt=f"GPT ניתוח תוכן:
{gpt_analysis}")
    return pdf.output(dest='S').encode('latin1')

uploaded_file = st.file_uploader("📤 העלה תמונה לניתוח", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    filename = uploaded_file.name
    st.image(image, caption="📷 התמונה שהועלתה", use_column_width=True)
    st.subheader("🧾 Metadata (מטא-דאטה)")
    metadata = extract_metadata(image)
    for k, v in metadata.items():
        st.write(f"**{k}:** {v}")
    if all(v == "N/A" for v in metadata.values()):
        st.info("📭 לא נמצאו נתוני Metadata – המשך הניתוח יתבצע לפי המאפיינים הגרפיים בלבד.")
    st.subheader("🧪 ניתוחים פורנזיים")
    ela_image = error_level_analysis(image)
    noise_map = compute_noise_map(image)
    anomaly_map = detect_pixel_anomalies(image)
    show_image("ELA - ניתוח רמות שגיאה", ela_image)
    show_image("Noise Map - מפת רעש", noise_map, cmap='gray')
    show_image("Pixel Anomalies - חריגות פיקסל", anomaly_map, cmap='hot')
    score = calculate_score(metadata, np.array(ela_image), noise_map, anomaly_map)
    st.subheader("📊 ציון אותנטיות כולל")
    st.metric(label="Authenticity Score", value=f"{score}/100")
    if score > 85:
        st.success("✅ התמונה נראית אותנטית מאוד")
    elif score > 65:
        st.warning("⚠️ קיימת אפשרות למניפולציה – יש לבחון לעומק")
    else:
        st.error("❌ חשד גבוה לתמונה מזויפת או שנוצרה על ידי AI")
    gpt_analysis = None
    st.subheader("🧠 ניתוח מבוסס GPT-4 Vision")
    if "OPENAI_API_KEY" in st.secrets:
        with st.spinner("🔎 מריץ ניתוח GPT-4 Vision..."):
            gpt_analysis = analyze_with_openai_vision(image)
            st.markdown(f"**תוצאות הניתוח:**

{gpt_analysis}")
    st.session_state.history.append({
        "file": filename,
        "score": score,
        "result": "אותנטית" if score > 85 else "חשודה" if score > 65 else "מזויפת",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    st.download_button(
        label="📄 הורד מסמך PDF",
        data=generate_pdf_report(filename, metadata, score, gpt_analysis),
        file_name=f"forensic_report_{filename.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

if st.session_state.history:
    st.subheader("🗂️ היסטוריית ניתוחים קודמים")
    for item in reversed(st.session_state.history[-5:]):
        st.write(f"📁 **{item['file']}** | ציון: {item['score']} | סיווג: {item['result']} | 🕓 {item['datetime']}")
