import streamlit as st
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

# --- Configuration ---
APP_ROOT = Path(__file__).parent  # Get the root directory of the app
STATIC_DIR = APP_ROOT / "static"
DATA_DIR = APP_ROOT / "data"
DATA_FILE = DATA_DIR / "attendance.xlsx"

# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# -------- إعداد الصفحة --------
st.set_page_config(page_title="Attendance App", page_icon="📝", layout="centered")

# -------- تحميل CSS --------
try:
    css_file = STATIC_DIR / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("`static/style.css` not found. Running without custom styles.")
except Exception as e:
    st.error(f"Error loading CSS: {e}")

# -------- خلفية موجية + مسافة فوق المحتوى --------
st.markdown("""
    <div class='wave-bg'></div>
    <div style='height:120px'></div>
""", unsafe_allow_html=True)

# -------- الشعار (Inline SVG لضمان الظهور على Streamlit Cloud) --------
logo_path = STATIC_DIR / "logo.svg"
if logo_path.exists():
    try:
        svg = logo_path.read_text(encoding="utf-8")
        st.markdown(f"<div style='text-align:center;margin-bottom:10px'>{svg}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading logo SVG: {e}")
else:
    st.warning("`static/logo.svg` not found. Running without logo.")

# -------- عنوان ووصف --------
st.title("📝 نموذج حضور – تسجيل البيانات")
st.write("املأ البيانات التالية. النموذج متجاوب ويعمل باللمس على الأجهزة المحمولة.")

# -------- ملف البيانات --------
if not DATA_FILE.exists():
    pd.DataFrame(columns=["الاسم الكامل", "التليفون", "الإيميل", "الوقت"]).to_excel(DATA_FILE, index=False)

# -------- دوال التحقق --------
try:
    phone_re = re.compile(r"^\+?\d{7,15}$")
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
except Exception as e:
    st.error(f"Regex compilation error: {e}")
    phone_re = None
    email_re = None

def validate_phone(x: str) -> bool:
    if phone_re:
        return bool(phone_re.match(x.strip()))
    return len(x.strip()) > 5

def validate_email(x: str) -> bool:
    if email_re:
        return bool(email_re.match(x.strip()))
    return "@" in x.strip() and "." in x.strip()



# -------- حاوية النموذج --------
with st.container():
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)

    name  = st.text_input("الاسم الكامل", placeholder="اكتب اسمك هنا")
    phone = st.text_input("التليفون (مثال: +971501234567 أو 0501234567)")
    email = st.text_input("الإيميل", placeholder="example@email.com")

    if st.button("سجّل الحضور ✅", use_container_width=True):
        if not name.strip() or not phone.strip() or not email.strip():
            st.warning("الرجاء إدخال جميع البيانات قبل التسجيل.")
        elif not validate_phone(phone):
            st.warning("صيغة رقم الهاتف غير صحيحة.")
        elif not validate_email(email):
            st.warning("صيغة البريد الإلكتروني غير صحيحة.")
        else:
            try:
                df_old = pd.read_excel(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame(
                    columns=["الاسم الكامل", "التليفون", "الإيميل", "الوقت"]
                )
                new_row = {
                    "الاسم الكامل": name.strip(),
                    "التليفون": phone.strip(),
                    "الإيميل": email.strip(),
                    "الوقت": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                df_new = pd.concat([df_old, pd.DataFrame([new_row])], ignore_index=True)
                df_new.to_excel(DATA_FILE, index=False)
                st.success("تم تسجيل حضورك بنجاح 🎉")
            except Exception as e:
                st.error(f"حدث خطأ أثناء حفظ البيانات: {e}")

    if DATA_FILE.exists():
        with open(DATA_FILE, "rb") as fh:
            st.download_button(
                "⬇️ تحميل قاعدة البيانات",
                data=fh,
                file_name="attendance.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)



# -------- فاصل وملاحظات --------
st.markdown("---")
st.caption("لتشغيله محليًا: `python3 -m pip install streamlit pandas openpyxl && streamlit run attendance_app.py`")
