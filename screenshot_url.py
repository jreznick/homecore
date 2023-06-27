#!/Anaconda3/python
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep


def mugshot(url: str, file_path: str, width=1600, height=1200):
  """
  :param url: the location on the web you would like to screenshot
  :param file_path: the location on disk where you want to store the screenshot
  :param width: the width of the resulting screenshot, in pixels
  :param height: the height of the resulting screenshot, in pixels
  """
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
	driver.save_screenshot(file_path)
	driver.close()

	sleep(1)

	return f"Snapshot made of {url}"

url = 'http://www.jonreznick.com'
file_path = 'test.png'
print(mugshot(url, file_path))
