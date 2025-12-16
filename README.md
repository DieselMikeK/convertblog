# DPP Blog Converter - Setup Guide

Convert .docx blog files to clean, formatted HTML using Google Docs API.

---

## 🔑 IMPORTANT: Get Your Google API Credentials

Before you can convert files, you need to download a `client_secret.json` file from Google. Follow these steps carefully:

### Step 1: Go to Google Cloud Console

Visit: **https://console.cloud.google.com/**

### Step 2: Create a New Project

1. Click **"Select a project"** at the top of the page
2. Click **"NEW PROJECT"**
3. Give it a name like **"Blog Converter"** or **"DPP Blog Tool"**
4. Click **"CREATE"**
5. Wait a few seconds for the project to be created

### Step 3: Enable Google Drive API

1. Make sure your new project is selected at the top
2. In the left sidebar, click **"APIs & Services"** → **"Library"**
3. In the search box, type: **"Google Drive API"**
4. Click on **"Google Drive API"** in the results
5. Click the blue **"ENABLE"** button
6. Wait for it to enable (takes a few seconds)

### Step 4: Set Up OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"** (in the left sidebar)
2. Select **"External"** user type (unless you have a Google Workspace account)
3. Click **"CREATE"**
4. Fill in the required information:
   - **App name:** `DPP Blog Converter`
   - **User support email:** Select your email from the dropdown
   - **Developer contact email:** Enter your email
5. Click **"SAVE AND CONTINUE"**
6. On the "Scopes" page, just click **"SAVE AND CONTINUE"** (no changes needed)
7. On the "Test users" page, click **"+ ADD USERS"**
8. Enter your email address (the one you'll use to authenticate)
9. Click **"ADD"**
10. Click **"SAVE AND CONTINUE"**
11. Review and click **"BACK TO DASHBOARD"**

### Step 5: Create OAuth Client ID Credentials

1. Go to **"APIs & Services"** → **"Credentials"** (in the left sidebar)
2. Click the blue **"+ CREATE CREDENTIALS"** button at the top
3. Select **"OAuth client ID"**
4. For "Application type", select: **"Desktop app"**
5. Give it a name like: **"Blog Converter Desktop"**
6. Click **"CREATE"**

### Step 6: Download Your Credentials

1. A popup will appear showing your Client ID and Client Secret
2. Click the **"DOWNLOAD JSON"** button
3. A file will download with a long name like: `client_secret_123456789-abcdefg.apps.googleusercontent.com.json`

### Step 7: Rename and Place the File

**THIS IS CRITICAL:**

1. Find the downloaded file (usually in your Downloads folder)
2. **Rename it to exactly:** `client_secret.json` (all lowercase, no extra numbers)
3. **Move it to this folder:** `DPPBlogBuilder` (the same folder where this README is located)

The file should be at:
```
DPPBlogBuilder/client_secret.json
```

---

The first time you click "Convert":

1. **A browser window will automatically open**
2. **Log in with your Google account** (the one you added as a test user)
3. You may see a warning: **"Google hasn't verified this app"**
   - This is normal! It's your own app.
   - Click **"Advanced"** → **"Go to Blog Converter (unsafe)"**
4. Click **"Allow"** to grant the app access to Google Drive
5. The browser will show "The authentication flow has completed"
6. **Close the browser** and return to the converter

The app saves your authentication, so you only need to do this once!

---

## 📝 How to Use the Converter

Once you have `client_secret.json` in place:

1. **Add .docx files** to the `todo` folder inside DPPBlogBuilder
2. **Open DPPBlogConvert.exe** (or it's already open)
3. **Click the "Convert" button**
4. Watch the progress in real-time
5. When complete, your HTML files are in the **`output_html`** folder
6. Click **"Open Output Folder"** to see them

---

## 📁 Folder Structure

```
DPPBlogBuilder/
├── todo/              ← PUT YOUR .DOCX FILES HERE
├── output_html/       ← YOUR HTML FILES APPEAR HERE
├── raw_html/          ← Raw HTML (for debugging)
├── docx/              ← Archive folder (optional)
├── client_secret.json ← YOUR GOOGLE CREDENTIALS (you download this)
├── token.pickle       ← Saved login (auto-generated, don't touch)
├── convert_blog.py    ← Conversion script (bundled)
├── README.md          ← This file
└── Tags.txt           ← Blog tags template
```

---

## ❓ Troubleshooting

### Error: "client_secret.json not found"
- Make sure you downloaded the credentials from Google Cloud Console
- Make sure you renamed it to exactly `client_secret.json`
- Make sure it's in the `DPPBlogBuilder` folder (not in a subfolder)

### Error: "No .docx files found in todo folder"
- Make sure your Word files are in the `todo` folder
- Make sure they have the `.docx` extension (not `.doc`)

### Browser doesn't open for authentication
- Make sure you have a default browser set
- Try running the converter as administrator
- Check if your firewall is blocking it

### Authentication expires
- Delete the `token.pickle` file
- Run the converter again
- You'll be asked to authenticate again in the browser

### Conversion fails or produces errors
- Check that your .docx file isn't corrupted (try opening it in Word)
- Make sure you're connected to the internet
- Look at the status messages for specific error details

---

## 🎉 You're Ready!

Once you have `client_secret.json` in the DPPBlogBuilder folder, you're all set!

Just add .docx files to the `todo` folder and click Convert.

---

**Questions?** Contact your DPP Blog Converter administrator.

**Version:** 1.0
