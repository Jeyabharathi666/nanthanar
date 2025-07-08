'''from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

# Start Selenium WebDriver
driver = webdriver.Chrome()
driver.get("https://www.business-standard.com/markets/research-report")

# Wait a few seconds for JS to load data
time.sleep(5)

# Parse HTML
html = BeautifulSoup(driver.page_source, 'html.parser')

# Find the main table
table = html.find("table")
if table:
    # Get all rows
    rows = table.find_all("tr")

    # Loop through each row and print the text from all cells
    for row in rows:
        cells = row.find_all(["td", "th"])  # include headers and data
        data = [cell.get_text(strip=True) for cell in cells]
        print(" | ".join(data))
else:
    print("Table not found.")

driver.quit()
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--headless")  # Required for GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start Selenium WebDriver with options
driver = webdriver.Chrome(options=options)
driver.get("https://www.business-standard.com/markets/research-report")

# Wait a few seconds for JS to load data
time.sleep(5)

# Parse HTML
html = BeautifulSoup(driver.page_source, 'html.parser')

# Find the main table
table = html.find("table")
if table:
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        data = [cell.get_text(strip=True) for cell in cells]
        print(" | ".join(data))
else:
    print("Table not found.")

driver.quit()
