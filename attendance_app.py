import streamlit as st
import requests
import time
from datetime import datetime

# -----------------------------------------------------
# إعداد الصفحة العامة
# -----------------------------------------------------
st.set_page_config(page_title="نظام تسجيل الحضور", page_icon="📝", layout="centered")

# -----------------------------------------------------
# تحميل CSS (من static أو من نفس المجلد)
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
# رابط Google Apps Script
# -----------------------------------------------------
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw8cBRPqxDeBT2PMxdijsMApk1kqBvfHW_XzPzTfDGsn9TTiIut4xxwXgpkKPV0dr3d0Q/exec"

# -----------------------------------------------------
# دالة جلب عدد المسجلين من Google Sheet
# -----------------------------------------------------
def get_registered_count():
    try:
        response = requests.get(GOOGLE_SHEET_URL)
        if response.status_code == 200:
            return int(response.text.strip())
        else:
            return None
    except Exception:
        return None

# -----------------------------------------------------
# شعار علوي + عداد
# -----------------------------------------------------
st.markdown(
    '<div class="form-logo-wrapper"><svg viewBox="0 0 512 512"><circle cx="256" cy="256" r="200" fill="#f0f0f0"/><text x="50%" y="53%" text-anchor="middle" font-size="140" font-family="sans-serif">📝</text></svg></div>',
    unsafe_allow_html=True
)
st.header("📋 تسجيل حضور الماستر كلاس")

count = get_registered_count()
if count is not None:
    st.markdown(f"<div style='text-align:center; font-size:18px; margin-bottom:15px;'>👥 عدد المسجلين حتى الآن: <b>{count}</b></div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align:center; color:#999;'>جارٍ تحميل عدد المسجلين...</div>", unsafe_allow_html=True)

# -----------------------------------------------------
# إعداد session_state للفورم
# -----------------------------------------------------
defaults = {
    "name": "",
    "email": "",
    "selected_country": "🇦🇪 الإمارات",
    "phone_number": "",
    "masterclass": "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
    "session": "اليوم الأول",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -----------------------------------------------------
# قائمة أكواد الدول
# -----------------------------------------------------
country_codes = {
    "🇦🇪 الإمارات": "+971",
    "🇸🇦 السعودية": "+966",
    "🇪🇬 مصر": "+20",
    "🇶🇦 قطر": "+974",
    "🇰🇼 الكويت": "+965",
    "🇧🇭 البحرين": "+973",
    "🇴🇲 عمان": "+968",
    "🇯🇴 الأردن": "+962",
    "🇱🇧 لبنان": "+961"
}

# -----------------------------------------------------
# عناصر الفورم
# -----------------------------------------------------
name = st.text_input("الاسم الكامل", key="name")
email = st.text_input("البريد الإلكتروني", key="email")

col_code, col_phone = st.columns([1, 2])
with col_code:
    selected_country = st.selectbox("كود الدولة", list(country_codes.keys()), index=0, key="selected_country")
with col_phone:
    phone_number = st.text_input("رقم الموبايل", placeholder="5xxxxxxxx", key="phone_number")

masterclass = st.selectbox(
    "اختر الماستر كلاس",
    [
        "كيف تتحقق من الأخبار باستخدام الذكاء الاصطناعي - فهمي متولي",
        "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
        "كتابة وصياغة الأخبار للسوشيال ميديا - محمد عواد",
        "تصحيح مفاهيم التسويق الرقمي - يحيى نايل",
    ],
    key="masterclass"
)

session = st.selectbox(
    "اختر اليوم / الجلسة",
    ["اليوم الأول", "اليوم الثاني", "اليوم الثالث"],
    key="session"
)

# -----------------------------------------------------
# دالة الإرسال إلى Google Sheet
# -----------------------------------------------------
def send_to_google_sheet(record: dict):
    try:
        response = requests.post(GOOGLE_SHEET_URL, json=record)
        return response.status_code == 200
    except Exception:
        return False

# -----------------------------------------------------
# زر التسجيل
# -----------------------------------------------------
success_message = st.empty()  # لعرض رسالة النجاح تحت الزر

if st.button("تسجيل الحضور", use_container_width=True):
    if not st.session_state.name.strip() or not st.session_state.email.strip() or not st.session_state.phone_number.strip():
        st.warning("⚠️ الرجاء إدخال الاسم والبريد الإلكتروني ورقم الموبايل.")
    else:
        full_phone = f"{country_codes[st.session_state.selected_country]} {st.session_state.phone_number.strip()}"
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": st.session_state.name.strip(),
            "email": st.session_state.email.strip(),
            "phone": full_phone,
            "masterclass": st.session_state.masterclass,
            "session": st.session_state.session,
        }

        if send_to_google_sheet(record):
            success_message.success("✅ تم تسجيل حضورك بنجاح!")

            # تصفير الخانات بعد التسجيل
            for key, value in defaults.items():
                st.session_state[key] = value

            # إبقاء الرسالة 3 ثواني
            time.sleep(3)
            success_message.empty()
            st.rerun()
        else:
            st.error("⚠️ حدث خطأ أثناء الإرسال إلى Google Sheet.")

# -----------------------------------------------------
# ملاحظة أسفل الصفحة
# -----------------------------------------------------
st.markdown(
    """
    <div style='text-align:center; margin-top:40px; color:#666; font-size:0.9rem'>
        يتم حفظ جميع البيانات مباشرة في Google Sheet.<br>
        تأكد من أن الرابط مفعل للوصول العام (Anyone can access).
    </div>
    """,
    unsafe_allow_html=True,
)
