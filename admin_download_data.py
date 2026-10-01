"""
Admin Panel - Download Study Data
─────────────────────────────────────────────────────────────────────────────
Use this to download all study data from Streamlit Cloud deployment.

Run this on EACH deployed app to collect data:
1. Add ?admin=true to URL
2. Download the ZIP file
3. Extract and merge with your local data

Usage: 
- Variant A: https://your-app.streamlit.app?admin=true
- Variant B: https://your-app.streamlit.app?admin=true
- Final Feedback: https://your-app.streamlit.app?admin=true
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
from pathlib import Path
import zipfile
from io import BytesIO

# Check for admin mode
query_params = st.query_params
if query_params.get("admin") != "true":
    st.error("❌ Access Denied. Add ?admin=true to URL")
    st.stop()

st.title("📊 Admin Data Download")
st.markdown("---")

# Password protection (simple)
password = st.text_input("Enter Admin Password:", type="password")

if password != "download123":  # Change this password!
    if password:
        st.error("❌ Incorrect password")
    st.stop()

st.success("✅ Access Granted")
st.markdown("---")

# Check what data exists
study_data_dir = Path("study_data")

if not study_data_dir.exists():
    st.error("No study_data folder found!")
    st.stop()

# List all CSV files
csv_files = list(study_data_dir.glob("*.csv"))

if not csv_files:
    st.warning("No CSV files found in study_data folder")
    st.stop()

st.write(f"**Found {len(csv_files)} data files:**")
for f in csv_files:
    st.write(f"- {f.name}")

st.markdown("---")

# Create ZIP file
if st.button("📥 Download All Data as ZIP", type="primary", use_container_width=True):
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for csv_file in csv_files:
            zip_file.write(csv_file, arcname=csv_file.name)
    
    zip_buffer.seek(0)
    
    st.download_button(
        label="💾 Download study_data.zip",
        data=zip_buffer,
        file_name="study_data.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    st.success("✅ Download ready! Click the button above.")

st.markdown("---")

# Show preview of each file
if st.checkbox("Show Data Preview"):
    import pandas as pd
    
    for csv_file in csv_files:
        st.subheader(f"📄 {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            st.write(f"**Rows:** {len(df)}")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error reading {csv_file.name}: {e}")
        st.markdown("---")

st.caption("⚠️ Keep this URL private. Only share with authorized researchers.")
