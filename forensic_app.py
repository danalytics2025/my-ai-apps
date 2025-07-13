
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import piexif
import os

# =========================== Helper Functions ============================

def extract_metadata(image: Image.Image):
    try:
        exif_data = piexif.load(image.info['exif'])
        exif_dict = {tag: str(exif_data['0th'].get(tag, b'')).strip() for tag in [
            piexif.ImageIFD.DateTime,
            piexif.ImageIFD.Make,
            piexif.ImageIFD.Model,
            piexif.ImageIFD.Software
        ]}
        suspicious = any(keyword in str(exif_dict).lower() for keyword in ['photoshop', 'ai', 'dalle', 'diffusion'])
        score = 20 if not suspicious else 10
    except Exception:
        exif_dict = {"Metadata": "None"}
        score = 5
    return exif_dict, score

def error_level_analysis(image: Image.Image):
    image.save("temp.jpg", "JPEG", quality=95)
    original = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    recompressed = cv2.imread("temp.jpg")
    ela_image = cv2.absdiff(original, recompressed)
    ela_score = 25 - int(np.std(ela_image) / 3)
    ela_score = max(0, min(25, ela_score))
    return ela_image, ela_score

def analyze_noise(image: Image.Image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = np.var(laplacian)
    score = 20 if 100 < variance < 1000 else 10
    return score, variance

def pixel_anomaly_detection(image: Image.Image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    kernel = np.ones((5, 5), np.float32) / 25
    smoothed = cv2.filter2D(gray, -1, kernel)
    diff = cv2.absdiff(gray, smoothed)
    std_dev = np.std(diff)
    score = 20 if std_dev < 20 else 10
    return score, std_dev

def stylistic_symmetry_check(image: Image.Image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    symmetry = np.mean(np.abs(gray - np.fliplr(gray)))
    score = 15 if symmetry > 10 else 10
    return score, symmetry

# =============================== Streamlit App ===============================

st.title("🔍 מערכת פורנזית לזיהוי תמונות מזויפות (ללא מודל ML)")

uploaded_file = st.file_uploader("העלה תמונה לבדיקה", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="התמונה שהועלתה", use_column_width=True)

    st.subheader("📊 ניתוח אלגוריתמי")

    metadata, score_meta = extract_metadata(image)
    st.markdown("**🗂️ מטא־דאטה:**")
    st.json(metadata)

    ela_image, score_ela = error_level_analysis(image)
    st.image(ela_image, caption="🎞️ ELA - ניתוח רמות שגיאה")

    score_noise, noise_val = analyze_noise(image)
    score_pixel, pixel_dev = pixel_anomaly_detection(image)
    score_style, sym_val = stylistic_symmetry_check(image)

    st.write(f"**ציון מטא־דאטה:** {score_meta}/20")
    st.write(f"**ציון ELA:** {score_ela}/25")
    st.write(f"**ציון רעש דיגיטלי:** {score_noise}/20 (שונות: {noise_val:.2f})")
    st.write(f"**ציון חריגות פיקסלים:** {score_pixel}/20 (סטיית תקן: {pixel_dev:.2f})")
    st.write(f"**ציון סימטריה חזותית:** {score_style}/15 (סטיית סימטריה: {sym_val:.2f})")

    final_score = score_meta + score_ela + score_noise + score_pixel + score_style
    st.markdown(f"### ✅ ציון סופי: {final_score}/100")

    if final_score >= 90:
        st.success("התמונה אותנטית מאוד")
    elif final_score >= 70:
        st.info("התמונה נראית אותנטית")
    elif final_score >= 50:
        st.warning("⚠️ התמונה חשודה")
    else:
        st.error("❌ ייתכן שמדובר בזיוף")

    os.remove("temp.jpg")
