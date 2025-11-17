# ConvertBlog

A Python script that converts .docx files to clean HTML using Google Drive API. Designed for converting blog articles with specific formatting requirements.

## Features

- Converts .docx files to HTML via Google Drive API
- Removes Google Docs inline styles and cleans HTML structure
- Preserves nested lists from Google Docs
- Normalizes strong tag formatting in list items
- Removes empty table cells while preserving intentional blanks
- Converts first H1 to H2 with custom styling
- Removes marker text and notes sections
- Applies consistent text and link colors
- Adds table styling with borders

## Setup

1. Install required packages:
```bash
python -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4
```

2. Set up Google Drive API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `client_secret.json` in the script folder

3. Create required folders:
   - `todo/` - Place .docx files here for conversion
   - `output_html/` - Cleaned HTML output (auto-created)
   - `raw_html/` - Raw Google Docs HTML (auto-created)

## Usage

```bash
python convert_blog.py
```

The script will:
1. Find all .docx files in the `todo/` folder
2. Upload each to Google Drive and convert to HTML
3. Apply cleaning transformations
4. Save both raw and cleaned HTML versions
5. Delete the temporary Google Drive files

## Output

- **Raw HTML**: Unprocessed HTML from Google Docs (`raw_html/`)
- **Cleaned HTML**: Formatted and cleaned HTML ready for publishing (`output_html/`)

## Configuration

Edit `convert_blog.py` to customize:
- `OUTPUT_FOLDER` - Where cleaned HTML is saved
- `RAW_FOLDER` - Where raw HTML is saved
- `SAFE_ATTRS` - HTML attributes to preserve during cleaning

## Requirements

- Python 3.6+
- Google Drive API credentials
- Internet connection for Google Drive API calls
