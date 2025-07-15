# 🕵️ אפליקציה פורנזית לזיהוי תמונות היסטוריות בשחור-לבן

אפליקציה מבוססת Streamlit לבדיקת אותנטיות של תמונות, כולל:
- ניתוח ELA, מפת רעש, חריגות פיקסלים
- חילוץ Metadata (אם קיים)
- שילוב GPT-4 Vision API (עם הגדרת API Key דרך Streamlit secrets)

## 🚀 התקנה והרצה מקומית

1. התקן את התלויות:
```bash
pip install -r requirements.txt
```

2. הפעל את האפליקציה:
```bash
streamlit run forensic_app.py
```

3. במצב פרטי (ללא שאלת מפתח בכל פעם) - צור קובץ `secrets.toml` בתיקייה `.streamlit/`:

```toml
OPENAI_API_KEY = "sk-...המפתח שלך כאן..."
```

## 🌐 פריסה ב־Streamlit Cloud

1. העלה את כל הקבצים ל־GitHub.
2. ב־Streamlit Cloud, חבר את הריפוזיטורי והגדר את `OPENAI_API_KEY` תחת Settings > Secrets.

---

© 2025 יוסי אביטל