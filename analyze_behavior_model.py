import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 1. تحميل البيانات من ملف CSV
df = pd.read_csv("client_behavior_data.csv")

# 2. فصل الميزات (features) عن التصنيف (label)
X = df.drop("label", axis=1)
y = df["label"]

# 3. تقسيم البيانات إلى تدريب واختبار
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. إنشاء وتدريب نموذج التصنيف
model = RandomForestClassifier(n_estimators=20, random_state=42)
model.fit(X_train, y_train)

# 5. التنبؤ على مجموعة الاختبار
y_pred = model.predict(X_test)

# 6. تقييم النموذج
accuracy = accuracy_score(y_test, y_pred)
print("Model Accuracy:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
