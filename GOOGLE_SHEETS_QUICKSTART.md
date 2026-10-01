# Google Sheets Setup - Quick Start

## Why We Switched to Google Sheets

**Problem:** Streamlit Cloud apps can't write back to GitHub (read-only access)
- P004, P005 data was stuck in cloud containers
- No automatic way to collect participant responses

**Solution:** Write directly to Google Sheets from cloud apps
- ✅ Real-time data sync
- ✅ No manual downloads needed
- ✅ Accessible from anywhere
- ✅ CSV backup still works locally

---

## Setup Process (30 minutes)

### 1️⃣ **Create Google Cloud Project** (5 min)
- Visit: https://console.cloud.google.com/
- Create new project: "mphil-study-data"

### 2️⃣ **Enable Google Sheets API** (2 min)
- APIs & Services → Library
- Search "Google Sheets API" → Enable

### 3️⃣ **Create Service Account** (3 min)
- APIs & Services → Credentials
- Create Credentials → Service Account
- Name: "streamlit-study-logger"
- Role: "Editor"

### 4️⃣ **Download JSON Key** (1 min)
- Click service account → Keys tab
- Add Key → Create New Key → JSON
- **Save this file securely!**

### 5️⃣ **Create Google Sheet** (2 min)
- Visit: https://sheets.google.com/
- New blank spreadsheet
- Name: "MPhil Study Data Collection"
- Copy the Spreadsheet ID from URL

### 6️⃣ **Share Sheet with Service Account** (1 min)
- Click "Share" button
- Paste service account email (from JSON file)
- Give "Editor" access
- Uncheck "Notify people"

### 7️⃣ **Configure Streamlit Cloud Secrets** (10 min per app)

For **EACH** of your 3 deployed apps:

1. Go to: https://share.streamlit.io/
2. Select app → Settings → Secrets
3. Paste this template:

```toml
spreadsheet_key = "YOUR_SPREADSHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

4. Fill in values from your downloaded JSON file
5. **Important:** Keep `\n` in private_key (don't replace with actual line breaks)
6. Save

### 8️⃣ **Test It!** (5 min)
- Open deployed app
- Complete a test response
- Check Google Sheet → Data should appear!

---

## Using the Setup Wizard

For local development, run:

```bash
python setup_google_sheets.py
```

This will:
1. Copy your service account JSON
2. Save spreadsheet ID
3. Show you the exact format for Streamlit Cloud secrets

---

## What Gets Created in Google Sheets

Your spreadsheet will automatically create these tabs:

| Tab Name | Content |
|----------|---------|
| `demographics` | Participant background info |
| `sus_responses` | System Usability Scale scores |
| `trust_responses` | Trust questionnaire data |
| `understanding_responses` | Task prediction accuracy |
| `decision_confidence` | Confidence ratings per task |
| `qualitative_feedback` | Open-ended responses |

---

## Viewing Your Data

**Real-time monitoring:**
- Open your Google Sheet
- Data appears as participants complete study
- Share (view-only) with supervisor

**Download for analysis:**
- File → Download → CSV (or Excel)
- Import to SPSS, R, Python for statistics

---

## Troubleshooting

### "No module named 'gspread'"
```bash
pip install -r requirements.txt
```

### "Insufficient permissions"
- Check: Did you share the Sheet with service account email?
- Check: Service account has "Editor" role?

### "API not enabled"
- Go to Google Cloud Console
- Enable Google Sheets API

### Data not appearing
- Check Streamlit Cloud logs (Settings → Logs)
- Verify secrets are configured correctly
- Make sure `private_key` has `\n` intact

### "active_sessions.csv" still missing
- This is now expected behavior
- Session persistence handled differently (see below)

---

## Session Persistence Fix

**Old approach (broken on cloud):**
- Used `.active_session.json` file
- Streamlit Cloud apps can't share files

**Current status:**
- Each app tracks sessions independently
- P001-P003 exist locally
- P004-P005 will be in Google Sheets

**Next step:**
- Test the flow: Complete Variant A → Open Variant B
- If "No active session" error persists, we'll implement URL-based session passing

---

## Security Notes

⚠️ **Never commit:**
- `service_account.json`
- `google_sheets_config.json`
- Spreadsheet private keys

✅ **Safe to share:**
- Spreadsheet view-only link
- Spreadsheet ID

---

## Need Help?

See full documentation: **GOOGLE_SHEETS_SETUP.md**

Or contact your supervisor for Google Cloud assistance.
