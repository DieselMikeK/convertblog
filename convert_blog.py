# convert_blog.py

# Uploads .docx files to Google Docs, exports HTML, cleans excess formatting but preserves bold text and structure.

import os
import re
import io
import pickle
from bs4 import BeautifulSoup, NavigableString, Tag
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ==== CONFIGURATION ====

SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'  # make sure this exists in script folder
TOKEN_FILE = 'token.pickle'
OUTPUT_FOLDER = 'output_html'
RAW_FOLDER = 'raw_html'
SAFE_ATTRS = {"href", "aria-level", "role", "class"}

# ==== AUTHENTICATION ====

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not getattr(creds, "valid", False):
        if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

# ==== CLEANUP HELPERS ====

def remove_everything_before_marker(soup):
    """
    Remove everything above and including the 'Begin writing the article below the line break' marker
    and the <hr> that follows it.
    """
    marker_re = re.compile(r"begin writing the article below the line break", re.I)
    marker_node = None
    for text_node in soup.find_all(string=marker_re):
        marker_node = text_node
        break
    if not marker_node:
        return

    # Find the paragraph containing the marker
    container = marker_node.parent
    while container and container.name not in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        container = container.parent
        if not container or container.name == 'body':
            container = marker_node.parent
            break

    body = soup.body or soup

    # Remove all previous siblings of the container
    for sibling in list(container.previous_siblings):
        try:
            sibling.decompose()
        except Exception:
            try:
                sibling.extract()
            except Exception:
                pass

    # Find and remove the next <hr> after the container
    next_elem = container.next_sibling
    hr_found = False
    while next_elem:
        if hasattr(next_elem, 'name'):
            if next_elem.name == 'hr':
                try:
                    next_elem.decompose()
                    hr_found = True
                except Exception:
                    pass
                break
            else:
                # Stop if we hit another element that's not whitespace
                if next_elem.name:
                    break
        next_elem = next_elem.next_sibling if next_elem else None

    # Remove the container itself (the paragraph with the marker)
    try:
        container.decompose()
    except Exception:
        try:
            container.extract()
        except Exception:
            pass

def convert_bold_italic_spans(soup):
    """
    Convert spans/font tags that declare bold/italic into <strong>/<em> respectively.
    """
    for tag in list(soup.find_all(["span", "font"])):
        style = tag.get("style", "") or ""
        is_bold = False
        is_italic = False
        if re.search(r'font-weight\s*:\s*(700|bold)', style, re.I) or tag.name == "b":
            is_bold = True
        if re.search(r'font-style\s*:\s*italic', style, re.I) or tag.name == "i":
            is_italic = True

        if is_bold or is_italic:
            new_inner = None
            children = list(tag.contents)
            if is_bold:
                strong = soup.new_tag("strong")
                for c in children:
                    strong.append(c.extract() if isinstance(c, Tag) else c)
                new_inner = strong
            if is_italic:
                if new_inner:
                    em = soup.new_tag("em")
                    em.append(new_inner)
                    new_inner = em
                else:
                    em = soup.new_tag("em")
                    for c in children:
                        em.append(c.extract() if isinstance(c, Tag) else c)
                    new_inner = em
            if new_inner:
                tag.replace_with(new_inner)
                continue

def normalize_heading_markers(soup):
    """
    Convert text patterns like '(H1)', 'H1:', etc. into real headings.
    """
    pattern = re.compile(r'^\s*\(?h([1-6])\)?[:=\-\s]+(.+)$', re.I)
    for text_node in list(soup.find_all(string=True)):
        if not isinstance(text_node, NavigableString):
            continue
        raw = text_node.strip()
        if not raw:
            continue
        m = pattern.match(raw)
        if not m:
            continue
        level = int(m.group(1))
        content = m.group(2).strip()
        new_tag = soup.new_tag(f"h{level}")
        new_tag.string = content
        parent = text_node.parent
        if parent and parent.name not in [f"h{i}" for i in range(1, 7)]:
            try:
                parent.replace_with(new_tag)
            except Exception:
                text_node.replace_with(new_tag)
        else:
            text_node.replace_with(new_tag)

