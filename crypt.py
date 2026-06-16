import time
import os
import platform
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# Turns short market cap text like "$1.32T" into a full number like "$1,320,000,000,000"
def expand_market_cap(short_value):
    short_value = short_value.replace("$", "").replace(",", "").strip()
    multipliers = {"T": 1_000_000_000_000, "B": 1_000_000_000, "M": 1_000_000, "K": 1_000}
    suffix = short_value[-1]
    if suffix in multipliers:
        number = float(short_value[:-1]) * multipliers[suffix]
    else:
        number = float(short_value)
    return "$" + format(int(number), ",")

url = "https://coinmarketcap.com/"
driver.get(url)
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr")))
    print("Page loaded, table found.")
except Exception:
    print("The price table did not load in time. The site may be slow, blocking automated browsers, or showing a popup.")
time.sleep(2)

rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
print(f"Found {len(rows)} rows on the page.")
coin_list = []
for row in rows[:15]:
    try:
        columns = row.find_elements(By.TAG_NAME, "td")

        name = columns[2].text.split("\n")[0]
        price = columns[3].text
        change_24h = columns[5].text
        market_cap = expand_market_cap(columns[7].text)

        # Skip index/fund entries that sometimes appear mixed in with real coins
        if "Index" in name or "DTF" in name:
            continue

        coin_list.append({
            "Timestamp": time.strftime("%d-%m-%Y %H:%M"),
            "Coin Name": name,
            "Price (USD)": price,
            "24h Change": change_24h,
            "Market Cap": market_cap
        })
    except Exception as e:
        print("Skipped a row because of an error:", e)

driver.quit()
coin_list = coin_list[:10]

if not coin_list:
    print("No data was collected, so no CSV was created. See the messages above for the reason.")
else:
    filename = "crypto_prices.csv"
    df = pd.DataFrame(coin_list)

    if os.path.isfile(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, mode="w", header=True, index=False)

    print(f"Data saved successfully to {filename}")

    system_name = platform.system()
    if system_name == "Windows":
        os.startfile(filename)
    elif system_name == "Darwin":  # macOS
        os.system(f"open {filename}")
    else:  # Linux
        os.system(f"xdg-open {filename}")