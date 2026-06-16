# Cryptocurrency Price Tracker
# A simple beginner-friendly script that scrapes the top 20 coin prices
# from CoinMarketCap using Selenium, saves them to a CSV file,
# and automatically opens that CSV file.

# Make sure these libraries are installed first:
# pip install selenium pandas
# (Selenium 4.6+ already manages the Chrome driver for you,
#  so webdriver_manager is no longer needed.)

import time
import os
import platform
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- Step 1: Setup the Chrome browser ----------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless=new")  # uncomment this to hide the browser window

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)  # will wait up to 20 seconds for things to load

# ---------- Step 2: Open the CoinMarketCap website ----------
url = "https://coinmarketcap.com/"
driver.get(url)

# ---------- Step 3: Wait for the price table to actually appear ----------
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr")))
    print("Page loaded, table found.")
except Exception:
    print("The price table did not load in time. The site may be slow, blocking automated browsers, or showing a popup.")

time.sleep(2)  # tiny extra pause so all row data finishes rendering

# ---------- Step 4: Find the table rows with coin data ----------
rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
print(f"Found {len(rows)} rows on the page.")

coin_list = []  # this will store all the coin details we collect

# ---------- Step 5: Go through the first 20 rows and grab the data ----------
for row in rows[:20]:
    try:
        columns = row.find_elements(By.TAG_NAME, "td")

        # NOTE: CoinMarketCap sometimes changes its layout.
        # If this stops working, right-click a price on the site,
        # choose "Inspect", and update the column numbers below.
        name = columns[2].text.split("\n")[0]
        price = columns[3].text
        change_24h = columns[5].text
        market_cap = columns[7].text

        coin_list.append({
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Coin Name": name,
            "Price": price,
            "24h Change": change_24h,
            "Market Cap": market_cap
        })
    except Exception as e:
        print("Skipped a row because of an error:", e)

# ---------- Step 6: Close the browser ----------
driver.quit()

# ---------- Step 7: Save the data into a CSV file ----------
if not coin_list:
    print("No data was collected, so no CSV was created. See the messages above for the reason.")
else:
    filename = "crypto_prices.csv"
    df = pd.DataFrame(coin_list)

    # If the file already exists, add new data below the old data (for history tracking)
    if os.path.isfile(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, mode="w", header=True, index=False)

    print(f"Data saved successfully to {filename}")

    # ---------- Step 8: Automatically open the CSV file ----------
    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(filename)
    elif system_name == "Darwin":  # macOS
        os.system(f"open {filename}")
    else:  # Linux
        os.system(f"xdg-open {filename}")