def flatten_nested_headings(soup):
    """Flatten nested headings like <h4><h1>...</h1></h4>."""
    for outer in list(soup.find_all(re.compile(r"^h[1-6]$", re.I))):
        inner = outer.find(re.compile(r"^h[1-6]$", re.I))
        if inner:
            outer.replace_with(inner)

def strip_styles_and_attributes(soup):
    """Remove <style> tags and inline styles; keep only safe attributes."""
    for style_tag in soup.find_all("style"):
        style_tag.decompose()
    for tag in soup.find_all(True):
        kept = {}
        for k, v in list(tag.attrs.items()):
            if k in SAFE_ATTRS:
                kept[k] = v
        tag.attrs = kept

def unwrap_spans_and_fonts(soup):
    """Unwrap remaining span/font tags after bold/italic conversion."""
    for tag in list(soup.find_all(["span", "font"])):
        try:
            tag.unwrap()
        except Exception:
            pass

def remove_empty_meta_and_images(soup):
    """Remove meta/script tags and blank images."""
    for tag in soup.find_all(["meta", "script"]):
        try:
            tag.decompose()
        except Exception:
            pass
    for img in list(soup.find_all("img")):
        if not img.get("src"):
            try:
                img.decompose()
            except Exception:
                pass

def fix_google_redirect_links(soup):
    """Replace 'https://www.google.com/url?q=' with the real destination URL.
    Skips YouTube links to preserve URL encoding."""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        match = re.search(r"https://www\.google\.com/url\?q=([^&]+)", href)
        if match:
            decoded_url = match.group(1)
            # Skip YouTube links to preserve their URL encoding
            if 'youtube.com' not in decoded_url and 'youtu.be' not in decoded_url:
                a["href"] = decoded_url

def fix_specific_links(soup):
    """Replace specific URLs with updated versions."""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Replace old contact page URL with new one
        if href == "https://www.dieselpowerproducts.com/t-contact.aspx":
            a["href"] = "https://dieselpowerproducts.com/pages/contact-us"

def remove_empty_paragraphs(soup):
    """Remove <p> tags that are empty or contain only nbsp."""
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if not text or text == "\xa0":
            try:
                p.decompose()
            except Exception:
                pass

def remove_notes_section(soup):
    """Remove 'Notes' section and everything that follows."""
    notes_heading = soup.find(
        lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and "notes" in tag.get_text(strip=True).lower()
    )
    if notes_heading:
        # Remove all following siblings (elements after the Notes heading at the same level)
        for elem in list(notes_heading.find_next_siblings()):
            try:
                elem.decompose()
            except Exception:
                pass
        # Remove the Notes heading itself
        try:
            notes_heading.decompose()
        except Exception:
            pass

def preserve_list_structure(soup):
    """
    Convert Google Docs flat list structure to proper nested HTML lists.
    Google Docs exports nested lists as sibling <ul> tags with class indicators
    like 'lst-kix_list_9-0' (level 0), 'lst-kix_list_9-1' (level 1), etc.
    """
    import re

    # Find all ul tags
    all_lists = soup.find_all('ul')

    # Pattern to extract list ID and level from Google Docs classes
    # e.g., 'lst-kix_list_9-1' -> list_id='9', level=1
    list_class_pattern = re.compile(r'lst-kix_list_(\d+)-(\d+)')

    # Track processed lists to avoid double-processing
    processed = set()

    for ul in all_lists:
        if ul in processed:
            continue

        # Get class attribute
        classes = ul.get('class', [])
        if not classes:
            continue

        # Find the list class with level info
        list_id = None
        level = None
        for cls in classes:
            match = list_class_pattern.match(cls)
            if match:
                list_id = match.group(1)
                level = int(match.group(2))
                break

        if list_id is None or level == 0:
            # This is a top-level list, continue
            continue

        # This is a nested list (level > 0)
        # Find the previous list with the same list_id and level-1
        parent_level = level - 1
        parent_pattern = re.compile(rf'lst-kix_list_{list_id}-{parent_level}')

        # Search backwards through previous siblings to find parent list
        parent_ul = None
        sibling = ul.previous_sibling

        while sibling:
            if hasattr(sibling, 'name') and sibling.name == 'ul':
                sibling_classes = sibling.get('class', [])
                for cls in sibling_classes:
                    if parent_pattern.match(cls):
                        parent_ul = sibling
                        break
                if parent_ul:
                    break
            sibling = sibling.previous_sibling

        if parent_ul:
            # Find the last <li> in the parent list
            parent_lis = parent_ul.find_all('li', recursive=False)
            if parent_lis:
                last_li = parent_lis[-1]

                # Move the nested ul into the last li of the parent
                ul_extract = ul.extract()
                last_li.append(ul_extract)
                processed.add(ul_extract)

