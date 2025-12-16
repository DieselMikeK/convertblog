# Quick Start Guide - DPP Blog Converter

## For Developers (Building the .exe)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the executable:**
   ```bash
   pyinstaller DPPBlogConvert.spec
   ```

3. **Find your .exe:**
   - Look in `dist/DPPBlogConvert.exe`
   - This is your standalone application

## For End Users (Using the .exe)

### First Time Setup

1. **Run DPPBlogConvert.exe**
   - Double-click the application

2. **Click "Setup New Project"**
   - Choose where to create your project folder (e.g., Desktop)
   - A "DPPBlogBuilder" folder will be created automatically

3. **Get Google API Credentials**
   - Follow the instructions in the README.md file (found in your DPPBlogBuilder folder)
   - Download `client_secret.json` from Google Cloud Console
   - Place it in your DPPBlogBuilder folder

### Daily Use

1. **Add .docx files** to the `DPPBlogBuilder/todo` folder

2. **Run DPPBlogConvert.exe**
   - It will remember your project location

3. **Click "Convert"**
   - Watch the progress bar
   - Wait for "All files processed!" message

4. **Get your HTML files**
   - Click "Open Output Folder" button
   - Or navigate to `DPPBlogBuilder/output_html`

## If You Already Have a Project

- Run DPPBlogConvert.exe
- Click "Find Existing Project"
- Navigate to and select your DPPBlogBuilder folder
- Click "Select Folder"

## Folder Structure

```
DPPBlogBuilder/
├── todo/              ← Put .docx files here
├── docx/              ← Archive folder (optional)
├── output_html/       ← Your converted HTML files
├── raw_html/          ← Raw HTML (for debugging)
├── client_secret.json ← Google API credentials
└── token.pickle       ← Auto-generated auth token
```

## Troubleshooting

**"client_secret.json not found"**
- See README.md for how to get this file from Google Cloud Console

**"No .docx files found"**
- Make sure files are in the `todo` folder
- Files must have `.docx` extension

**Application won't start**
- Make sure you have internet connection (needed for Google API)
- Try running as administrator
- Check Windows Defender/antivirus hasn't quarantined it

**Conversion fails**
- Check progress messages for specific errors
- Verify your Google credentials are valid
- Make sure .docx files aren't corrupted

## Adding Your Logo (For Developers)

Place these files in DPPBlogApp folder before building:

- `logo.png` - 256x256px company logo (shows in setup screen)
- `header.png` - Header image for main UI
- `logo.ico` - Icon for the .exe file (optional)

Update `DPPBlogConvert.spec` to include them in `datas` list.

## Support

For technical issues or questions, contact your administrator.
