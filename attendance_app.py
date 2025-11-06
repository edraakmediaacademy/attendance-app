import streamlit as st
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

# -------- إعداد الصفحة --------
st.set_page_config(page_title="Attendance App", page_icon="📝", layout="centered")

# -------- تحميل CSS --------
try:
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass  # لو مفيش CSS، كمل عادي

# -------- خلفية موجية + مسافة فوق المحتوى --------
st.markdown("""
    <div class='wave-bg'></div>
    <div style='height:160px'></div>
""", unsafe_allow_html=True)

# -------- الشعار (Inline SVG لضمان الظهور على Streamlit Cloud) --------
logo_path = Path("static/logo.svg")
if logo_path.exists():
    try:
        svg = logo_path.read_text(encoding="utf-8")
        st.markdown(f"<div style='text-align:center;margin-bottom:10px'>{svg}</div>", unsafe_allow_html=True)
    except Exception:
        pass

# -------- عنوان ووصف --------
st.title("📝 نموذج حضور – تسجيل البيانات")
st.write("املأ البيانات التالية. النموذج متجاوب ويعمل باللمس على الأجهزة المحمولة.")

# -------- ملف البيانات --------
DATA_FILE = Path("data/attendance.xlsx")
DATA_FILE.parent.mkdir(exist_ok=True)

if not DATA_FILE.exists():
    pd.DataFrame(columns=["الاسم الكامل", "التليفون", "الإيميل", "الوقت"]).to_excel(DATA_FILE, index=False)

# -------- دوال التحقق --------
phone_re = re.compile(r"^\+?\d{7,15}$")
email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_phone(x: str) -> bool:
    return bool(phone_re.match(x.strip()))

def validate_email(x: str) -> bool:
    return bool(email_re.match(x.strip()))

# -------- الحقول --------
name  = st.text_input("الاسم الكامل", placeholder="اكتب اسمك هنا")
phone = st.text_input("التليفون (مثال: +971501234567 أو 0501234567)")
email = st.text_input("الإيميل", placeholder="example@email.com")

# -------- زر التسجيل --------
if st.button("سجّل الحضور ✅", use_container_width=True):
    if not name.strip() or not phone.strip() or not email.strip():
        st.warning("الرجاء إدخال جميع البيانات قبل التسجيل.")
    elif not validate_phone(phone):
        st.warning("صيغة رقم الهاتف غير صحيحة.")
    elif not validate_email(email):
        st.warning("صيغة البريد الإلكتروني غير صحيحة.")
    else:
        try:
            df_old = pd.read_excel(DATA_FILE)
        except Exception:
            df_old = pd.DataFrame(columns=["الاسم الكامل", "التليفون", "الإيميل", "الوقت"])

        new_row = {
            "الاسم الكامل": name.strip(),
            "التليفون": phone.strip(),
            "الإيميل": email.strip(),
            "الوقت": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        df_new = pd.concat([df_old, pd.DataFrame([new_row])], ignore_index=True)
        df_new.to_excel(DATA_FILE, index=False)
        st.success("تم تسجيل حضورك بنجاح 🎉")

# -------- تنزيل قاعدة البيانات --------
if DATA_FILE.exists():
    with open(DATA_FILE, "rb") as fh:
        st.download_button(
            "⬇️ تحميل قاعدة البيانات",
            data=fh,
            file_name="attendance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# -------- فاصل وملاحظات --------
st.markdown("---")
st.caption("لتشغيله محليًا: `python3 -m pip install streamlit pandas openpyxl && streamlit run attendance_app.py`")