# ==== MAIN CLEANUP PIPELINE ====

def add_table_styling(soup):
    """Add basic styling to tables for better appearance."""
    for table in soup.find_all("table"):
        table["style"] = "border-collapse: collapse; width: 100%; margin: 20px 0;"
        for td in table.find_all(["td", "th"]):
            td["style"] = "border: 1px solid #ddd; padding: 8px;"
        for th in table.find_all("th"):
            th["style"] = "border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2; font-weight: bold;"

def remove_trailing_hr(soup):
    """Remove the last <hr> at the bottom of the page."""
    body = soup.body or soup
    all_hrs = body.find_all("hr")
    if all_hrs:
        # Remove the last hr
        try:
            all_hrs[-1].decompose()
        except Exception:
            pass

def remove_blank_paragraphs_before_headings(soup):
    """Remove empty <p> tags that appear directly before heading tags."""
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        prev_sibling = heading.previous_sibling
        # Check previous siblings for empty p tags
        while prev_sibling:
            if hasattr(prev_sibling, 'name'):
                if prev_sibling.name == 'p':
                    text = prev_sibling.get_text(strip=True)
                    if not text or text == "\xa0":
                        temp = prev_sibling.previous_sibling
                        try:
                            prev_sibling.decompose()
                        except:
                            pass
                        prev_sibling = temp
                        continue
                break
            prev_sibling = prev_sibling.previous_sibling

def convert_first_h1_to_h2(soup):
    """Convert the first <h1> to <h2 class="h1"> with larger font size."""
    first_h1 = soup.find('h1')
    if first_h1:
        h2 = soup.new_tag('h2')
        h2['class'] = 'h1'
        h2['style'] = 'font-size: 2em; font-weight: bold;'
        # Move all children from h1 to h2
        for child in list(first_h1.children):
            h2.append(child)
        first_h1.replace_with(h2)

def apply_text_and_link_colors(soup):
    """Make all text black and links blue."""
    # Add style to body for black text
    if soup.body:
        soup.body['style'] = 'color: #000000;'

    # Make all links blue
    for link in soup.find_all('a'):
        link['style'] = 'color: #0000EE;'

def remove_all_empty_tags(soup):
    """Remove all empty tags throughout the document (final cleanup pass)."""
    # Keep running until no more empty tags are found
    # (some tags may become empty after their children are removed)
    changed = True
    while changed:
        changed = False
        for tag in soup.find_all(True):
            # Skip tags that are allowed to be empty
            # Include td and th to preserve table structure
            if tag.name in ['br', 'hr', 'img', 'input', 'meta', 'link', 'td', 'th']:
                continue

            # Check if tag is empty (no text and no non-empty children)
            text = tag.get_text(strip=True)
            if not text or text == "\xa0":
                # Check if it has any meaningful children (like images, etc)
                has_content = False
                for child in tag.children:
                    if hasattr(child, 'name') and child.name in ['img', 'br', 'hr']:
                        has_content = True
                        break

                if not has_content:
                    try:
                        tag.decompose()
                        changed = True
                    except:
                        pass

def unwrap_headings_from_paragraphs(soup):
    """If a heading is wrapped in a paragraph tag, unwrap it."""
    for p in list(soup.find_all('p')):
        # Check if this paragraph only contains a single heading
        headings = p.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) == 1:
            # Check if the paragraph only contains this one heading (and whitespace)
            other_content = False
            for child in p.children:
                if hasattr(child, 'name'):
                    if child.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        other_content = True
                        break
                else:
                    # It's text - check if it's just whitespace
                    if str(child).strip():
                        other_content = True
                        break

            if not other_content:
                # Replace the paragraph with just the heading
                heading = headings[0]
                p.replace_with(heading)

