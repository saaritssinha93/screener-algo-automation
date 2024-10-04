# -*- coding: utf-8 -*-
"""
webscraping using selenium after clicking buttons

@author: Mayank
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

path = "C:\\Users\\Mayank\\OneDrive\\Udemy\\Quant Investing Using Python\\1.5_Web Scraping\\scripts\\chromedriver.exe"


### clicking dropdown buttons before scraping   
service = webdriver.chrome.service.Service(path)
service.start()

ticker = "AAPL"
url = "https://finance.yahoo.com/quote/{}/financials?p={}".format(ticker,ticker)

driver = webdriver.Chrome(service=service)
driver.get(url)
driver.implicitly_wait(3) 

buttons = driver.find_elements(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]//button')
for button in buttons:
    if button.accessible_name in ["Quarterly","Expand All"]:
        pass
    else:
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(button)).click()
        
income_st_dir = {}
table = driver.find_elements(By.XPATH,  '//div[@class="tableBody yf-1pgoo1f"]')
table_heading = driver.find_elements(By.XPATH,  '//div[@class="tableHeader yf-1pgoo1f"]')
for cell in table_heading:
    headings = cell.text.split(" ")

for cell in table:
    vals = cell.text.split("\n")
    income_st_dir[vals[0]] = vals[1:]
    
income_statement_df = pd.DataFrame(income_st_dir).T
income_statement_df.columns = headings[1:]
        