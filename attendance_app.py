import streamlit as st
import requests
from datetime import datetime

# -----------------------------------------------------
# إعداد الصفحة العامة
# -----------------------------------------------------
st.set_page_config(page_title="نظام تسجيل الحضور", page_icon="📝", layout="centered")

# -----------------------------------------------------
# تحميل CSS (تصميم الواجهة)
# -----------------------------------------------------
def load_css():
    for path in ["static/style.css", "style.css"]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                return
        except FileNotFoundError:
            continue

load_css()

# -----------------------------------------------------
# رابط Google Apps Script (احفظ هذا كما هو)
# -----------------------------------------------------
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw8cBRPqxDeBT2PMxdijsMApk1kqBvfHW_XzPzTfDGsn9TTiIut4xxwXgpkKPV0dr3d0Q/exec"

# -----------------------------------------------------
# دالة لجلب عدد المسجلين
# -----------------------------------------------------
def get_registered_count():
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=5)
        if response.status_code == 200:
            return int(response.text.strip())
        return None
    except Exception:
        return None

# -----------------------------------------------------
# تفعيل التحديث التلقائي للعداد كل 30 ثانية
# -----------------------------------------------------
st.autorefresh(interval=30000, key="auto_refresh_count")

# -----------------------------------------------------
# شعار وواجهة العنوان
# -----------------------------------------------------
st.markdown(
    '<div class="form-logo-wrapper"><svg viewBox="0 0 512 512">'
    '<circle cx="256" cy="256" r="200" fill="#f0f0f0"/>'
    '<text x="50%" y="53%" text-anchor="middle" font-size="140" font-family="sans-serif">📝</text>'
    '</svg></div>',
    unsafe_allow_html=True
)
st.header("تسجيل حضور الماستر كلاس")

# -----------------------------------------------------
# عرض العدّاد
# -----------------------------------------------------
count = get_registered_count()
if count is not None:
    st.markdown(
        f"<div style='text-align:center; font-size:18px; margin-bottom:15px;'>"
        f"👥 عدد المسجلين حتى الآن: <b>{count}</b></div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='text-align:center; color:#999;'>جارٍ تحميل عدد المسجلين...</div>",
        unsafe_allow_html=True
    )

# -----------------------------------------------------
# session_state الثابت (لحفظ البيانات أثناء التفاعل)
# -----------------------------------------------------
defaults = {
    "name": "",
    "email": "",
    "selected_country": "🇦🇪 الإمارات",
    "phone_num_
