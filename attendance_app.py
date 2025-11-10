import streamlit as st
import requests
from datetime import datetime
import json
import html
import streamlit.components.v1 as components

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
# رابط Google Apps Script
#   - يجب أن يكون السكربت يحتوي doPost (للحفظ) و doGet (لإرجاع العدّاد)
# -----------------------------------------------------
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw8cBRPqxDeBT2PMxdijsMApk1kqBvfHW_XzPzTfDGsn9TTiIut4xxwXgpkKPV0dr3d0Q/exec"

# -----------------------------------------------------
# دالة لجلب عدد المسجلين مرة واحدة كبداية (لا تسبب وميض)
# -----------------------------------------------------
def get_registered_count_initial():
    try:
        r = requests.get(GOOGLE_SHEET_URL, timeout=5)
        if r.status_code == 200:
            txt = r.text.strip()
            return int(txt) if txt.isdigit() else None
        return None
    except Exception:
        return None

# -----------------------------------------------------
# الشعار + العنوان
# -----------------------------------------------------
st.markdown(
    '<div class="form-logo-wrapper"><svg viewBox="0 0 512 512">'
    '<circle cx="256" cy="256" r="200" fill="#f0f0f0"/>'
    '<text x="50%" y="53%" text-anchor="middle" font-size="140" font-family="sans-serif">📝</text>'
    '</svg></div>',
    unsafe_allow_html=True
)
st.header("📋 تسجيل حضور الماستر كلاس")

# -----------------------------------------------------
# عدّاد المسجلين (بدون ريفريش الصفحة)
#   - نعرض قيمة أولية من السيرفر
#   - ثم نُحدّثها كل 30 ثانية داخل المتصفح عبر JS فقط
# -----------------------------------------------------
initial_count = get_registered_count_initial()
initial_count_text = str(initial_count) if initial_count is not None else "—"
safe_url = html.escape(GOOGLE_SHEET_URL, quote=True)

counter_html = f"""
<div id="count-box" style="text-align:center; font-size:18px; margin-bottom:15px;">
  👥 عدد المسجلين حتى الآن: <b id="count">{initial_count_text}</b>
</div>
<script>
  const url = "{safe_url}";
  async function updateCount() {{
    try {{
      const res = await fetch(url, {{ method: "GET", cache: "no-store" }});
      if (!res.ok) return;
      const txt = (await res.text()).trim();
      const n = parseInt(txt, 10);
      if (!Number.isNaN(n)) {{
        const el = document.getElementById("count");
        if (el) el.textContent = n.toString();
      }}
    }} catch (e) {{
      // تجاهل الأخطاء الشبكية بصمت (بدون كسر الواجهة)
    }}
  }}
  // تحديث مبدئي + تحديث كل 30 ثانية
  updateCount();
  setInterval(updateCount, 30000);
</script>
"""
components.html(counter_html, height=60)

# -----------------------------------------------------
# session_state (ثابت – لا نصفر أي حقول)
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
    "🇱🇧 لبنان": "+961",
}

# -----------------------------------------------------
# واجهة الإدخال (الفورم الأساسي) — لا تصفير بعد الإرسال
# -----------------------------------------------------
name = st.text_input("الاسم الكامل", key="name")
email = st.text_input("البريد الإلكتروني", key="email")

col_code, col_phone = st.columns([1, 2])
with col_code:
    selected_country = st.selectbox(
        "كود الدولة", list(country_codes.keys()), index=0, key="selected_country"
    )
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
# دالة الإرسال إلى Google Sheet (POST)
# -----------------------------------------------------
def send_to_google_sheet(record: dict) -> bool:
    try:
        res = requests.post(GOOGLE_SHEET_URL, json=record, timeout=8)
        return res.status_code == 200
    except Exception:
        return False

# -----------------------------------------------------
# زر التسجيل
# -----------------------------------------------------
if st.button("تسجيل الحضور", use_container_width=True):
    if not name.strip() or not email.strip() or not phone_number.strip():
        st.warning("⚠️ الرجاء إدخال الاسم والبريد الإلكتروني ورقم الموبايل.")
    else:
        full_phone = f"{country_codes[selected_country]} {phone_number.strip()}"
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name.strip(),
            "email": email.strip(),
            "phone": full_phone,
            "masterclass": masterclass,
            "session": session,
        }
        if send_to_google_sheet(payload):
            st.success("✅ تم تسجيل حضورك بنجاح!")
        else:
            st.error("⚠️ حدث خطأ أثناء الإرسال إلى Google Sheet. تأكد أن السكربت منشور كـ Web App ومتاح (Anyone).")

# -----------------------------------------------------
# ملاحظة أسفل الصفحة
# -----------------------------------------------------
st.markdown(
    """
    <div style='text-align:center; margin-top:40px; color:#666; font-size:0.9rem'>
        يتم حفظ جميع البيانات مباشرة في Google Sheet.<br>
        تأكد من أن رابط Google Apps Script مفعل للوصول العام (Anyone).
    </div>
    """,
    unsafe_allow_html=True,
)
