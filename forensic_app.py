
# Forensic Web App for Authenticity Detection of Historical Black-and-White Photos
# Streamlit-based with metadata, graphical forensics, and GPT-4 Vision

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

st.set_page_config(page_title="Forensic Analysis of Historical Photos", layout="centered")
st.title("🧠 GPT-4 Vision Based Analysis")

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
        st.warning(f"⚠️ Could not extract Metadata: {str(e)}")
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
            {
                "role": "system",
                "content": "You are a forensic expert. Analyze the uploaded photo and describe if it seems manipulated, AI-generated, or authentic."
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
    return response['choices'][0]['message']['content']


def generate_pdf_report(filename, metadata, score, gpt_analysis=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Forensic Analysis Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Filename: {filename}", ln=True)
    for k, v in metadata.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Authenticity Score: {score}/100", ln=True)
    result = "🟢 Highly Authentic" if score > 85 else "🟡 Some Suspicion" if score > 65 else "🔴 Possible Forgery"
    pdf.cell(200, 10, txt=f"Classification: {result}", ln=True)
    if gpt_analysis:
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"GPT Content Analysis:
{gpt_analysis}")
    return pdf.output(dest='S').encode('latin1')
