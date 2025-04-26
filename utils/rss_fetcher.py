from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import html
import re
import emoji

def clean_html_snippets(text):
    # Patterns to remove
    patterns = [
        r'^\s*ioned-image-container">\s*',  # start of line
        r'^\s*s="captioned-image-container">\s*',
        r'^\s*p>\s*',
        r'^\s*>[\s]*',
    ]
    
    # Apply all patterns
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
     # Remove the specific unwanted sentence
    unwanted_sentence = (
        "With corporate outlets , supporting independent political media is more important right now than ever. "
        "Public Notice is possible thanks to paid subscribers. "
        "If you arent one already, please click the button below and become one to support our work."
    )
    text = text.replace(unwanted_sentence, '')

    return text


def parse_timestamp(timestamp_str):
    """Parse timestamp from RSS feed with 'GMT'."""
    try:
        # Replace 'GMT' with '+0000' to make it compatible with datetime parsing
        timestamp_str = timestamp_str.replace("GMT", "+0000")
        return datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %z")
    except ValueError as e:
        print(f"Error parsing timestamp: {e}")
        return None  # Handle error appropriately


def extract_post_content(rss_xml):
    """Extract and clean content from <content:encoded> tag."""
    start_tag = "<content:encoded>"
    end_tag = "</content:encoded>"
    content_start = rss_xml.find(start_tag) + len(start_tag)
    content_end = rss_xml.find(end_tag)
    content = rss_xml[content_start:content_end].strip()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove images, buttons, and other non-content elements
    for element in soup.find_all(['img', 'a', 'button', 'div', 'figure', 'style', 'script']):
        element.decompose()  # Remove the element from the tree

    # Clean special characters and extract text
    clean_content = soup.get_text(separator=" ").strip()

    # Unescape HTML entities
    clean_content = html.unescape(clean_content) 

    # Remove HTML broken leftovers
    clean_content = re.sub(r'<[^>]+>', ' ', clean_content)
    clean_content = re.sub(r'[\s"\']*<\/?[a-zA-Z0-9\-:_]+\s*[^>]*>?', ' ', clean_content)

    # Remove emojis
    clean_content = emoji.replace_emoji(clean_content, replace='')

    # Remove non-ASCII characters
    clean_content = clean_content.encode('ascii', 'ignore').decode()

    # Remove multiple spaces
    clean_content = re.sub(r'\s+', ' ', clean_content)

    # Final cleanup
    clean_content = clean_html_snippets(clean_content)
    final_content = clean_content.strip()

    if len(final_content) == 0:
        return None
    
    return clean_content


def fetch_rss_feed(url):
    """Fetch RSS feed and return a list of new posts with relevant information."""
    feed = feedparser.parse(url)
    posts = []

    for entry in feed.entries:
        # Use the parse_timestamp function to handle 'GMT' properly
        post = {
            'post_title': entry.title,
            'author_name': entry.get('author', 'Unknown'),
            'publication_name': feed.feed.get('title', 'No Name'),
            'timestamp': parse_timestamp(entry.published),  # Use the updated function here
            'post_url': entry.link,
            'post_content': extract_post_content(entry.content[0].value) if entry.content else ''
        }
        posts.append(post)
    
    return posts


def get_new_substack_posts():
    """Fetch posts from the defined Substack blogs."""
    urls = [
        'https://robertreich.substack.com/feed',
        'https://www.publicnotice.co/feed'
    ]
    
    all_posts = []
    for url in urls:
        all_posts.extend(fetch_rss_feed(url))

    return all_posts
