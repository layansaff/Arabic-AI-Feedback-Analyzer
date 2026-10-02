
import re
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Arabic AI Feedback Analyzer",
    layout="wide"
)

st.title("Arabic AI Feedback Analyzer")
st.write("تحليل الملاحظات وتصنيف المشاعر")

if st.session_state.pop("feedback_success", False):
    st.success("تمت إضافة الملاحظة وتحديث النتائج بنجاح")


# تطبيع النص العربي
def normalize_arabic(text):
    text = str(text).strip()
    text = re.sub(r'[\u064B-\u065F\u0670ـ]', '', text)
    text = re.sub(r'[أإآٱ]', 'ا', text)
    return text.replace('ى', 'ي')


# الكلمات المفتاحية
positive = [
    "ممتاز", "رائع", "جميل", "ممتازة",
    "ممتازين", "ممتازه", "رائعة", "جيد", "جيدة"
]

negative = [
    "سيئ", "سيئة", "سيء", "مشكلة",
    "سيئه", "سيء جدا", "سيئة جدا", "ضعيف", "ضعيفة"
]

positive = [normalize_arabic(w) for w in positive]
negative = [normalize_arabic(w) for w in negative]


# تصنيف المشاعر
def classify(text):
    text = normalize_arabic(text)

    has_positive = any(word in text for word in positive)
    has_negative = any(word in text for word in negative)

    if has_positive and not has_negative:
        return "إيجابي"
    if has_negative and not has_positive:
        return "سلبي"
    return "محايد"


# قراءة البيانات
file_path = Path(__file__).parent / "feedback.csv"

if file_path.exists():
    try:
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig",
            keep_default_na=False
        )
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["feedback"])
    except Exception as e:
        st.error(f"تعذرت قراءة ملف البيانات: {e}")
        st.stop()

    if "feedback" not in df.columns:
        st.error("ملف البيانات لا يحتوي على عمود feedback")
        st.stop()

    df = df[["feedback"]].copy()
else:
    df = pd.DataFrame(columns=["feedback"])

df["feedback"] = df["feedback"].fillna("").astype(str)
df = df[df["feedback"].str.strip() != ""].copy()
df["sentiment"] = df["feedback"].apply(classify)


# الإحصائيات
counts = df["sentiment"].value_counts()

col1, col2, col3 = st.columns(3)

col1.metric("إجمالي الملاحظات", len(df))
col2.metric("الإيجابية", counts.get("إيجابي", 0))
col3.metric("السلبية", counts.get("سلبي", 0))


# الرسم البياني
st.subheader("نتائج تحليل المشاعر")

chart_data = pd.DataFrame(
    {
        "عدد الملاحظات": [
            counts.get("إيجابي", 0),
            counts.get("سلبي", 0),
            counts.get("محايد", 0)
        ]
    },
    index=["إيجابي", "سلبي", "محايد"]
)

st.bar_chart(chart_data)


# جدول الملاحظات
st.subheader("الملاحظات المصنفة")
st.dataframe(df, use_container_width=True, hide_index=True)


# تحميل النتائج
csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="تحميل النتائج",
    data=csv,
    file_name="output_feedback.csv",
    mime="text/csv"
)


# إضافة ملاحظة جديدة
st.divider()
st.subheader("إضافة ملاحظة جديدة")

with st.form("feedback_form", clear_on_submit=True):
    new_feedback = st.text_area("اكتبي ملاحظتك هنا")
    submitted = st.form_submit_button("تحليل الملاحظة")

    if submitted:
        if not new_feedback.strip():
            st.warning("اكتبي ملاحظة أولًا")
        else:
            new_row = pd.DataFrame(
                [{"feedback": new_feedback.strip()}]
            )

            updated_df = pd.concat(
                [df[["feedback"]], new_row],
                ignore_index=True
            )

            try:
                updated_df.to_csv(
                    file_path,
                    index=False,
                    encoding="utf-8-sig"
                )
                st.session_state["feedback_success"] = True
                st.rerun()
            except OSError as e:
                st.error(f"تعذر حفظ الملاحظة: {e}")
