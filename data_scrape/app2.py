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
options.add_argument("--headless")  # Optional: Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})

data = []
date_str = "2024-04-18"
date_format = "%Y-%m-%d"
current_date = datetime.strptime(date_str, date_format)

# Open the webpage
for _ in range(360):
    new_date_str = current_date.strftime(date_format)
    driver.get(f"https://www.foxsports.com/stories?date={new_date_str}")
    
    # Wait for the cards to load (adjust the timeout if needed)
    try:
        # Wait for cards to be loaded (cards-slide-up class should appear)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "cards-slide-up"))
        )

        elements = driver.find_elements(By.CLASS_NAME, "cards-slide-up")
        elements_title = [element for element in elements if len(element.text) > 20]

        for idx, element in enumerate(elements_title):
            # Wait for image to load
            img_tag = WebDriverWait(element, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "img"))
            )
            img_url = img_tag.get_attribute("src")
            title = element.text
            
            # Open the article in a new tab
            driver.execute_script("window.open(arguments[0], '_blank');", element.find_element(By.TAG_NAME, "a").get_attribute("href"))
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            
            # Wait for article content to load
            try:
                article_content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "article-content"))
                )
            except:
                try:
                    article_content = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'story-content'))
                    )
                except:
                    print("Failed to find article content")
                    continue

            article_text = article_content.text
            
            # Wait for the story header to get the date
            try:
                story_header = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "story-header-container"))
                )
                story_time = story_header.text.split("\n")[2]
            except:
                story_time = "Unknown"

            # Save the article data
            news_obj = {"title": title, "img_url": img_url, "text": article_text, "date": story_time}
            data.append(news_obj)
            print(f"Scraped {idx + 1} news articles")

            # Close the new tab and switch back to the main page
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Write data to file periodically
        with open("news.jsonl", "a") as file:
            for news in data:
                file.write(json.dumps(news) + "\n")
            data = []

    except Exception as err:
        print(f"Error occurred: {err}")
        pass

    # Move to the previous day
    current_date -= timedelta(days=1)

# Write remaining data to file at the end
with open("news.jsonl", "a") as file:
    for news in data:
        file.write(json.dumps(news) + "\n")

# Quit the driver at the end of the script
driver.quit()
