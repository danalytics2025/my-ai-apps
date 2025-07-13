
# 🕵️ Forensic Image Authenticity Checker (No ML)

This Streamlit app performs forensic analysis of uploaded images to help detect possible tampering or AI generation — using only lightweight visual algorithms (no machine learning).

## 🔍 Features

- **ELA (Error Level Analysis)**: Detects inconsistencies in compression levels.
- **Digital Noise Analysis**: Detects unnatural texture consistency.
- **Pixel Anomaly Detection**: Flags odd smoothing or blurring patterns.
- **Symmetry Check**: Flags excessive visual symmetry (common in AI).
- **Metadata Inspection**: Extracts EXIF and detects editing software.

## 🧠 No ML Required

This app is ideal for environments like [streamlit.app](https://streamlit.app) with strict size or dependency limits. No external models or cloud inference needed.

## 🚀 How to Deploy

1. Upload to a GitHub repo.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and connect your repo.
3. Set the main file to `forensic_app.py`.
4. Click **Deploy** and start analyzing images.

## Example Use Cases
- Journalistic photo verification
- Forensic image analysis
- Educational demos on image manipulation
