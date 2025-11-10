import streamlit as st
import requests
from datetime import datetime

# -----------------------------------------------------
# إعداد الصفحة العامة
# -----------------------------------------------------
st.set_page_config(page_title="نظام تسجيل الحضور", page_icon="📝", layout="centered")

# -----------------------------------------------------
# تحميل CSS (من مجلد static أو من نفس المجلد)
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
# إعداد الرابط الخاص بـ Google Apps Script
# -----------------------------------------------------
# 🔹 غيّر هذا الرابط إلى رابط الـ Web App الخاص بك بعد النشر من Google Apps Script
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwhZixCLKXVdp0mKl43_wUDbG4ggFrqE4uk68HhbhClEkZGIcg4m-UDMXFdeu4EWrtGmg/exec"

# -----------------------------------------------------
# واجهة التسجيل
# -----------------------------------------------------
st.markdown('<div class="form-logo-wrapper"><svg viewBox="0 0 512 512"><circle cx="256" cy="256" r="200" fill="#f0f0f0"/><text x="50%" y="53%" text-anchor="middle" font-size="140" font-family="sans-serif">📝</text></svg></div>', unsafe_allow_html=True)

st.header("📋 تسجيل حضور الماستر كلاس")

# بيانات الفورم
name = st.text_input("الاسم الكامل")
email = st.text_input("البريد الإلكتروني")

masterclass = st.selectbox(
    "اختر الماستر كلاس",
    [
        "كيف تتحقق من الأخبار باستخدام الذكاء الاصطناعي - فهمي متولي",
        "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
        "كتابة وصياغة الأخبار للسوشيال ميديا - محمد عواد",
        "تصحيح مفاهيم التسويق الرقمي - يحيى نايل",
    ]
)

session = st.selectbox("اختر اليوم / الجلسة", ["اليوم الأول", "اليوم الثاني", "اليوم الثالث"])

# -----------------------------------------------------
# إرسال البيانات إلى Google Sheet
# -----------------------------------------------------
def send_to_google_sheet(record: dict):
    """يرسل البيانات إلى Google Sheet عبر API."""
    try:
        response = requests.post(GOOGLE_SHEET_URL, json=record)
        if response.status_code == 200:
            st.success(f"✅ تم تسجيل حضورك بنجاح في «{record['masterclass']}».")
        else:
            st.error("⚠️ حدث خطأ أثناء الإرسال إلى Google Sheet.")
    except Exception as e:
        st.error(f"❌ لم يتمكن التطبيق من الاتصال: {e}")

# -----------------------------------------------------
# أزرار التحكم
# -----------------------------------------------------
col_submit, col_clear = st.columns([2, 1], gap="small")

with col_submit:
    submit = st.button("تسجيل الحضور", use_container_width=True)

with col_clear:
    clear = st.button("تفريغ الحقول", use_container_width=True)

if clear:
    st.experimental_rerun()

# -----------------------------------------------------
# عند الضغط على زر التسجيل
# -----------------------------------------------------
if submit:
    if not name.strip() or not email.strip():
        st.warning("⚠️ الرجاء إدخال الاسم والبريد الإلكتروني.")
    elif GOOGLE_SHEET_URL.startswith("https://script.google.com/macros/s/AKfycbxxxxxxxx"):
        st.warning("⚠️ الرجاء استبدال رابط GOOGLE_SHEET_URL بالرابط الصحيح من Google Apps Script.")
    else:
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name.strip(),
            "email": email.strip(),
            "masterclass": masterclass,
            "session": session,
        }
        send_to_google_sheet(record)

# -----------------------------------------------------
# ملاحظة للمستخدم
# -----------------------------------------------------
st.markdown(
    """
    <div style='text-align:center; margin-top:40px; color:#666; font-size:0.9rem'>
        يتم حفظ جميع البيانات مباشرة في Google Sheet المربوطة بالتطبيق.<br>
        تأكد من أن رابط Google Script صالح ومفعل للوصول العام (Anyone).
    </div>
    """,
    unsafe_allow_html=True,
)
