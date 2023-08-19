import os
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep

BASE_PATH = Path(os.getcwd())


def screenshot(url: str, file_path: Path, width=1600, height=1200):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument('--start-maximized')
    driver = webdriver.Chrome(
        executable_path="/usr/bin/chromedriver", 
        options=chrome_options
    )
    driver.get(url)
    driver.set_window_size(width, height)
    driver.save_screenshot(str(file_path))
    driver.close()

    print(f"Snapshot made of {url} placed in {file_path}")


file_path = BASE_PATH / 'test.png'
url = 'http://www.jonreznick.com'
screenshot(url, file_path)
