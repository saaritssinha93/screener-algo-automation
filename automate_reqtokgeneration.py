# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication
"""

from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from pyotp import TOTP


cwd = os.chdir("C:\\Users\\Saarit\\OneDrive\\Desktop\\Trading\\screener-algo-automation")

def autologin():
    token_path = "api_key.txt"
    key_secret = open(token_path,'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])

# Use WebDriver Manager to download and setup chromedriver automatically
    service = Service(ChromeDriverManager().install())
    
    options = webdriver.ChromeOptions()
# Uncomment this if you want to run headless
# options.add_argument('--headless')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    username = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    time.sleep(15)
    request_token=driver.current_url.split('request_token=')[1][:32]
    with open('request_token.txt', 'w') as the_file:
        the_file.write(request_token)
    driver.quit()

autologin()
