from ixbrlparse import IXBRL
import re
import sys
import json
import requests
from bs4 import BeautifulSoup
import pathlib
from dateutil.parser import parse as dateParse
import datetime

page_url = f"https://find-and-update.company-information.service.gov.uk/company/01069886/officers?page=1"
page = requests.get(page_url)
soup = BeautifulSoup(page.content,"html.parser")

def appointmentCheck(text):
    if not text is None:
        if "appointments-" in text:
            return True
    return False       

div = soup.find("div",class_=appointmentCheck)

print(div)

