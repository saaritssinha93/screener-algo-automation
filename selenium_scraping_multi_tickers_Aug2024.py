# -*- coding: utf-8 -*-
"""
webscraping using selenium - multiple tickers

@author: Mayank
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd

path = "C:\\Users\\Mayank\\OneDrive\\Udemy\\Quant Investing Using Python\\1.5_Web Scraping\\scripts\\chromedriver.exe"
tickers = ["AAPL","META","CSCO"]
income_statatement_dict = {}
balance_sheet_dict = {}
cashflow_st_dict = {}

### clicking dropdown buttons before scraping   
service = webdriver.chrome.service.Service(path)
service.start()
options = Options()
#options.add_argument("--headless") #use this to not render the actual browser


for ticker in tickers:
    #scrape income statement
    url = "https://finance.yahoo.com/quote/{}/financials?p={}".format(ticker,ticker)
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(url)
    driver.implicitly_wait(0.2)

    buttons = driver.find_elements(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]//button')
    for button in buttons:
        if button.accessible_name in ["Quarterly","Expand All"]:
            pass
        else:
            WebDriverWait(driver, 0.2).until(EC.element_to_be_clickable(button)).click()
            
        
    income_st = {}
    table = driver.find_elements(By.XPATH,  '//div[@class="tableBody yf-1pgoo1f"]')
    table_heading = driver.find_elements(By.XPATH,  '//div[@class="tableHeader yf-1pgoo1f"]')
    for cell in table_heading:
        headings = cell.text.split(" ")
    
    for cell in table:            
        vals = cell.text.split("\n")
        for count, element in enumerate(vals):
            if count%len(headings) == 0:
                key = element
                income_st[key] = []
            else:
                income_st[key].append(element)
        
    income_statement_df = pd.DataFrame(income_st).T
    income_statement_df.columns = headings[1:]
    income_statatement_dict[ticker] = income_statement_df
    
    #scrape balance sheet statement
    url = "https://finance.yahoo.com/quote/{}/balance-sheet?p={}".format(ticker,ticker)
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(url)
    driver.implicitly_wait(0.2)

    buttons = driver.find_elements(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]//button')
    for button in buttons:
        if button.accessible_name in ["Quarterly","Expand All"]:
            pass
        else:
            WebDriverWait(driver, 0.2).until(EC.element_to_be_clickable(button)).click()
        
    balance_sheet = {}
    table = driver.find_elements(By.XPATH,  '//div[@class="tableBody yf-1pgoo1f"]')
    table_heading = driver.find_elements(By.XPATH,  '//div[@class="tableHeader yf-1pgoo1f"]')    
    for cell in table_heading:
        headings = cell.text.split(" ")
    
    #the balance sheet table is rendered differently than income statement in that the entire data is wrapped into one array
    for cell in table:            
        vals = cell.text.split("\n")
        for count, element in enumerate(vals):
            if count%len(headings) == 0:
                key = element
                balance_sheet[key] = []
            else:
                balance_sheet[key].append(element)
        
    balance_sheet_df = pd.DataFrame(balance_sheet).T
    balance_sheet_df.columns = headings[1:]
    balance_sheet_dict[ticker] = balance_sheet_df
    
    #scrape cashflow statement
    url = "https://finance.yahoo.com/quote/{}/cash-flow?p={}".format(ticker,ticker)
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(url)
    driver.implicitly_wait(0.2)

    buttons = driver.find_elements(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]//button')
    for button in buttons:
        if button.accessible_name in ["Quarterly","Expand All"]:
            pass
        else:
            WebDriverWait(driver, 0.2).until(EC.element_to_be_clickable(button)).click()
        
    cashflow_statement = {}
    table = driver.find_elements(By.XPATH,  '//div[@class="tableBody yf-1pgoo1f"]')
    table_heading = driver.find_elements(By.XPATH,  '//div[@class="tableHeader yf-1pgoo1f"]')
    for cell in table_heading:
        headings = cell.text.split(" ")
    
    for cell in table:            
        vals = cell.text.split("\n")
        for count, element in enumerate(vals):
            if count%len(headings) == 0:
                key = element
                cashflow_statement[key] = []
            else:
                cashflow_statement[key].append(element)
        
    cashflow_statement_df = pd.DataFrame(cashflow_statement).T
    cashflow_statement_df.columns = headings[1:]
    cashflow_st_dict[ticker] = cashflow_statement_df
    
    
#converting dataframe values to numeric
for ticker in tickers:
    for col in income_statatement_dict[ticker].columns:
        income_statatement_dict[ticker][col] = income_statatement_dict[ticker][col].str.replace(',|- ','')
        income_statatement_dict[ticker][col] = pd.to_numeric(income_statatement_dict[ticker][col], errors = 'coerce')
        cashflow_st_dict[ticker][col] = cashflow_st_dict[ticker][col].str.replace(',|- ','')
        cashflow_st_dict[ticker][col] = pd.to_numeric(cashflow_st_dict[ticker][col], errors = 'coerce') 
        if col!="TTM": #yahoo has ttm column for income statement and cashflow statement only
            balance_sheet_dict[ticker][col] = balance_sheet_dict[ticker][col].str.replace(',|- ','')
            balance_sheet_dict[ticker][col] = pd.to_numeric(balance_sheet_dict[ticker][col], errors = 'coerce')
        