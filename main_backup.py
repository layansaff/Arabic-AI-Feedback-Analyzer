
import csv
import re
from collections import Counter
import matplotlib.pyplot as plt


# تنظيف النصوص العربية
def normalize_arabic(text):
    # إزالة التشكيل والتطويل
    text = re.sub(r'[\u064B-\u065F\u0670ـ]', '', text)

    # توحيد أشكال الألف
    text = re.sub(r'[أإآٱ]', 'ا', text)

    # توحيد الألف المقصورة
    text = text.replace('ى', 'ي')

    return text


# كلمات التصنيف
positive_words = ["ممتاز", "رائع", "جميل", "ممتازة"]
negative_words = ["سيئ", "سيئة", "سيء", "مشكلة"]

positive_words = [normalize_arabic(w) for w in positive_words]
negative_words = [normalize_arabic(w) for w in negative_words]


# قراءة الملاحظات وتصنيفها
results = []

with open("feedback.csv", "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        feedback = row["feedback"].strip()
        clean_feedback = normalize_arabic(feedback)

        if any(word in clean_feedback for word in positive_words):
            sentiment = "إيجابي"
        elif any(word in clean_feedback for word in negative_words):
            sentiment = "سلبي"
        else:
            sentiment = "محايد"

        results.append({
            "feedback": feedback,
            "sentiment": sentiment
        })


# تصدير النتائج إلى ملف CSV
with open("output_feedback.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["feedback", "sentiment"]
    )
    writer.writeheader()
    writer.writerows(results)


# إحصائيات التصنيف
counts = Counter(item["sentiment"] for item in results)
total = len(results)

print("\n--- ملخص تحليل الملاحظات ---")
print(f"إجمالي الملاحظات: {total}")

for sentiment in ["إيجابي", "سلبي", "محايد"]:
    count = counts[sentiment]
    percentage = (count / total * 100) if total else 0
    print(f"{sentiment}: {count} ({percentage:.1f}%)")


# استخراج أكثر 16 كلمة تكرارًا
stop_words = {
    "من", "في", "على", "الى", "عن", "هذا",
    "هذه", "كان", "كانت", "مع", "ما", "لا",
    "لم", "لن", "انا", "هو", "هي", "و"
}

stop_words = {normalize_arabic(w) for w in stop_words}

all_words = []

for item in results:
    clean_feedback = normalize_arabic(item["feedback"])
    words = re.findall(r'[\u0600-\u06FF]+', clean_feedback)

    all_words.extend(
        word for word in words
        if len(word) > 2 and word not in stop_words
    )

word_counts = Counter(all_words)

print("\n--- أكثر 16 كلمة تكرارًا ---")

for word, count in word_counts.most_common(16):
    print(f"{word}: {count}")


# تأكيد اكتمال التحليل
print("\nتم تحليل الملاحظات بنجاح!")


# إنشاء الرسم البياني
sentiments = ["Positive", "Negative", "Neutral"]

chart_counts = [
    counts["إيجابي"],
    counts["سلبي"],
    counts["محايد"]
]

plt.figure(figsize=(8, 5))
plt.bar(sentiments, chart_counts)

plt.title("Arabic Feedback Sentiment Analysis")
plt.xlabel("Sentiment")
plt.ylabel("Number of Feedbacks")

plt.tight_layout()
plt.savefig("sentiment_chart.png")
plt.show()
