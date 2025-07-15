# 🧠 Forensic Analysis Web App (Black & White Historical Photos)

This Streamlit-based web application is designed to perform forensic analysis of black-and-white historical images. It assesses image authenticity using a combination of EXIF metadata extraction, image forensics (ELA, noise maps, anomaly detection), and GPT-4 Vision for AI-based content interpretation.

---

## 🔧 Features

- 📤 Upload historical B&W images in JPG or PNG format.
- 🧾 Extract EXIF metadata (Make, Model, Software, DateTime).
- 🧪 Run image forensic tools:
  - Error Level Analysis (ELA)
  - Noise Map Computation
  - Pixel Anomaly Detection
- 📊 Calculate an authenticity score (0–100).
- 🧠 GPT-4 Vision integration for deep AI content analysis.
- 📄 Download a full forensic report in PDF format (English only).
- 🗂️ Track recent analysis history within the session.

---

## 🛠 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-user/forensic-app.git
cd forensic-app
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add OpenAI API Key

Create a `.streamlit/secrets.toml` file:

```toml
[general]
OPENAI_API_KEY = "your_openai_api_key_here"
```

> **Important:** Never expose your secret key in public repositories.

### 4. Run the app

```bash
streamlit run forensic_app.py
```

---

## 📤 Deployment (Streamlit Cloud)

To deploy on [Streamlit Cloud](https://streamlit.io/cloud):
- Upload your project files.
- Add your OpenAI API key via the "Secrets" tab (`OPENAI_API_KEY`).
- Click "Deploy".

---

## 📁 Project Structure

```
forensic_app/
├── forensic_app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```

---

## 🧠 AI Disclaimer

The application uses OpenAI’s GPT-4 Vision model to assist in identifying AI-generated or manipulated content. This is not a certified forensic tool and should be used for educational or investigative support only.

---

## 📄 License

MIT License