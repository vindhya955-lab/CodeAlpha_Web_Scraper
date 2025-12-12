import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from datetime import datetime

# ================================================
# LOGGING SETUP
# ================================================
logging.basicConfig(
    filename="scraper_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Scraper Started")

# ================================================
# FUNCTION TO FETCH WEBPAGE
# ================================================
def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info(f"Fetched: {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

# ================================================
# FUNCTION TO PARSE HTML AND EXTRACT DATA
# ================================================
def parse_quotes(html):
    soup = BeautifulSoup(html, "html.parser")
    quotes_data = []

    quotes = soup.find_all("div", class_="quote")

    for q in quotes:
        try:
            text = q.find("span", class_="text").get_text(strip=True)
            author = q.find("small", class_="author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in q.find_all("a", class_="tag")]

            quotes_data.append({
                "quote": text,
                "author": author,
                "tags": ", ".join(tags)
            })

        except Exception as e:
            logging.error(f"Error parsing quote data: {e}")

    return quotes_data

# ================================================
# FUNCTION TO CHECK NEXT PAGE
# ================================================
def get_next_page(html):
    soup = BeautifulSoup(html, "html.parser")
    next_btn = soup.find("li", class_="next")

    if next_btn:
        next_page = next_btn.find("a")["href"]
        return "https://quotes.toscrape.com" + next_page
    return None

# ================================================
# SAVE DATA TO CSV
# ================================================
def save_to_csv(data, filename="quotes_dataset.csv"):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["quote", "author", "tags"])
            writer.writeheader()
            writer.writerows(data)
        logging.info("CSV saved successfully")
    except Exception as e:
        logging.error(f"Error writing CSV: {e}")


# ================================================
# MAIN FUNCTION
# ================================================
def scrape_all_pages():
    base_url = "https://quotes.toscrape.com/"
    all_data = []

    current_url = base_url

    while current_url:
        print(f"Scraping: {current_url}")
        html = fetch_page(current_url)

        if html:
            page_data = parse_quotes(html)
            all_data.extend(page_data)
            current_url = get_next_page(html)
        else:
            break

        time.sleep(1)  # polite delay

    save_to_csv(all_data)
    print("\nScraping Completed Successfully!")
    print(f"Total Quotes Extracted: {len(all_data)}")
    logging.info("Scraper Finished")


# ================================================
# RUN SCRAPER
# ================================================
if __name__ == "__main__":
    print("===== QUOTES SCRAPER STARTED =====")
    start = datetime.now()

    scrape_all_pages()

    end = datetime.now()
    print(f"Time Taken: {end - start}")
    print("Logs saved in scraper_log.txt")
