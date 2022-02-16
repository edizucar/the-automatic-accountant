from selenium import webdriver
#from BeautifulSoup import BeautifulSoup
import pandas as pd
from bs4 import BeautifulSoup



def fromWebsite(url):
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    products = []  # List to store name of the product
    prices = []  # List to store price of the product
    ratings = []  # List to store rating of the product
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content)
    print(soup)



if __name__ == '__main__':
    fromWebsite("https://find-and-update.company-information.service.gov.uk/search?q=Microsoft")