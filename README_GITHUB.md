# DPP Blog Converter

Convert .docx blog files to clean, formatted HTML using Google Docs API with an easy-to-use desktop application.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Option 1: Download Pre-Built Executable (Recommended)](#option-1-download-pre-built-executable-recommended)
  - [Option 2: Run from Source](#option-2-run-from-source)
  - [Option 3: Build Your Own Executable](#option-3-build-your-own-executable)
- [Google API Setup](#google-api-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## ✨ Features

- **Automated Conversion**: Upload .docx files to Google Drive, export as HTML, and clean automatically
- **Smart HTML Cleaning**: Removes excess formatting while preserving:
  - Bold text and semantic formatting
  - Headings (H1-H6)
  - Lists (bulleted and numbered)
  - Tables with proper styling
  - Links
- **Two Document Formats Supported**:
  - Formatted documents (with "Begin writing" marker)
  - Unformatted documents (automatic heading detection)
- **Automatic Tag Generation**: AI-powered tag suggestion based on content
- **User-Friendly GUI**:
  - Setup wizard for first-time users
  - Real-time progress tracking
  - Status updates during conversion
  - One-click "Copy HTML" to clipboard
- **Standalone Application**: No Python installation required for end users

---

## 🚀 Installation

### Option 1: Download Pre-Built Executable (Recommended)

**For End Users (No Python Required)**

1. Download `DPPBlogConvert.exe` from the [Releases](https://github.com/DieselMikeK/convertblog/releases) page
2. Run the executable - that's it! No installation needed.
3. On first run, you'll be guided through the setup process

> **Note**: Windows may show a security warning. This is normal for unsigned executables. Click "More info" → "Run anyway"

### Option 2: Run from Source

**For Developers**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DieselMikeK/convertblog.git
   cd convertblog
   ```

2. **Install Python 3.8 or higher**:
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python blog_converter_gui.py
   ```

### Option 3: Build Your Own Executable

**For Creating a Distributable .exe**

1. Follow steps 1-3 from "Option 2: Run from Source"

2. **Build with PyInstaller**:
   ```bash
   pyinstaller DPPBlogConvert.spec
   ```

3. **Find your executable**:
   - Location: `dist/DPPBlogConvert.exe`
   - Size: ~40 MB (includes all dependencies)

4. **Distribute**:
   - Copy `DPPBlogConvert.exe` to share with others
   - No other files needed!

---

## 🔑 Google API Setup

Before you can convert files, you need Google API credentials. This is a **one-time setup**:

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"NEW PROJECT"**
3. Name it (e.g., "Blog Converter") and click **"CREATE"**

### Step 2: Enable Google Drive API

1. Make sure your project is selected
2. Go to **"APIs & Services"** → **"Library"**
3. Search for **"Google Drive API"**
4. Click **"ENABLE"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type → **"CREATE"**
3. Fill in required fields:
   - **App name**: `DPP Blog Converter`
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **"SAVE AND CONTINUE"** through all screens
5. On "Test users" page, add your email address

### Step 4: Create Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Select **"Desktop app"** as application type
4. Name it (e.g., "Blog Converter Desktop")
5. Click **"CREATE"**

### Step 5: Download Credentials

1. Click **"DOWNLOAD JSON"** on the popup
2. **Rename the file to**: `client_secret.json`
3. **Move it to**: Your DPPBlogBuilder folder (created during first run)

### First-Time Authentication

The first time you click "Convert":
1. A browser window will open automatically
2. Log in with your Google account
3. You may see: **"Google hasn't verified this app"**
   - This is normal! Click **"Advanced"** → **"Go to [App Name] (unsafe)"**
4. Click **"Allow"** to grant access
5. Close the browser and return to the app

Your authentication is saved in `token.pickle` - you only do this once!

---

## 📖 Usage

### Quick Start

1. **Run the Application**:
   - Double-click `DPPBlogConvert.exe` (or run `python blog_converter_gui.py`)

2. **First-Time Setup**:
   - Click **"Setup New Project"**
   - Choose a location (e.g., Desktop)
   - A `DPPBlogBuilder` folder will be created with:
     ```
     DPPBlogBuilder/
     ├── todo/              ← Put your .docx files here
     ├── output_html/       ← Your converted HTML appears here
     ├── raw_html/          ← Raw HTML (for debugging)
     ├── docx/              ← Archive folder
     ├── client_secret.json ← Add this (from Google Cloud)
     ├── token.pickle       ← Auto-generated
     ├── README.md          ← Instructions
     └── Tags.txt           ← Tag template
     ```

3. **Add Your Credentials**:
   - Place `client_secret.json` in the `DPPBlogBuilder` folder

4. **Convert Your Files**:
   - Add `.docx` files to the `todo` folder
   - Click **"Convert"**
   - Watch the real-time progress
   - Find your HTML in `output_html/[blog-name]/`

5. **Use Your HTML**:
   - Click **"Copy HTML"** to copy to clipboard
   - Paste into your blog editor
   - Tags are saved in `tags.txt` in each blog folder

### Converting Multiple Files

The converter processes all `.docx` files in the `todo` folder in one batch:
- Progress bar shows completion percentage
- Status window displays real-time updates
- Each file gets its own folder in `output_html/`

### Understanding Output Folders

Each converted blog creates a folder with:
```
output_html/
└── blog-name/
    ├── blog-name.html  ← Cleaned HTML
    └── tags.txt        ← Suggested tags
```

---

## 📁 Project Structure

```
convertblog/
├── blog_converter_gui.py    # Main GUI application
├── convert_blog.py           # Conversion logic and HTML cleaning
├── tagFinder.py              # Automatic tag generation
├── DPPBlogConvert.spec       # PyInstaller build configuration
├── requirements.txt          # Python dependencies
├── README.md                 # User setup guide
├── README_GITHUB.md          # This file (GitHub installation)
├── BUILD_INSTRUCTIONS.md     # How to build the executable
├── Tags.txt                  # Default tag list
├── header.png                # UI header image
├── icon.png                  # Application icon
├── icon.ico                  # Windows executable icon
└── dist/
    └── DPPBlogConvert.exe    # Built executable
```

---

## 🛠️ Requirements

### For Running from Source:
- Python 3.8 or higher
- Dependencies (installed via `requirements.txt`):
  - `google-api-python-client>=2.0.0`
  - `google-auth>=2.0.0`
  - `google-auth-oauthlib>=0.5.0`
  - `google-auth-httplib2>=0.1.0`
  - `beautifulsoup4>=4.9.0`
  - `pillow>=9.0.0`

### For Building Executable:
- All of the above, plus:
  - `pyinstaller>=5.0.0`

### For End Users (Pre-Built .exe):
- **Nothing!** Just Windows 10/11

---

## 🐛 Troubleshooting

### "client_secret.json not found"
- Make sure you downloaded credentials from Google Cloud Console
- Rename to exactly `client_secret.json` (lowercase, no extra numbers)
- Place in the `DPPBlogBuilder` folder

### "No .docx files found"
- Check files are in the `todo` folder
- Make sure they have `.docx` extension (not `.doc`)

### Browser doesn't open for authentication
- Make sure you have a default browser set
- Try running as administrator
- Check firewall settings

### Conversion fails or produces errors
- Verify your .docx file isn't corrupted
- Make sure you're connected to the internet
- Check the status messages for specific errors

### Authentication expires
- Delete `token.pickle` file
- Run the converter again
- Re-authenticate in the browser

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/convertblog.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Mike K** - [DieselMikeK](https://github.com/DieselMikeK)

---

## 🙏 Acknowledgments

- Uses Google Drive API for document conversion
- BeautifulSoup4 for HTML parsing and cleaning
- PyInstaller for executable creation

---

## 📧 Support

For issues, questions, or feature requests, please [open an issue](https://github.com/DieselMikeK/convertblog/issues) on GitHub.

---

**Version**: 1.0
**Last Updated**: December 2024
