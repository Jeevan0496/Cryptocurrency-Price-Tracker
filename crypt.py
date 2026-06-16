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

for row in rows[:20]:
    try:
        columns = row.find_elements(By.TAG_NAME, "td")

        
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

driver.quit()

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