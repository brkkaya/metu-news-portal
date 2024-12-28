from bs4 import BeautifulSoup
import jsonlines
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import parser
from tqdm import tqdm


def parse_xml_to_jsonl(xml_string):
    """
    Parses an XML string containing URLs and last modification dates,
    and returns a JSONL string with links and dates.

    Args:
    xml_string: The XML string to parse.

    Returns:
        A string containing the JSONL representation of the links and dates.
    """
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
       print(f"Error parsing XML: {e}")
       return ""

    # Extract the URLs and dates, accommodating the namespace
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    url_entries = []
    for url_element in root.findall('ns:url', namespace):
        loc_element = url_element.find('ns:loc', namespace)
        lastmod_element = url_element.find('ns:lastmod', namespace)
        if loc_element is not None and lastmod_element is not None:
              url_entries.append({
                 "link": loc_element.text,
                 "date": lastmod_element.text
             })
    
    # Convert the list of dictionaries to a JSONL string
    return url_entries

def get_urls(sitemap_url, output_path):

    # Load and parse the sitemap
    response = requests.get(sitemap_url)
    response.raise_for_status()

    url_entries = parse_xml_to_jsonl(response.text)

    with jsonlines.open(output_path, "w") as writer:
        writer.write_all(url_entries)


def pull_url(url):
    response = requests.get(url)
    response.raise_for_status()    

    soup = BeautifulSoup(response.content, 'html.parser')

    line = {"title": "", "url": url, "img_url": "", "excerpt": "", "author": "METU News", "body": "", "date": ""}

    title = soup.select_one("article > div:nth-child(1) > header > h1")
    if title:
        line["title"] = title.text.strip()

    # Use a CSS selector to find the `h1`
    # Extract Excerpt
    excerpt = soup.select_one("article > div:nth-child(1) > header > p")
    if excerpt:
        line["excerpt"] = excerpt.text.strip()

    # Extract Image URL
    image = soup.select_one("article > div:nth-child(3) > div img")
    if image and image.has_attr("src"):
        line["img_url"] = image["src"]

    # Extract Body Text (Multiple <p> tags)
    body_paragraphs = soup.select("article > div:nth-child(3) > p")
    body_string = ""
    for paragraph in body_paragraphs:
        body_string = body_string + "\n" + paragraph.text.strip()
    line["body"] = body_string

    return line

def is_within_last_4_months(date_string):
    # Parse the input date
    input_date = parser.parse(date_string)
    
    # Get the current date and time
    now = datetime.now(input_date.tzinfo)  # Retain the same timezone as the input
    
    # Calculate the date 4 months ago
    four_months_ago = now - timedelta(days=365)  # Approximate 4 months as 120 days
    
    # Check if the input date is within the last 4 months
    return four_months_ago <= input_date <= now

def main():
    sitemap_path = "https://haber.metu.edu.tr/en/wp-sitemap-posts-post-1.xml"
    output_path = "metu_news.jsonl"
    scrape_path = "metu_scrape.jsonl"

    get_urls(sitemap_path, output_path)

    scrape_lines = []

    with jsonlines.open(output_path) as reader:
        for obj in tqdm(reader):
            if is_within_last_4_months(obj["date"]): 
                line = pull_url(obj["link"])
                line["date"] = obj["date"]
                scrape_lines.append(line)
    
    with jsonlines.open(scrape_path, "w") as writer:
        writer.write_all(scrape_lines)

if __name__ == "__main__":



    main()