


          
# IBM UI Salesforce Simulation

This project simulates a system that randomly switches between visually identical HTML scripts and monitors if these changes are detected. The HTML extractor runs every 20 seconds to check for changes.

## Features

- Two visually identical HTML pages with different underlying code
- Automatic HTML switching at random intervals
- HTML extractor that runs every 20 seconds
- Backend system to flag HTML changes
- Logging system to track changes and detections
- User-configurable simulation duration
- Summary report generation

## Requirements

- Python 3.6+
- Flask

## How to Run

1. Make sure you have Python installed
2. Run the simulation script:
   ```bash
   python run_simulation.py
   ```

## Web Scraper Usage

1. Save to file - Scrape a website and save the HTML:
   ```bash
   python web_scraper.py "https://example.com" -o example.html
   ```

2. Monitor for changes - Scrape every 60 seconds, 5 times:
   ```bash
   python web_scraper.py "https://example.com" -o example.html -i 60 -n 5
   ```

3. Crawl the website - Follow links up to depth 2:
   ```bash
   python web_scraper.py "https://example.com" -o example.html -f -d 2
   ```
4. Crawl the website every 2 minutes infinitely:
   ```bash
   python web_scraper.py "https://example.com" -o example.html -f -d 2 -i 120 --infinite
   ```

## Note
-Update html files for simulation in server.py once the newer html files are saved in the output folder



## Dependencies



You'll need to install Scrapy:
```bash
pip install scrapy
```
        