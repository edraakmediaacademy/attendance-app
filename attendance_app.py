import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# --------------------------- Page Config ---------------------------
st.set_page_config(page_title="نظام تسجيل الحضور", page_icon="📝", layout="centered")

# --------------------------- CSS Loader ----------------------------
def load_css():
    # Try to load from ./static/style.css then ./style.css
    css_candidates = ["static/style.css", "style.css"]
    for p in css_candidates:
        try:
            with open(p, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                return
        except FileNotFoundError:
            continue

load_css()

# --------------------------- Header visuals ------------------------
st.markdown('<div class="wave-bg"></div>', unsafe_allow_html=True)
# Replace with your logo if desired
st.markdown(
    '<div class="logo-wrapper"><svg viewBox="0 0 512 512"><circle cx="256" cy="256" r="200" fill="#f0f0f0"/><text x="50%" y="53%" text-anchor="middle" font-size="140" font-family="sans-serif">📝</text></svg></div>',
    unsafe_allow_html=True
)

# --------------------------- Data setup ----------------------------
DATA_FILE = Path("attendance_data.csv")

COLUMNS = ["timestamp", "name", "email", "masterclass", "session"]

MASTERCLASSES = [
    "كيف تتحقق من الأخبار باستخدام الذكاء الاصطناعي - فهمي متولي",
    "كتابة المحتوى للسوشيال ميديا - أشرف سالم",
    "كتابة وصياغة الأخبار للسوشيال ميديا - محمد عواد",
    "تصحيح مفاهيم التسويق الرقمي - يحيى نايل",
]

SESSIONS = ["اليوم الأول", "اليوم الثاني", "اليوم الثالث"]

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            # Ensure required columns
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def append_record(record: dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    # also clear cache to reflect immediately
    load_data.clear()

@st.cache_data(show_spinner=False)
def get_today_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # parse timestamp to date
    try:
        d = pd.to_datetime(df["timestamp"])
        today = pd.Timestamp.now().date()
        return df[d.dt.date == today]
    except Exception:
        return df.tail(50)

# --------------------------- Form UI -------------------------------
st.markdown('<div class="form-box">', unsafe_allow_html=True)

st.header("📋 تسجيل حضور الماستر كلاس")

name = st.text_input("الاسم الكامل")
email = st.text_input("البريد الإلكتروني")
masterclass = st.selectbox("اختر الماستر كلاس", MASTERCLASSES, index=1)
session = st.selectbox("اختر اليوم / الجلسة", SESSIONS, index=0)

col_submit, col_clear = st.columns([2,1], gap="small")

with col_submit:
    submit = st.button("تسجيل الحضور", use_container_width=True)
with col_clear:
    clear = st.button("تفريغ الحقول", use_container_width=True)

if clear:
    st.experimental_rerun()

if submit:
    if not name.strip() or not email.strip():
        st.warning("⚠️ الرجاء إدخال الاسم والبريد الإلكتروني.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rec = {
            "timestamp": timestamp,
            "name": name.strip(),
            "email": email.strip(),
            "masterclass": masterclass,
            "session": session,
        }
        try:
            append_record(rec)
            st.success(f"✅ تم تسجيل حضورك بنجاح في «{masterclass}». شكرًا يا {name}!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء حفظ البيانات: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------- Data Preview & Export -----------------
st.markdown("### 🗂️ سجلات اليوم (آخر المدخلات)")
df_all = load_data()
df_today = get_today_data(df_all)

if df_today.empty:
    st.info("لا توجد سجلات لليوم حتى الآن.")
else:
    st.dataframe(df_today[::-1], use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)

with col1:
    # CSV download
    csv_bytes = df_all.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ تنزيل CSV كامل",
        data=csv_bytes,
        file_name="attendance_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Excel download
    try:
        import io
        from pandas import ExcelWriter
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_all.to_excel(writer, sheet_name="Attendance", index=False)
        st.download_button(
            label="⬇️ تنزيل Excel كامل",
            data=output.getvalue(),
            file_name="attendance_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.caption(f"تعذّر إنشاء ملف Excel ({e}). يرجى تنزيل CSV.")
