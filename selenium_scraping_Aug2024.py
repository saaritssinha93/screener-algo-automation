# -*- coding: utf-8 -*-
"""
webscraping using selenium

@author: Mayank
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

path = "C:\\Users\\Mayank\\OneDrive\\Udemy\\Quant Investing Using Python\\1.5_Web Scraping\\scripts\\chromedriver.exe"

service = webdriver.chrome.service.Service(path)
service.start()

ticker = "AAPL"
url = "https://finance.yahoo.com/quote/{}/financials?p={}".format(ticker,ticker)

driver = webdriver.Chrome(service=service)
driver.get(url)
driver.implicitly_wait(3)

table = driver.find_element(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]')
text_blob = table.text.split("\n")
income_st_dir = {}
last_key = None
for count, row in enumerate(text_blob):
    if count == 0:
        heading = row.split()
        column_count = len(heading[1:])
    else:
        if count%(column_count+1) == 1:
            income_st_dir[row] = []
            last_key = row
        else:
            income_st_dir[last_key].append(row)
        


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
    if button.accessible_name in ["","Follow","Quarterly","Annual","prev","next"]:
        pass
    else:
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable(button)).click()
   
table = driver.find_element(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]')
text_blob = table.text.split("\n")
income_st_dir = {}
last_key = None
for count, row in enumerate(text_blob):
    if count == 0:
        heading = row.split()
        column_count = len(heading[1:])
    else:
        if count%(column_count+1) == 1:
            income_st_dir[row] = []
            last_key = row
        else:
            income_st_dir[last_key].append(row)
    
income_statement_df = pd.DataFrame(income_st_dir).T
income_statement_df.columns = heading[1:]
        





