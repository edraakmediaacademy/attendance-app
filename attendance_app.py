import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# إعداد الصفحة
st.set_page_config(page_title="Attendance App", page_icon="📝", layout="centered")

# تحميل CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# رسم الخلفية الموجية
st.markdown("""
    <div class='wave-bg'></div>
    <div style='height:160px'></div>
""", unsafe_allow_html=True)

# عرض الشعار
logo_path = Path("static/logo.svg")
if logo_path.exists():
    with open(logo_path, "r") as f:
        logo_data = f.read()
    st.markdown(
        f"""
        <div style='text-align:center; margin-bottom:10px;'>
            {logo_data}
        </div>
        """,
        unsafe_allow_html=True
    )

# عنوان التطبيق
st.title("📝 نموذج حضور – تسجيل البيانات")
st.write("املأ البيانات التالية. النموذج متجاوب ويعمل باللمس على الأجهزة المحمولة.")

# إنشاء ملف البيانات إذا لم يكن موجودًا
DATA_FILE = Path("data/attendance.xlsx")
DATA_FILE.parent.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    df_init = pd.DataFrame(columns=["الاسم الكامل", "التليفون", "الإيميل", "الوقت"])
    df_init.to_excel(DATA_FILE, index=False)

# إدخ
