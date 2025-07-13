
import streamlit as st
from PIL import Image, ImageChops
import numpy as np
import os

# =========================== Helper Functions ============================

def extract_metadata(image: Image.Image):
    try:
        exif_data = image._getexif()
        if exif_data is not None:
            exif = {str(k): str(v) for k, v in exif_data.items()}
            suspicious = any(keyword in str(exif).lower() for keyword in ['photoshop', 'ai', 'dalle', 'diffusion'])
            score = 20 if not suspicious else 10
        else:
            exif = {"Metadata": "None"}
            score = 5
    except Exception:
        exif = {"Metadata": "Unavailable"}
        score = 5
    return exif, score

def error_level_analysis(image: Image.Image):
    image.save("temp.jpg", "JPEG", quality=90)
    recompressed = Image.open("temp.jpg").convert("RGB")
    ela_image = ImageChops.difference(image, recompressed)
    ela_np = np.array(ela_image)
    ela_score = 25 - int(np.std(ela_np) / 3)
    ela_score = max(0, min(25, ela_score))
    return ela_image, ela_score

def analyze_noise(image: Image.Image):
    gray = image.convert("L")
    img_np = np.array(gray, dtype=np.float32)
    sobel_x = np.abs(np.diff(img_np, axis=1))
    sobel_y = np.abs(np.diff(img_np, axis=0))
    gradient = np.mean(sobel_x) + np.mean(sobel_y)
    score = 20 if 5 < gradient < 50 else 10
    return score, gradient

def pixel_anomaly_detection(image: Image.Image):
    gray = image.convert("L")
    img_np = np.array(gray, dtype=np.float32)
    smoothed = np.array(Image.fromarray(img_np).filter(Image.Filter.BoxBlur(2)))
    diff = np.abs(img_np - smoothed)
    std_dev = np.std(diff)
    score = 20 if std_dev < 20 else 10
    return score, std_dev

def stylistic_symmetry_check(image: Image.Image):
    gray = image.convert("L")
    img_np = np.array(gray)
    flipped = np.fliplr(img_np)
    symmetry = np.mean(np.abs(img_np - flipped))
    score = 15 if symmetry > 10 else 10
    return score, symmetry

# =============================== Streamlit App ===============================

st.title("🔍 מערכת פורנזית לזיהוי תמונות מזויפות (ללא מודל ML)")
st.image("logo.png", width=200)

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
    st.write(f"**ציון רעש דיגיטלי:** {score_noise}/20 (gradient: {noise_val:.2f})")
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
