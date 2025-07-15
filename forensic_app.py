import streamlit as st
from PIL import Image
import numpy as np
import io
import base64
import openai

st.set_page_config(page_title="זיהוי פורנזי לתמונות", layout="centered")
st.title("🔍 אפליקציה פורנזית לזיהוי תמונות היסטוריות בשחור-לבן")

uploaded_file = st.file_uploader("📤 העלה תמונה לניתוח", type=["jpg", "jpeg", "png"])

def error_level_analysis(image):
    buf = io.BytesIO()
    image.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    resaved = Image.open(buf)
    ela_image = Image.fromarray(
        np.abs(np.array(image, dtype=np.int16) - np.array(resaved, dtype=np.int16)).astype(np.uint8)
    )
    return ela_image

def analyze_with_openai_vision(image_pil):
    if "OPENAI_API_KEY" not in st.secrets:
        st.warning("🔐 לא הוגדר מפתח API של OpenAI בקובץ secrets.toml")
        return None

    openai.api_key = st.secrets["OPENAI_API_KEY"]
    buffered = io.BytesIO()
    image_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "אתה מומחה לזיהוי זיופים בתמונות היסטוריות."},
            {
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}],
            },
        ],
        max_tokens=600,
    )
    return response["choices"][0]["message"]["content"]

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="📷 התמונה שהועלתה", use_column_width=True)

    st.subheader("📊 ניתוח בסיסי")
    st.write(f"✅ פורמט: {image.format or 'N/A'}")
    st.write(f"📐 גודל: {image.size[0]} x {image.size[1]}")
    st.write(f"🎨 ערוצים: {len(image.getbands())}")

    st.subheader("🔍 ניתוח ELA (Error Level Analysis)")
    ela = error_level_analysis(image)
    st.image(ela, caption="ELA - ניתוח רמות שגיאה", use_column_width=True)

    st.subheader("🧠 ניתוח מבוסס GPT-4 Vision")
    gpt_result = analyze_with_openai_vision(image)
    if gpt_result:
        st.success("תוצאות הניתוח מבוסס GPT:")
        st.markdown(gpt_result)

