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
# قائمة أكواد الدول (تم نقلها للأعلى لتكون متاحة للـ callback)
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
# القيم الافتراضية للحقول
# -----------------------------------------------------
defaults = {
    "name": "",
    "email": "",
    "selected_country": "🇦🇪 الإمارات",
    "phone_number": "",
    "masterclass": "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
    "session": "اليوم الأول",
    "submission_status": None, # حالة جديدة لعرض الرسائل
}

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
# دالة الإرسال إلى Google Sheet (POST)
# -----------------------------------------------------
def send_to_google_sheet(record: dict) -> bool:
    try:
        res = requests.post(GOOGLE_SHEET_URL, json=record, timeout=8)
        return res.status_code == 200
    except Exception:
        return False

# -----------------------------------------------------
# دالة الإرسال وإعادة التعيين (Callback لـ st.button)
# -----------------------------------------------------
def submit_and_reset_form():
    """
    تُرسل البيانات ثم تُعيد تعيين قيم session_state.
    تُستدعى عبر on_click لتجنب StreamlitAPIException.
    """
    # جلب القيم من session_state مباشرة
    name = st.session_state["name"].strip()
    email = st.session_state["email"].strip()
    phone_number = st.session_state["phone_number"].strip()
    selected_country = st.session_state["selected_country"]
    masterclass = st.session_state["masterclass"]
    session = st.session_state["session"]

    # 1. التحقق من صحة البيانات
    if not name or not email or not phone_number:
        st.session_state["submission_status"] = "incomplete"
        return

    # 2. إعداد حمولة البيانات
    full_phone = f"{country_codes[selected_country]} {phone_number}"
    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "email": email,
        "phone": full_phone,
        "masterclass": masterclass,
        "session": session,
    }

    # 3. الإرسال وإعادة التعيين
    if send_to_google_sheet(payload):
        st.session_state["submission_status"] = "success"
        
        # تفريغ الحقول النصية والقيم الأخرى
        st.session_state["name"] = ""
        st.session_state["email"] = ""
        st.session_state["phone_number"] = ""
        # إعادة تعيين SelectBox إلى قيمها الافتراضية
        st.session_state["selected_country"] = defaults["selected_country"]
        st.session_state["masterclass"] = defaults["masterclass"]
        st.session_state["session"] = defaults["session"]
    else:
        st.session_state["submission_status"] = "error"

# -----------------------------------------------------
# تهيئة session_state
# -----------------------------------------------------
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


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
# واجهة الإدخال (الفورم الأساسي)
# -----------------------------------------------------
st.text_input("الاسم الكامل", key="name")
st.text_input("البريد الإلكتروني", key="email")

col_code, col_phone = st.columns([1, 2])
with col_code:
    st.selectbox(
        "كود الدولة", list(country_codes.keys()), index=0, key="selected_country"
    )
with col_phone:
    # هذا هو السطر الذي تم إصلاحه لضمان إغلاق السلسلة النصية والقوس بشكل صحيح
    st.text_input("رقم الموبايل", placeholder="5xxxxxxxx", key="phone_number")

st.selectbox(
    "اختر الماستر كلاس",
    [
        "كيف تتحقق من الأخبار باستخدام الذكاء الاصطناعي - فهمي متولي",
        "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
        "كتابة وصياغة الأخبار للسوشيال ميديا - محمد عواد",
        "تصحيح مفاهيم التسويق الرقمي - يحيى نايل",
    ],
    key="masterclass"
)

st.selectbox(
    "اختر اليوم / الجلسة",
    ["اليوم الأول", "اليوم الثاني", "اليوم الثالث"],
    key="session"
)

# -----------------------------------------------------
# زر التسجيل (باستخدام on_click)
# -----------------------------------------------------
# يتم استدعاء submit_and_reset_form مباشرة عند النقر لتحديث session_state بأمان
st.button(
    "تسجيل الحضور", 
    use_container_width=True, 
    on_click=submit_and_reset_form
)

# -----------------------------------------------------
# عرض رسالة الحالة بعد الإرسال
# -----------------------------------------------------
status = st.session_state["submission_status"]

if status == "success":
    st.success("✅ تم تسجيل حضورك بنجاح!")
    # إعادة تعيين الحالة لمنع ظهور الرسالة في دورات لاحقة
    st.session_state["submission_status"] = None 
elif status == "error":
    st.error("⚠️ حدث خطأ أثناء الإرسال إلى Google Sheet. تأكد أن السكربت منشور كـ Web App ومتاح (Anyone).")
    st.session_state["submission_status"] = None
elif status == "incomplete":
    st.warning("⚠️ الرجاء إدخال الاسم والبريد الإلكتروني ورقم الموبايل.")
    st.session_state["submission_status"] = None

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