from datetime import datetime, timedelta
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize WebDriver
options = Options()
options.add_argument("--headless")  # Run in headless mode (optional)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})
# driver.set_page_load_timeout(20)
# options.page_load_strategy = "none"
data = []
date_str = "2024-11-29"
date_format = "%Y-%m-%d"
current_date = datetime.strptime(date_str, date_format)
# Reconstruct the date in the original format
new_date_str = current_date.strftime(date_format)

# Open a webpage
for _ in range(360):
    new_date_str = current_date.strftime(date_format)
    driver.get(f"https://www.foxsports.com/stories?date={new_date_str}")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "cards-slide-up")))
    # Navigate to the desired URL using JavaScript

    # Wait for the initial content to load
    try:
        elements = driver.find_elements(By.CLASS_NAME, "cards-slide-up")
        elements_title = [element for element in elements if len(element.text) > 20]
        for idx, element in enumerate(elements_title):
            img_tag = WebDriverWait(element, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            img_tag = element.find_element(By.TAG_NAME, "img")
            img_url = img_tag.get_attribute("src")  # Get the 'src' attribute
            title = element.text
            element.click()
            try:
                # article_content = driver.find_element(By.ID, "article-content")
                article_content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "article-content"))
                )
            except:
                try:
                    # article_content = driver.find_element(By.CLASS_NAME, "story-content")
                    article_content = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "story-content"))
                    )
                except:
                    continue

            article_text = article_content.text
            story_header = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "story-header-container"))
            )
            story_header = driver.find_element(By.CLASS_NAME, "story-header-container")  # text of article date
            story_time = story_header.text.split("\n")[2]
            news_obj = {"title": title, "img_url": img_url, "text": article_text, "date": story_time}
            driver.back()
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "cards-slide-up"))
            )
            data.append(news_obj)
            print(f"Scraped {idx + 1} news articles")
        with open(f"news.jsonl", "a") as file:
            for news in data:
                file.write(json.dumps(news) + "\n")
            data = []
    except Exception as err:
        pass
    current_date -= timedelta(days=1)

with open(f"news.jsonl", "a") as file:
    for news in data:
        file.write(json.dumps(news) + "\n")
# Convert the string to a datetime object
