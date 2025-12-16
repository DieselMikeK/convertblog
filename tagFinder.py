#!/usr/bin/env python3
"""
Tag Finder - Automatically suggest blog tags based on content
Uses hybrid fuzzy + exact matching for best results
"""

from pathlib import Path
from difflib import SequenceMatcher
import re


def load_tags(tags_file):
    """Load tags from Tags.txt file"""
    tags_path = Path(tags_file)
    if not tags_path.exists():
        print(f"Warning: Tags file not found at {tags_file}")
        return []

    with open(tags_path, 'r', encoding='utf-8') as f:
        tags = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    return tags


def extract_keywords(html_content):
    """
    Extract potential keywords from HTML content
    Removes HTML tags and filters out common stop words
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_content)

    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')

    # Remove special characters but keep hyphens, underscores, and periods (for model numbers)
    text = re.sub(r'[^\w\s\-_\.]', ' ', text)

    # Split into words and convert to lowercase
    words = text.lower().split()

    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'it', 'its', 'they', 'them', 'their', 'we', 'our', 'you', 'your'
    }

    # Filter words: must be longer than 2 chars and not a stop word
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]

    return keywords


def fuzzy_match_score(word, tag):
    """
    Calculate similarity between word and tag (0.0 to 1.0)
    Uses SequenceMatcher for fuzzy matching
    """
    return SequenceMatcher(None, word.lower(), tag.lower()).ratio()


def normalize_tag(tag):
    """
    Normalize tag for comparison (remove spaces, lowercase, etc.)
    """
    return tag.lower().replace(' ', '').replace('-', '').replace('_', '')


def find_tags(html_content, tags_list, threshold=0.80, max_tags=10):
    """
    Find matching tags from HTML content using hybrid approach

    Args:
        html_content: The HTML blog content
        tags_list: List of available tags from Tags.txt
        threshold: Minimum similarity score (0.80 = 80% match)
        max_tags: Maximum number of tags to return

    Returns:
        List of matched tags, sorted by relevance
    """
    if not tags_list:
        return []

    keywords = extract_keywords(html_content)
    tag_scores = {}

    # Create full text for phrase matching
    full_text = ' '.join(keywords)

    # Step 1: Exact phrase matching (highest confidence)
    for tag in tags_list:
        tag_normalized = normalize_tag(tag)

        # Check if tag appears in content (exact match)
        if tag.lower() in full_text or tag_normalized in full_text.replace(' ', '').replace('-', '').replace('_', ''):
            tag_scores[tag] = tag_scores.get(tag, 0) + 15  # Very high weight

    # Step 2: Multi-word tag matching (for tags like "Bully Dog", "clean diesel")
    for tag in tags_list:
        if ' ' in tag or '-' in tag:
            tag_words = re.split(r'[\s\-_]+', tag.lower())
            # If all words of the tag appear in content, it's a strong match
            if all(word in keywords for word in tag_words if len(word) > 2):
                tag_scores[tag] = tag_scores.get(tag, 0) + 12

    # Step 3: Fuzzy matching for variations and misspellings
    for keyword in keywords:
        # Skip very short keywords for fuzzy matching
        if len(keyword) < 4:
            continue

        for tag in tags_list:
            # Calculate similarity
            score = fuzzy_match_score(keyword, tag)

            # Also check if keyword contains tag or vice versa (for compound words)
            if tag.lower() in keyword or keyword in tag.lower():
                score = max(score, 0.90)

            if score >= threshold:
                # Weight by similarity score (closer match = higher weight)
                tag_scores[tag] = tag_scores.get(tag, 0) + (score * 5)

    # Step 4: Substring matching for model numbers (e.g., "6.7" matches "67cummins")
    for keyword in keywords:
        for tag in tags_list:
            # Remove dots and spaces for model number matching
            keyword_clean = keyword.replace('.', '').replace(' ', '')
            tag_clean = normalize_tag(tag)

            # Check if keyword is a substring of tag (e.g., "67" in "67cummins")
            if len(keyword_clean) >= 2 and keyword_clean in tag_clean:
                tag_scores[tag] = tag_scores.get(tag, 0) + 3

    # Sort by score (highest first) and return top N
    sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)

    # Return only the tag names (not scores)
    return [tag for tag, score in sorted_tags[:max_tags]]


def process_html_file(html_file, tags_file):
    """
    Process a single HTML file and return suggested tags

    Args:
        html_file: Path to the HTML file
        tags_file: Path to Tags.txt

    Returns:
        List of suggested tags
    """
    html_path = Path(html_file)

    if not html_path.exists():
        print(f"Warning: HTML file not found: {html_file}")
        return []

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tags_list = load_tags(tags_file)
    matched_tags = find_tags(content, tags_list)

    return matched_tags


def save_tags_file(tags, output_file):
    """
    Save tags to a text file (one per line)
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tags))


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python tagFinder.py <html_file> <tags_file>")
        print("Example: python tagFinder.py output_html/blog.html Tags.txt")
        sys.exit(1)

    html_file = sys.argv[1]
    tags_file = sys.argv[2]

    print(f"Analyzing: {html_file}")
    tags = process_html_file(html_file, tags_file)

    print(f"\nSuggested tags ({len(tags)}):")
    print(", ".join(tags))
