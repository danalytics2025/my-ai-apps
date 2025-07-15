import streamlit as st
import os
import numpy as np
from PIL import Image, ExifTags
import cv2
import matplotlib.pyplot as plt
import io
import base64
import openai
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Forensic Image Analysis", layout="centered")
st.title("🔍 Forensic Analysis of Historical B&W Images")

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
        st.warning(f"⚠️ Metadata extraction failed: {str(e)}")
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
    api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_key = api_key
    buffered = io.BytesIO()
    image_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a forensic image expert. Analyze this historical photo for signs of manipulation, AI generation or photo editing."},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}
        ],
        max_tokens=600
    )
    return response['choices'][0]['message']['content']

def generate_pdf_report(filename, metadata, score, gpt_analysis=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Forensic Image Analysis Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"File Name: {filename}", ln=True)
    for k, v in metadata.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Authenticity Score: {score}/100", ln=True)
    result = "🟢 Highly Authentic" if score > 85 else "🟡 Possible Manipulation" if score > 65 else "🔴 Likely Fake"
    pdf.cell(200, 10, txt=f"Classification: {result}", ln=True)
    if gpt_analysis:
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"GPT-4 Analysis:
{gpt_analysis}")
    return pdf.output(dest='S').encode('latin1')

uploaded_file = st.file_uploader("📤 Upload an image for analysis", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    filename = uploaded_file.name
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.subheader("🧾 Metadata")
    metadata = extract_metadata(image)
    for k, v in metadata.items():
        st.write(f"**{k}:** {v}")

    if all(v == "N/A" for v in metadata.values()):
        st.info("No EXIF metadata found. Continuing with visual analysis only.")

    st.subheader("🧪 Forensic Visual Analysis")
    ela_image = error_level_analysis(image)
    noise_map = compute_noise_map(image)
    anomaly_map = detect_pixel_anomalies(image)

    show_image("ELA - Error Level Analysis", ela_image)
    show_image("Noise Map", noise_map, cmap='gray')
    show_image("Pixel Anomalies", anomaly_map, cmap='hot')

    score = calculate_score(metadata, np.array(ela_image), noise_map, anomaly_map)
    st.subheader("📊 Authenticity Score")
    st.metric(label="Score", value=f"{score}/100")

    if score > 85:
        st.success("✅ Highly authentic image.")
    elif score > 65:
        st.warning("⚠️ Possible manipulation detected.")
    else:
        st.error("❌ High likelihood of being fake or AI-generated.")

    gpt_analysis = None
    st.subheader("🧠 GPT-4 Vision Analysis")
    if "OPENAI_API_KEY" in st.secrets:
        with st.spinner("Analyzing with GPT-4 Vision..."):
            gpt_analysis = analyze_with_openai_vision(image)
            st.markdown("**GPT-4 Result:**")
            st.markdown(gpt_analysis)

    st.session_state.history.append({
        "file": filename,
        "score": score,
        "result": "Authentic" if score > 85 else "Suspicious" if score > 65 else "Fake",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    st.download_button(
        label="📄 Download PDF Report",
        data=generate_pdf_report(filename, metadata, score, gpt_analysis),
        file_name=f"forensic_report_{filename.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

if st.session_state.history:
    st.subheader("🗂️ Recent Analyses")
    for item in reversed(st.session_state.history[-5:]):
        st.write(f"📁 **{item['file']}** | Score: {item['score']} | Result: {item['result']} | 🕓 {item['datetime']}")