import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

# Function to save content to a single file
def save_content(filename, content):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content + "\n\n")

# Function to scrape a single page and return its content and links
def scrape_page(url, base_url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract the title for the section header
        title = soup.title.string if soup.title else 'untitled'
        title = title.replace('/', '_').replace('\\', '_')  # Sanitize title
        # Save the page content as text in the output file
        page_content = f"Title: {title}\nURL: {url}\n\n{soup.get_text()}"
        save_content(output_file, page_content)
        # Extract and return all links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Normalize and filter URLs
            href = urljoin(base_url, href)
            parsed_href = urlparse(href)
            if parsed_href.scheme in ['http', 'https']:
                href = parsed_href._replace(fragment='').geturl()  # Remove fragment
                links.append(href)
        return links
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

# Function to crawl links and scrape each page
def crawl_and_scrape(start_url, base_url, output_file, max_depth=2, max_pages=50):
    visited = set()
    to_visit = [(start_url, 0)]
    pages_scraped = 0

    while to_visit and pages_scraped < max_pages:
        current_url, depth = to_visit.pop(0)
        if current_url not in visited and depth <= max_depth:
            visited.add(current_url)
            links = scrape_page(current_url, base_url, output_file)
            pages_scraped += 1
            for link in links:
                if base_url in link and link not in visited:
                    to_visit.append((link, depth + 1))

# Main script
def main():
    url_file = input("Enter the path to the text file with URLs (leave blank to enter a URL manually): ").strip()
    output_file = "consolidated_content.txt"
    
    if url_file:
        try:
            with open(url_file, 'r') as file:
                urls = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"File not found: {url_file}")
            return
    else:
        urls = [input("Enter the URL to start scraping: ").strip()]

    # Clear the output file before starting
    open(output_file, 'w').close()

    for url in urls:
        base_url = '/'.join(url.split('/')[:3])  # Extract base URL
        crawl_and_scrape(url, base_url, output_file)

if __name__ == "__main__":
    main()