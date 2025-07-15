# 🕵️ אפליקציית זיהוי פורנזי לתמונות היסטוריות

אפליקציה מבוססת Streamlit לניתוח אותנטיות של תמונות שחור-לבן, כולל:
- ניתוחי ELA, רעש, חריגות פיקסלים
- חילוץ Metadata
- שילוב GPT-4 Vision API

## 📦 התקנה מקומית

```bash
pip install -r requirements.txt
streamlit run forensic_app.py
```

## 🔐 מפתח OpenAI API

צור קובץ `.streamlit/secrets.toml` עם התוכן הבא:

```toml
OPENAI_API_KEY = "sk-...המפתח שלך כאן..."
```

## 🌐 פריסה ב־Streamlit Cloud

1. העלה את הפרויקט ל־GitHub.
2. ב־Streamlit Cloud:
   - בחר את הקובץ `forensic_app.py` כ־Main file.
   - הגדר את `OPENAI_API_KEY` תחת Settings → Secrets.

© 2025