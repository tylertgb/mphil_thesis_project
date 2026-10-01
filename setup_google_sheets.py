"""
Google Sheets Setup Helper
─────────────────────────────────────────────────────────────────────────────
Interactive script to help configure Google Sheets for data collection.

Run: python setup_google_sheets.py
─────────────────────────────────────────────────────────────────────────────
"""

import json
from pathlib import Path

print("\n" + "="*80)
print("GOOGLE SHEETS SETUP WIZARD")
print("="*80 + "\n")

print("This wizard will help you configure Google Sheets for data collection.")
print("Follow these steps BEFORE running this script:\n")
print("1. ✅ Create a Google Cloud project")
print("2. ✅ Enable Google Sheets API")
print("3. ✅ Create a service account")
print("4. ✅ Download the JSON key file")
print("5. ✅ Create a Google Sheet")
print("6. ✅ Share the sheet with your service account email\n")

print("See GOOGLE_SHEETS_SETUP.md for detailed instructions.\n")
print("="*80 + "\n")

# Check if ready
ready = input("Have you completed the above steps? (yes/no): ").strip().lower()

if ready != "yes":
    print("\n❌ Please complete the setup steps first.")
    print("   Read: GOOGLE_SHEETS_SETUP.md")
    exit(0)

print("\n" + "-"*80)
print("STEP 1: Service Account JSON")
print("-"*80 + "\n")

json_path = input("Enter path to your service account JSON file: ").strip()

if not Path(json_path).exists():
    print(f"\n❌ File not found: {json_path}")
    exit(1)

# Copy to project root
target_path = Path("service_account.json")
with open(json_path, 'r') as f:
    service_account = json.load(f)

with open(target_path, 'w') as f:
    json.dump(service_account, f, indent=2)

print(f"✅ Saved to: {target_path}")
print(f"   Service account: {service_account.get('client_email', 'N/A')}")

print("\n" + "-"*80)
print("STEP 2: Google Sheet ID")
print("-"*80 + "\n")

print("Your Google Sheet URL looks like:")
print("https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit\n")

spreadsheet_key = input("Enter your Spreadsheet ID: ").strip()

if not spreadsheet_key:
    print("\n❌ Spreadsheet ID is required")
    exit(1)

# Save config
config = {"spreadsheet_key": spreadsheet_key}
with open("google_sheets_config.json", 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Saved to: google_sheets_config.json")

print("\n" + "="*80)
print("✅ LOCAL SETUP COMPLETE!")
print("="*80 + "\n")

print("Your local environment is configured. Test it by running:")
print("  python -c \"from utils.dual_logger import DualLogger; logger = DualLogger()\"\n")

print("-"*80)
print("NEXT: Configure Streamlit Cloud")
print("-"*80 + "\n")

print("For your deployed apps, you need to add secrets:")
print("1. Go to https://share.streamlit.io/")
print("2. Select each app → Settings → Secrets")
print("3. Add the following:\n")

print("```toml")
print(f'spreadsheet_key = "{spreadsheet_key}"')
print("\n[gcp_service_account]")

# Show relevant fields from service account
for key in ["type", "project_id", "private_key_id", "client_email", "client_id"]:
    if key in service_account:
        print(f'{key} = "{service_account[key]}"')

print('private_key = "-----BEGIN PRIVATE KEY-----\\n...YOUR_KEY_HERE...\\n-----END PRIVATE KEY-----\\n"')
print('auth_uri = "https://accounts.google.com/o/oauth2/auth"')
print('token_uri = "https://oauth2.googleapis.com/token"')
print('auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"')

if "client_x509_cert_url" in service_account:
    print(f'client_x509_cert_url = "{service_account["client_x509_cert_url"]}"')

print("```\n")

print("⚠️  IMPORTANT:")
print("   - Copy the FULL private_key from your JSON file")
print("   - Keep the \\n characters (don't replace with actual line breaks)")
print("   - Add secrets to ALL 3 deployed apps\n")

print("="*80)
print("📖 For detailed instructions, see: GOOGLE_SHEETS_SETUP.md")
print("="*80 + "\n")
