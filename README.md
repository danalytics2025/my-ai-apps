# 🧠 Forensic AI Image Analyzer (Black-and-White Historical Photo Validator)

A Streamlit-based forensic web app to detect manipulations, deepfakes, or AI-generated black-and-white historical images.

## 🔍 Features

- Extracts and analyzes image metadata (EXIF)
- Performs Error Level Analysis (ELA)
- Generates noise and pixel anomaly maps
- Calculates an authenticity score
- Optional GPT-4 Vision-based analysis
- Generates downloadable PDF reports in English
- Session history tracking

## 🚀 Installation

```bash
git clone https://github.com/your-username/forensic-ai-analyzer.git
cd forensic-ai-analyzer
pip install -r requirements.txt
```

## 🧪 Running the App

```bash
streamlit run forensic_app.py
```

## 🔐 API Key Setup

Create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

This key is used for GPT-4 Vision analysis.

## 🖼️ Uploading Files

The app supports `.jpg`, `.jpeg`, and `.png` files.

## 📄 Output

Each uploaded image is analyzed and a forensic PDF report is generated.

## ☁️ Deploying to Streamlit Cloud

1. Push this repository to GitHub.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and connect your GitHub repo.
3. Set `OPENAI_API_KEY` in Streamlit Cloud's secret settings.

---

© 2025 Forensic AI Analyzer. Built with ❤️ and GPT-4.