# Build Instructions for DPP Blog Converter

## Prerequisites

Make sure you have Python 3.8+ installed with all required dependencies.

## Step 1: Install Dependencies

```bash
pip install google-api-python-client google-auth-oauthlib beautifulsoup4 pillow pyinstaller
```

## Step 2: Build the Executable

Run PyInstaller with the spec file:

```bash
cd c:\Users\Mike\Desktop\DPPBlogApp
pyinstaller DPPBlogConvert.spec
```

This will create a `dist` folder containing `DPPBlogConvert.exe`

## Step 3: Optional - Add Logo/Icon

If you have logo and header images:

1. Place `logo.png` (256x256) in the DPPBlogApp folder
2. Place `header.png` in the DPPBlogApp folder
3. Optionally create `logo.ico` for the exe icon
4. Update the spec file to include:
   ```python
   datas=[
       ('convert_blog.py', '.'),
       ('README.md', '.'),
       ('Tags.txt', '.'),
       ('logo.png', '.'),
       ('header.png', '.'),
   ],
   ```
   And set:
   ```python
   icon='logo.ico',
   ```

## Step 4: Test the Executable

1. Navigate to `dist` folder
2. Run `DPPBlogConvert.exe`
3. Test the setup flow:
   - Click "Setup New Project"
   - Select a location (e.g., Desktop)
   - Verify DPPBlogBuilder folder is created with correct structure
4. Test the Find Project feature
5. Add a test .docx file and test conversion (requires client_secret.json)

## File Structure After Build

```
DPPBlogApp/
├── blog_converter_gui.py
├── convert_blog.py
├── README.md
├── Tags.txt
├── DPPBlogConvert.spec
├── BUILD_INSTRUCTIONS.md
├── logo.png (optional)
├── header.png (optional)
├── build/ (created during build)
└── dist/
    └── DPPBlogConvert.exe  ← Your final executable
```

## Distribution

To distribute the application:

1. Copy `DPPBlogConvert.exe` from the `dist` folder
2. Users can run it standalone without Python installed
3. On first run, users will need to:
   - Set up project folder via Setup or Find Project
   - Add their `client_secret.json` (see README.md in project folder)

## Troubleshooting Build Issues

### Missing modules
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Import errors
- Check the `hiddenimports` list in DPPBlogConvert.spec
- Add any missing modules to the list

### Icon not working
- Make sure icon file is `.ico` format (not `.png`)
- Use online converter or: `pip install pillow` then convert with Python

### File too large
- The .exe will be 30-50MB due to bundled dependencies
- This is normal for PyInstaller builds with Google API libraries

## Notes

- The built .exe includes Python interpreter and all dependencies
- No Python installation required on target machines
- First run will be slightly slower as PyInstaller unpacks files
- Antivirus may flag the .exe (false positive) - this is common with PyInstaller