def fix_strong_tag_spacing(soup):
    """Fix spacing issues with strong tags - remove spaces inside tags and fix spacing after."""
    for strong in soup.find_all('strong'):
        # Get the text content
        text = strong.get_text()
        # Strip leading/trailing spaces from inside the strong tag
        stripped_text = text.strip()

        if stripped_text != text:
            # Replace the content with stripped version
            strong.clear()
            strong.string = stripped_text

        # Check the next sibling for spacing
        next_sibling = strong.next_sibling
        if next_sibling and isinstance(next_sibling, str):
            # If next character is punctuation, remove space before it
            if next_sibling.startswith(' ') and len(next_sibling) > 1:
                next_char = next_sibling[1] if len(next_sibling) > 1 else ''
                if next_char in '.,;:!?)':
                    # Remove the space before punctuation
                    next_sibling.replace_with(next_sibling[1:])

def fix_strong_in_list_items(soup):
    """
    Ensure consistency with strong tags in list items:
    1. If next sibling text starts with separating punctuation (:, ?, -, ,, etc.), move it inside the strong tag
    2. Remove nbsp and ensure single space after </strong> before the next text

    Fixes cases like:
    - <li><strong>Label</strong>: Text</li> → <li><strong>Label:</strong> Text</li>
    - <li><strong>Label</strong>, Text</li> → <li><strong>Label,</strong> Text</li>
    - <li><strong>Label:</strong>Text</li> → <li><strong>Label:</strong> Text</li>
    """
    # Punctuation that separates strong text from the rest of the list item
    SEPARATOR_PUNCTUATION = (':', '?', '-', '—', ',')

    for li in soup.find_all('li'):
        # Check if the first child is a strong tag
        first_child = None
        for child in li.children:
            if hasattr(child, 'name'):
                first_child = child
                break
            elif isinstance(child, str) and child.strip():
                # If first non-empty content is text, not a tag, skip this li
                break

        if first_child and first_child.name == 'strong':
            # Check what comes after the strong tag
            next_sibling = first_child.next_sibling

            if next_sibling and isinstance(next_sibling, str):
                # First, clean up nbsp and extra spaces
                # Replace nbsp (U+00A0) with regular space
                cleaned_text = next_sibling.replace('\xa0', ' ')

                # Collapse multiple spaces into single space
                import re
                cleaned_text = re.sub(r' +', ' ', cleaned_text)

                # Case 1: If text starts with separator punctuation, move it inside the strong tag
                if cleaned_text and cleaned_text[0] in SEPARATOR_PUNCTUATION:
                    separator = cleaned_text[0]

                    # Get current strong text
                    strong_text = first_child.get_text()

                    # Add separator to strong tag if it doesn't already have it
                    if not strong_text.endswith(separator):
                        first_child.clear()
                        first_child.string = strong_text + separator

                    # Remove the separator from the next sibling
                    remaining_text = cleaned_text[1:]  # Remove first character (separator)

                    # Ensure single space after the separator
                    remaining_text = remaining_text.lstrip()
                    # Always add a space if there's content OR if the next element is a tag (like <a>)
                    if remaining_text:
                        if not remaining_text.startswith('\n'):
                            remaining_text = ' ' + remaining_text
                    else:
                        # Empty after removing separator - check if next sibling after text is a tag
                        next_elem = next_sibling.next_sibling if next_sibling else None
                        if next_elem and hasattr(next_elem, 'name'):
                            # Next element is a tag, ensure there's a space
                            remaining_text = ' '

                    next_sibling.replace_with(remaining_text)

                # Case 2: Just clean up spacing
                else:
                    # Ensure single space at the start if text doesn't start with newline
                    cleaned_text = cleaned_text.lstrip()
                    if cleaned_text and not cleaned_text.startswith('\n'):
                        cleaned_text = ' ' + cleaned_text

                    if cleaned_text != next_sibling:
                        next_sibling.replace_with(cleaned_text)

            # Check if next sibling (skipping empty text nodes) is a link tag
            check_sibling = first_child.next_sibling
            while check_sibling:
                if isinstance(check_sibling, str):
                    # If it's a non-empty text node, we're done checking
                    if check_sibling.strip():
                        break
                    # Skip empty text nodes and keep looking
                    check_sibling = check_sibling.next_sibling
                elif hasattr(check_sibling, 'name') and check_sibling.name == 'a':
                    # Found an <a> tag - ensure there's a space before it
                    from bs4 import NavigableString
                    # Check if there's already a space
                    prev = check_sibling.previous_sibling
                    has_space = prev and isinstance(prev, str) and prev.strip() == ''
                    # If previous sibling is the strong tag directly, add space
                    if prev == first_child or not has_space:
                        check_sibling.insert_before(NavigableString(' '))
                    break
                else:
                    # Hit another tag that's not a link
                    break

