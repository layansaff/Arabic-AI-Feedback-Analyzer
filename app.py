import streamlit as st
import pandas as pd
import re
from collections import Counter
from pathlib import Path

st.set_page_config(page_title="Arabic AI Feedback Analyzer", layout="wide")

st.title("Arabic AI Feedback Analyzer")
st.write("تحليل الملاحظات وتصنيف المشاعر")

def normalize_arabic(text):
    text = re.sub(r'[\u064B-\u065F\u0670ـ]', '', str(text))
    text = re.sub(r'[أإآٱ]', 'ا', text)
    return text.replace('ى', 'ي')

positive = ["ممتاز", "رائع", "جميل", "ممتازة"]
negative = ["سيئ", "سيئة", "سيء", "مشكلة"]

file_path = Path(__file__).parent / "feedback.csv"

if file_path.exists():
    df = pd.read_csv(file_path, encoding="utf-8-sig")

    if "feedback" in df.columns:
        def classify(text):
            text = normalize_arabic(text)
            if any(w in text for w in positive):
                return "إيجابي"
            if any(w in text for w in negative):
                return "سلبي"
            return "محايد"

        df["sentiment"] = df["feedback"].apply(classify)

        counts = df["sentiment"].value_counts()

        col1, col2, col3 = st.columns(3)

        col1.metric("إجمالي الملاحظات", len(df))
        col2.metric("الإيجابية", counts.get("إيجابي", 0))
        col3.metric("السلبية", counts.get("سلبي", 0))

        counts = df["sentiment"].value_counts()
        st.subheader("نتائج تحليل المشاعر")
        st.bar_chart(counts)

        st.subheader("الملاحظات المصنفة")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "تحميل النتائج",
            data=csv,
            file_name="output_feedback.csv",
            mime="text/csv"
        )
    else:
        st.error("ملف البيانات لا يحتوي على عمود feedback")
else:
    st.error("ملف feedback.csv غير موجود")