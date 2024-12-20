from datetime import datetime, timedelta
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Initialize WebDriver
options = Options()
options.add_argument("--headless")  # Optional: Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})

data = []

driver.get(f"https://gamerant.com/gaming/")


def remove_ads():
    ad_class = "an-vp-int-video"
    driver.execute_script(
        f"""
        var ads = document.getElementsByClassName("{ad_class}");
        while(ads[0]) {{
            ads[0].parentNode.removeChild(ads[0]);
        }}
    """
    )
    ad_class = "ad-current"
    driver.execute_script(
        f"""
        var ads = document.getElementsByClassName("{ad_class}");
        while(ads[0]) {{
            ads[0].parentNode.removeChild(ads[0]);
        }}
    """
    )


remove_ads()
# Wait for the cards to load (adjust the timeout if needed)
try:
    # Wait for cards to be loaded (cards-slide-up class should appear)

    # within card items

    # Find all article cards within the section
    for i in range(300):
        section = driver.find_element(By.CLASS_NAME, "w-section-latest")

        cards = section.find_elements(By.CLASS_NAME, "display-card")

        for idx, card in enumerate(cards):

            # Extract Title
            title_element = card.find_element(By.CLASS_NAME, "display-card-title").find_element(By.TAG_NAME, "a")
            title = title_element.text
            url = title_element.get_attribute("href")

            # Extract Image URL
            img_element = card.find_element(By.TAG_NAME, "img")
            img_url = img_element.get_attribute("src")

            # Extract Excerpt
            excerpt = card.find_element(By.CLASS_NAME, "display-card-excerpt").text

            # Extract Author
            author_element = card.find_element(By.CLASS_NAME, "article-author")
            author = author_element.text

            # Extract Date
            date_element = card.find_element(By.CLASS_NAME, "display-card-date")
            date = date_element.text
            try:
                card.find_element(By.CLASS_NAME, "articleHasVideo")
                article_content = ""
            except:
                url = card.find_element(By.CLASS_NAME, "dc-img-link").get_attribute("href")
                driver.execute_script("window.open(arguments[0], '_blank');", url)
                driver.switch_to.window(driver.window_handles[-1])
                article_content = (
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "article-body"))).text
                )
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            data.append(
                {
                    "title": title,
                    "url": url,
                    "img_url": img_url,
                    "excerpt": excerpt,
                    "author": author,
                    "body": article_content,
                }
            )
            print(f"Scraped {idx + 1} news articles")

            # Switch to the new tab

        # Write data to file periodically
        with open("games.jsonl", "a") as file:
            for news in data:
                file.write(json.dumps(news) + "\n")
            data = []

        # next_button = driver.find_element(By.CLASS_NAME, "infinite-btn-next")
        # ActionChains(driver).move_to_element(next_button).click().perform()
        driver.get(f"https://gamerant.com/gaming/{i+2}")

        remove_ads()

except Exception as err:
    print(f"Error occurred: {err}")
    pass

# Move to the previous day


# Write remaining data to file at the end
with open("news.jsonl", "a") as file:
    for news in data:
        file.write(json.dumps(news) + "\n")

# Quit the driver at the end of the script
driver.quit()
