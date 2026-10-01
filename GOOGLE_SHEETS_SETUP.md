# Google Sheets Setup Guide

This guide will help you set up Google Sheets for real-time data collection from Streamlit Cloud.

## Why Google Sheets?

- ✅ **Real-time sync** - Data appears instantly as participants complete study
- ✅ **Cloud accessible** - View data from anywhere
- ✅ **No manual downloads** - Automatic collection
- ✅ **Works with Streamlit Cloud** - No file storage limitations

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a Project"** → **"New Project"**
3. Name it: `mphil-study-data`
4. Click **"Create"**

---

## Step 2: Enable Google Sheets API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Sheets API"**
3. Click on it → Click **"Enable"**

---

## Step 3: Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in:
   - **Name:** `streamlit-study-logger`
   - **Description:** `Service account for logging study data`
4. Click **"Create and Continue"**
5. **Role:** Select **"Editor"** (under "Basic")
6. Click **"Done"**

---

## Step 4: Generate JSON Key

1. In **"Credentials"**, find your service account
2. Click on the service account email
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create New Key"**
5. Choose **"JSON"**
6. Click **"Create"** - A JSON file will download
7. **Keep this file safe!** This is your authentication credential

---

## Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a **new blank spreadsheet**
3. Name it: `MPhil Study Data Collection`
4. Copy the **Spreadsheet ID** from URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```

---

## Step 6: Share Sheet with Service Account

1. In your Google Sheet, click **"Share"** button (top right)
2. Paste the **service account email** from the JSON file
   - It looks like: `streamlit-study-logger@mphil-study-data.iam.gserviceaccount.com`
3. Give it **"Editor"** access
4. **Uncheck** "Notify people"
5. Click **"Share"**

---

## Step 7: Configure Streamlit Cloud Secrets

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Select your app (e.g., **mphil-study-variant-a**)
3. Click **"⚙️ Settings"** → **"Secrets"**
4. Paste this format:

```toml
# Google Sheets Configuration
spreadsheet_key = "YOUR_SPREADSHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-study-logger@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

**How to fill this out:**
1. Open the downloaded JSON file
2. Copy each field from JSON to the TOML format above
3. **Important:** For `private_key`, keep the `\n` characters - don't replace them with actual line breaks

5. Click **"Save"**
6. **Repeat for all 3 apps** (Variant A, Variant B, Final Feedback)

---

## Step 8: Local Development Setup (Optional)

For local testing, create two files:

### `service_account.json`
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...paste entire downloaded JSON here...
}
```

### `google_sheets_config.json`
```json
{
  "spreadsheet_key": "YOUR_SPREADSHEET_ID_HERE"
}
```

**Add to `.gitignore`:**
```
service_account.json
google_sheets_config.json
```

---

## Step 9: Test the Setup

1. Push code changes to GitHub
2. Wait for Streamlit Cloud to redeploy (~2 minutes)
3. Open one of your deployed apps
4. Complete a test response
5. Check your Google Sheet - data should appear!

---

## Troubleshooting

### Error: "Insufficient permissions"
- Make sure you shared the Sheet with the service account email
- Check that the service account has "Editor" role

### Error: "API has not been used in project"
- Go back to Google Cloud Console
- Enable Google Sheets API for your project

### Error: "Invalid credentials"
- Double-check the secrets formatting in Streamlit Cloud
- Make sure `private_key` has `\n` characters intact

### Data not appearing
- Check Streamlit Cloud logs for error messages
- Verify spreadsheet_key is correct
- Ensure all 3 apps have the same secrets configured

---

## Viewing Your Data

Your Google Sheet will have these tabs (created automatically):
- `demographics` - Participant info
- `sus_responses` - System Usability Scale scores
- `trust_responses` - Trust questionnaire responses
- `understanding_responses` - Task prediction accuracy
- `decision_confidence` - Confidence ratings per task
- `qualitative_feedback` - Open-ended feedback

---

## Security Notes

⚠️ **Keep safe:**
- Service account JSON file
- Never commit to GitHub
- Don't share publicly

✅ **Safe to share:**
- Spreadsheet link (with view-only access)
- Spreadsheet ID

---

## Next Steps

After setup, you can:
1. Share Google Sheet with your supervisor (view-only)
2. Create charts/analysis in Google Sheets
3. Export to CSV for statistical analysis
4. Set up email notifications for new responses

---

Need help? Check the error messages in Streamlit Cloud logs or Google Cloud Console.