def normalize_link_spacing(soup):
    """
    Normalize spacing around <a> tags to ensure consistent formatting:
    - Single space before link if preceded by text/punctuation
    - Single space after link if followed by text
    - Replace nbsp with regular spaces
    - Handle links inside strong tags and between strong tags
    """
    import re
    from bs4 import NavigableString

    for link in soup.find_all('a'):
        # Check if link is inside a strong tag
        parent_strong = link.parent if link.parent and link.parent.name == 'strong' else None

        if parent_strong:
            # Handle spacing around the strong tag that contains the link
            prev_sibling = parent_strong.previous_sibling
            if prev_sibling and isinstance(prev_sibling, str):
                # Replace nbsp with regular space
                cleaned = prev_sibling.replace('\xa0', ' ')
                cleaned = re.sub(r' +', ' ', cleaned)

                if cleaned:
                    cleaned = cleaned.rstrip()
                    if cleaned and not cleaned.endswith('\n'):
                        cleaned = cleaned + ' '

                    if cleaned != prev_sibling:
                        prev_sibling.replace_with(cleaned)
            elif prev_sibling and hasattr(prev_sibling, 'name') and prev_sibling.name == 'strong':
                # Previous sibling is also a strong tag, ensure space between them
                # Check if there's a text node between them
                if prev_sibling.next_sibling == parent_strong:
                    # No space between, insert one
                    parent_strong.insert_before(NavigableString(' '))

            next_sibling = parent_strong.next_sibling
            if next_sibling and isinstance(next_sibling, str):
                cleaned = next_sibling.replace('\xa0', ' ')
                cleaned = re.sub(r' +', ' ', cleaned)

                if cleaned:
                    cleaned = cleaned.lstrip()
                    if cleaned and not cleaned[0] in '.,;:!?)}\n':
                        cleaned = ' ' + cleaned

                    if cleaned != next_sibling:
                        next_sibling.replace_with(cleaned)
            elif next_sibling and hasattr(next_sibling, 'name') and next_sibling.name == 'strong':
                # Next sibling is also a strong tag, ensure space between them
                if parent_strong.next_sibling == next_sibling:
                    # No space between, insert one
                    parent_strong.insert_after(NavigableString(' '))
        else:
            # Link is not inside a strong tag - handle normally
            prev_sibling = link.previous_sibling
            if prev_sibling and isinstance(prev_sibling, str):
                # Replace nbsp with regular space
                cleaned = prev_sibling.replace('\xa0', ' ')
                # Collapse multiple spaces
                cleaned = re.sub(r' +', ' ', cleaned)

                # If there's text before the link, ensure single space at the end
                # Store original to check if it was just whitespace
                was_just_whitespace = cleaned.strip() == ''

                if cleaned and not was_just_whitespace:
                    # Remove trailing spaces
                    cleaned = cleaned.rstrip()
                    # Add single space if there's actual content
                    if cleaned and not cleaned.endswith('\n'):
                        cleaned = cleaned + ' '

                    if cleaned != prev_sibling:
                        prev_sibling.replace_with(cleaned)
                elif was_just_whitespace:
                    # Previous sibling is just whitespace - preserve as single space
                    if prev_sibling != ' ':
                        prev_sibling.replace_with(' ')

            # Process next sibling
            next_sibling = link.next_sibling
            if next_sibling and isinstance(next_sibling, str):
                # Replace nbsp with regular space
                cleaned = next_sibling.replace('\xa0', ' ')
                # Collapse multiple spaces
                cleaned = re.sub(r' +', ' ', cleaned)

                # If there's text after the link, ensure single space at the start
                if cleaned:
                    # Remove leading spaces
                    cleaned = cleaned.lstrip()
                    # Add single space if there's actual content and it doesn't start with punctuation or newline
                    if cleaned and not cleaned[0] in '.,;:!?)}\n':
                        cleaned = ' ' + cleaned

                    if cleaned != next_sibling:
                        next_sibling.replace_with(cleaned)

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")

    convert_bold_italic_spans(soup)
    strip_styles_and_attributes(soup)
    remove_everything_before_marker(soup)
    normalize_heading_markers(soup)
    flatten_nested_headings(soup)
    unwrap_headings_from_paragraphs(soup)
    unwrap_spans_and_fonts(soup)
    preserve_list_structure(soup)
    remove_empty_meta_and_images(soup)
    fix_google_redirect_links(soup)
    fix_specific_links(soup)
    remove_empty_paragraphs(soup)
    remove_notes_section(soup)
    remove_trailing_hr(soup)
    remove_blank_paragraphs_before_headings(soup)
    convert_first_h1_to_h2(soup)
    apply_text_and_link_colors(soup)
    add_table_styling(soup)
    remove_all_empty_tags(soup)  # Final cleanup pass to remove all empty tags
    fix_strong_tag_spacing(soup)  # Run after prettify won't interfere
    fix_strong_in_list_items(soup)  # Ensure space after strong tags in list items
    normalize_link_spacing(soup)  # Ensure consistent spacing around links

    # Use str() instead of prettify() to avoid adding extra whitespace
    html_output = str(soup)
    return html_output

