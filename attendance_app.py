import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Attendance Minimal Test", page_icon="📝", layout="centered")

st.title("📝 Attendance App Test")

st.write("If you can see this text, the rendering issue was caused by CSS or layout.")

name = st.text_input("Full Name")
phone = st.text_input("Phone")
email = st.text_input("Email")

if st.button("Submit"):
    st.success(f"Recorded: {name} - {phone} - {email}")
