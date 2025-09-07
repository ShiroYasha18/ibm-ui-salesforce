import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import argparse
import logging
import os
from datetime import datetime
import time

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def log(message, level="INFO"):
    """Log a message with the specified level"""
    if level == "INFO":
        logging.info(message)
    elif level == "WARNING":
        logging.warning(message)
    elif level == "ERROR":
        logging.error(message)
    else:
        logging.info(message)

class WebsiteSpider(scrapy.Spider):
    name = 'website_spider'
    
    def __init__(self, url=None, output_file=None, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.output_file = output_file
        self.last_html = None
        log(f"Spider initialized for {url}")
    
    def parse(self, response):
        """Parse the response and extract data"""
        log(f"Scraped {response.url} (status: {response.status})")
        
        # Get the HTML content
        html = response.body.decode('utf-8')
        
        # Check if HTML has changed from last scrape
        if self.last_html and html != self.last_html:
            log(f"HTML content has changed since last scrape", "INFO")
        
        # Save the HTML if output file is specified
        if self.output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_file.split('.')[0]}_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            log(f"HTML saved to {filename}")
        else:
            # Print the first 500 characters of the HTML
            self.logger.info(f"\nHTML Content (first 500 chars):\n{html[:500]}...\n")
            self.logger.info(f"Total length: {len(html)} characters")
        
        self.last_html = html
        
        # Extract all links for potential crawling
        links = response.css('a::attr(href)').getall()
        log(f"Found {len(links)} links on the page")
        
        # Extract all images
        images = response.css('img::attr(src)').getall()
        log(f"Found {len(images)} images on the page")
        
        # Extract all text content
        texts = response.css('body ::text').getall()
        cleaned_texts = [text.strip() for text in texts if text.strip()]
        log(f"Extracted {len(cleaned_texts)} text elements")
        
        # You can yield data here if you want to process it further
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'links_count': len(links),
            'images_count': len(images),
            'text_elements_count': len(cleaned_texts)
        }

def run_spider(url, output_file=None, interval=None, num_scrapes=1, follow_links=False, depth=1):
    """Run the spider to scrape the website
    
    Args:
        url (str): The URL to scrape
        output_file (str, optional): File to save the HTML to
        interval (int, optional): Time in seconds between scrapes
        num_scrapes (int or float, optional): Number of times to scrape the site, can be float('inf') for infinite
        follow_links (bool, optional): Whether to follow links on the page
        depth (int, optional): Maximum depth to crawl if following links
    """
    log(f"Starting Scrapy spider for {url}")
    
    i = 0
    while i < num_scrapes:
        log(f"Starting scrape {i+1}/{num_scrapes if num_scrapes != float('inf') else 'infinite'}")
        
        # Configure the settings
        settings = get_project_settings()
        settings.update({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 1,  # Be nice to the websites
            'COOKIES_ENABLED': True,
            'CONCURRENT_REQUESTS': 1,
            'LOG_LEVEL': 'INFO',
        })
        
        if follow_links:
            settings.update({
                'DEPTH_LIMIT': depth,
                'DEPTH_PRIORITY': 1,
            })
        else:
            settings.update({
                'DEPTH_LIMIT': 0,  # Don't follow links
            })
        
        # Create and run the crawler process
        process = CrawlerProcess(settings)
        process.crawl(WebsiteSpider, url=url, output_file=output_file)
        process.start()  # This blocks until the crawling is finished
        process.stop()
        
        i += 1
        
        # If we're doing multiple scrapes with an interval
        if interval and i < num_scrapes:
            log(f"Waiting {interval} seconds before next scrape...")
            time.sleep(interval)
    
    if num_scrapes != float('inf'):
        log(f"Completed {num_scrapes} scrapes of {url}")
    else:
        log(f"Scraping stopped after {i} scrapes of {url}")

def main():
    parser = argparse.ArgumentParser(description='Scrape websites using Scrapy')
    parser.add_argument('url', help='The URL to scrape')
    parser.add_argument('-o', '--output', help='Base filename to save the HTML to')
    parser.add_argument('-i', '--interval', type=int, help='Time in seconds between scrapes for monitoring changes')
    parser.add_argument('-n', '--num-scrapes', type=int, default=1, help='Number of times to scrape the site')
    parser.add_argument('--infinite', action='store_true', help='Run scraper indefinitely at specified interval')
    parser.add_argument('-f', '--follow-links', action='store_true', help='Follow links on the page')
    parser.add_argument('-d', '--depth', type=int, default=1, help='Maximum depth to crawl if following links')
    
    args = parser.parse_args()
    
    # If infinite flag is set, override num_scrapes
    if args.infinite and args.interval:
        num_scrapes = float('inf')  # Set to infinity
    else:
        num_scrapes = args.num_scrapes
    
    run_spider(
        args.url, 
        args.output, 
        args.interval, 
        num_scrapes,
        args.follow_links,
        args.depth
    )

if __name__ == "__main__":
    main()