# ==== DRIVE CONVERSION ====

def convert_docx_to_html(drive_service, input_path, output_folder, raw_folder):
    filename = os.path.basename(input_path)
    print(f"\nUploading {filename} to Google Drive...")

    file_metadata = {"name": filename, "mimeType": "application/vnd.google-apps.document"}
    media = MediaFileUpload(
        input_path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = uploaded.get("id")

    try:
        html_bytes = drive_service.files().export(fileId=file_id, mimeType="text/html").execute()
        html_content = html_bytes.decode("utf-8") if isinstance(html_bytes, bytes) else html_bytes
    except Exception as e:
        try:
            drive_service.files().delete(fileId=file_id).execute()
        except Exception:
            pass
        raise e

    try:
        drive_service.files().delete(fileId=file_id).execute()
    except Exception:
        pass

    # Save raw HTML first
    os.makedirs(raw_folder, exist_ok=True)
    raw_output_path = os.path.join(raw_folder, f"{os.path.splitext(filename)[0]}.html")
    with open(raw_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved raw HTML -> {raw_output_path}")

    # Clean and save cleaned HTML
    cleaned_html = clean_html(html_content)

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

    print(f"Saved cleaned HTML -> {output_path}")

# ==== MAIN ====

def main():
    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    script_folder = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_folder, "todo")
    output_folder = os.path.join(script_folder, OUTPUT_FOLDER)
    raw_folder = os.path.join(script_folder, RAW_FOLDER)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(raw_folder, exist_ok=True)

    if not os.path.exists(input_folder):
        print(f"Error: 'todo' folder not found at {input_folder}")
        return

    print("Starting Google Docs -> HTML export...")

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            try:
                convert_docx_to_html(drive_service, input_path, output_folder, raw_folder)
            except Exception as e:
                print(f"Error converting {filename}: {e}")

    print("\nAll files processed!")
    print(f"Raw HTML: {raw_folder}")
    print(f"Cleaned HTML: {output_folder}")

if __name__ == "__main__":
    main()
