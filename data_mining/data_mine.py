from ixbrlparse import IXBRL
import re
import sys
import json
import requests
from bs4 import BeautifulSoup
import pathlib
from dateutil.parser import parse as dateParse
from typing import List



def matchAny(patterns: List[str], string:str) -> bool:
    """
    Applies re.match with every pattern on string. If it matches any pattern it should return true.
    """
    return len(filter(lambda pattern: re.match(pattern, string), patterns)) != 0


def searchAny(patterns :List[str], string:str)->bool:
    """
    Applies re.search with every pattern on string. If it matches any pattern it should return true.
    """
    return len(filter(lambda pattern: re.search(pattern, string), patterns)) != 0


def sanitiseName(name:str):
    """
    Changes a string so it only contains alphabetic characters in it.
    """
    return re.sub(r"[^a-zA-Z\- ]", "", name)


def maxDate(instant, start, end):
    """
    Finds the latest date of instant, start and end. Compatible with None values for any of the arguments.
    """
    if (instant != None):
        if (start == None):
            if (end == None):
                return instant
            elif (instant >= end):
                return instant
            else:
                return end
        elif (end == None):
            if (instant >= start):
                return instant
            else:
                return start
    elif start == None:
        return end
    elif end == None:
        return start
    elif end >= start:
        return end
    elif start >= end:
        return start
    else:
        return None


def addNonnumericTags(ixbrl_file:IXBRL, data:json)->json:
    """
    Takes the IXBRL file and data json.
    Appends relevant non-numeric data from the file into the data json object and returns it
    """
    important_role_patterns = ["Chairman", "ChiefExecutive", "Director[0-9]+"]
    important_people = set()

    for tag in ixbrl_file.nonnumeric:
        # Getting important people from document
        if tag.name == "NameEntityOfficer":
            val = tag.context.segments[0]["value"]
            # tag.value is the string of the chairman's name
            san_name = sanitiseName(tag.value)
            # Exhaust the different relevant roles
            if re.search("Chairman", val):
                data["People"]["Chairman"] = san_name
            elif re.search("ChiefExecutive", val):
                data["People"]["ChiefExecutive"] = san_name
            elif re.search("Director[0-9]+", val):
                # Each director is assigned a number from 1-40, so I extract this number
                director_number = int(re.findall('\d+', val)[-1])
                data["People"]["Directors"][director_number] = san_name

        elif tag.name == "EntityCurrentLegalOrRegisteredName":
            data["Company Name"] = tag.value

        elif tag.name == "UKCompaniesHouseRegisteredNumber":
            data["UK Companies House Registered Number"] = tag.value

        elif tag.name == "StartDateForPeriodCoveredByReport":
            date_parsed = dateParse(tag.value)
            date_formatted = date_parsed.strftime("%Y-%m-%d") #put into yyyy-mm-dd format
            data["Start date covered by report"] = date_formatted

        elif tag.name == "EndDateForPeriodCoveredByReport":
            date_parsed = dateParse(tag.value)
            date_formatted = date_parsed.strftime("%Y-%m-%d") #put into yyyy-mm-dd format
            data["End date covered by report"] = date_formatted

    return data


def addSICAndTag(data: json) -> json:
    """
    PREREQUISITE: Needs company_id to be found or it won't be happy

    Uses company_id to web scrape the SIC number from companies house website

    Appends this data to the data json and returns it.

    """

    company_id = data.get("UK Companies House Registered Number", None)
    if company_id is None:
        data["SIC And Tag Pairs"] = None
    else:
        front_page_url = f"https://find-and-update.company-information.service.gov.uk/company/{str(company_id)}"
        front_page = requests.get(front_page_url)
        fp_soup = BeautifulSoup(front_page.content, "html.parser")

        spans = fp_soup.find_all("span")  # get all span elements

        spans = filter(lambda span: re.search(
            "sic[0-9]+", span.get("id", "")), spans)  # filter by id
        spans_tuples = [tuple(span.text.strip().split(" - "))
                              for span in spans]  # split into sid,decription tuples
        # conversion to correct types
        data["SIC And Tag Pairs"] = [[int(sic), desc] for sic, desc in spans_tuples]

    return data



def addDirectorTurnover(data:json)->json:
    """
    PREREQUISITE: Needs company_id to be found or it won't be happy

    Takes data json object and web scrapes from companies house to get accurate resignations
    and assignment data

    Appends this data to the data json and returns it.    
    """

    company_id = data.get("UK Companies House Registered Number",None)
    if company_id is None:
        data["Number of Assignments"] = None
        data["Number of Resignations"] = None
    else:
        page_url = f"https://find-and-update.company-information.service.gov.uk/company/{company_id}/officers?page="
        page_soup = []
        max_iters = 10
        def checkIfEnd(text:str)->bool:
            if text is None:
                return False
            else:
                return "there are no officer details available for this company" in text.lower()
        for i in range(max_iters):
            page = requests.get(page_url+str(i+1))
            soup = BeautifulSoup(page.content,"html.parser")
            finished_search = soup.find_all("h2", string=checkIfEnd)
            if finished_search:
                break
            else:
                page_soup.append(soup)

        start_date = data.get("Start date covered by report")
        end_date = data.get("End date covered by report")

        if start_date is None or end_date is None:
            data["Number of Assignments"] = None
            data["Number of Resignations"] = None
            return data
        
        start_date = dateParse(start_date)
        end_date = dateParse(end_date)
        num_assign = 0
        num_resign = 0
        for page in page_soup:
            #Each 'page' is a BeautifulSoup object.
            temp = page.find_all("div",class_=re.compile("appointment-[0-9]+"))
            divs = sorted([(int(div["class"][0].split("-")[-1]),div) for div in temp])

            #Each element in divs refers to a specific person
            for i,div in divs:
                # Get assignment/resignation date for indiviual and check if within the years we care about.
                assign_date = div.find("dd",class_="data",id=f"officer-appointed-on-{i}")
                if not assign_date is None:
                    assign_date = dateParse(assign_date.text)
                    if start_date < assign_date and assign_date < end_date:
                        num_assign += 1
                
                resign_date = div.find("dd",class_="data",id=f"officer-resigned-on-{i}")
                if not resign_date is None:
                    resign_date = dateParse(resign_date.text)
                    if start_date < resign_date and resign_date < end_date:
                        num_resign += 1

    data["Number of Assignments"] = num_assign
    data["Number of Resignations"] = num_resign
    return data
     

def addNumericTags(ixbrl_file:IXBRL, data:json)->json:
    """
    Takes the IXBRL file and data json.
    Appends relevant numeric data from the file into the data json object and returns it
    """
    # Get Balance Sheet Info
    latest = {"turnover": None, "gpl": None, "npl": None, "fixed": None, "t fixed": None, "i fixed": None,
              "debtors": None, "debtors 1y": None, "c assets": None, "c liabilities": None,
              "creditors": None, "creditors 1y": None, "cash": None, "net al": None}

    # 1. date sweep:
    for tag in ixbrl_file.numeric:
        date = maxDate(tag.context.instant,
                       tag.context.startdate, tag.context.enddate)
        if (date != None):
            if tag.name == "TurnoverGrossOperatingRevenue" or tag.name == "TurnoverRevenue":
                if ((latest["turnover"] == None) or (date > latest["turnover"])):
                    latest["turnover"] = date
            if tag.name == "GrossProfitLoss":
                if ((latest["gpl"] == None) or (date > latest["gpl"])):
                    latest["gpl"] = date
            if tag.name == "ProfitLossForPeriod":
                if ((latest["npl"] == None) or (date > latest["npl"])):
                    latest["npl"] = date
            if tag.name == "FixedAssets":
                if ((latest["fixed"] == None) or (date > latest["fixed"])):
                    latest["fixed"] = date
            if tag.name == "TangibleFixedAssets":
                if ((latest["t fixed"] == None) or (date > latest["t fixed"])):
                    latest["t fixed"] = date
            if tag.name == "InvestmentsFixedAssets":
                if ((latest["i fixed"] == None) or (date > latest["i fixed"])):
                    latest["i fixed"] = date
            if tag.name == "DebtorsDueWithinOneYear":
                if ((latest["debtors 1y"] == None) or (date > latest["debtors 1y"])):
                    latest["debtors 1y"] = date
            if tag.name == "Debtors":
                if ((latest["debtors"] == None) or (date > latest["debtors"])):
                    latest["debtors"] = date
            if tag.name == "CurrentAssets":
                if ((latest["c assets"] == None) or (date > latest["c assets"])):
                    latest["c assets"] = date
            if tag.name == "CurrentLiabilities":
                if ((latest["c liabilities"] == None) or (date > latest["c liabilities"])):
                    latest["c liabilities"] = date
            if tag.name == "CreditorsDueWithinOneYear":
                if ((latest["creditors 1y"] == None) or (date > latest["creditors 1y"])):
                    latest["creditors 1y"] = date
            if tag.name == "Creditors":
                if ((latest["creditors"] == None) or (date > latest["creditors"])):
                    latest["creditors"] = date
            if tag.name == "CashBankOnHand":
                if ((latest["cash"] == None) or (date > latest["cash"])):
                    latest["cash"] = date
            if tag.name == "NetCurrentAssetsLiabilities":
                if ((latest["net al"] == None) or (date > latest["net al"])):
                    latest["net al"] = date

    # 2. contents sweep
    for tag in ixbrl_file.numeric:
        date = maxDate(tag.context.instant,
                       tag.context.startdate, tag.context.enddate)

        if tag.name == "TurnoverGrossOperatingRevenue"or tag.name == "TurnoverRevenue":
            if (date == latest["turnover"]):
                data["Profit & Loss Account"]["Turnover"] = tag.value
        if tag.name == "GrossProfitLoss":
            if (date == latest["gpl"]):
                data["Profit & Loss Account"]["Gross profit/loss"] = tag.value
        if tag.name == "ProfitLossForPeriod":
            if (date == latest["npl"]):
                data["Profit & Loss Account"]["Net profit/loss"] = tag.value

        if tag.name == "FixedAssets":
            if (date == latest["fixed"]):
                data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = tag.value
        if tag.name == "TangibleFixedAssets":
            if (date == latest["t fixed"]):
                data["Balance Sheet"]["Fixed assets"]["Tangible fixed assets"] = tag.value
        if tag.name == "InvestmentsFixedAssets":
            if (date == latest["i fixed"]):
                data["Balance Sheet"]["Fixed assets"]["Investments fixed assets"] = tag.value

        if tag.name == "CurrentAssets":
            if (date == latest["c assets"]):
                data["Balance Sheet"]["Current assets"]["Current assets balance"] = tag.value
        if (latest["debtors 1y"] != None):
            if ((tag.name == "DebtorsDueWithinOneYear") and (date == latest["debtors 1y"])):
                data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"] = tag.value
        elif (tag.name == "Debtors"):
            if (date == latest["debtors"]):
                data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"] = tag.value
        if tag.name == "CashBankOnHand":
            if (date == latest["cash"]):
                data["Balance Sheet"]["Current assets"]["Cash balance"] = tag.value

        if tag.name == "CurrentLiabilities":
            if (date == latest["c liabilities"]):
                data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] = tag.value
        if (latest["creditors 1y"] != None):
            if ((tag.name == "CreditorsDueWithinOneYear") and (date == latest["creditors 1y"])):
                data["Balance Sheet"]["Current liabilities"][
                    "Creditors (due within one year)"] = tag.value
        elif (tag.name == "Creditors"):
            if (date == latest["creditors"]):
                data["Balance Sheet"]["Current liabilities"][
                    "Creditors (due within one year)"] = tag.value

        if tag.name == "NetCurrentAssetsLiabilities":
            if (date == latest["net al"]):
                data["Balance Sheet"]["Net assets/liabilities balance"] = tag.value

    # 3. checks and additions

    tangible_fixed_assets = data["Balance Sheet"]["Fixed assets"]["Tangible fixed assets"]
    investments_fixed_assets = data["Balance Sheet"]["Fixed assets"]["Investments fixed assets"]
    if (data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] == None):
        if (tangible_fixed_assets == None):
            data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = investments_fixed_assets
        elif (investments_fixed_assets == None):
            data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = tangible_fixed_assets
        else:
            # add
            data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = tangible_fixed_assets + \
                investments_fixed_assets

    cash_balance = data["Balance Sheet"]["Current assets"]["Cash balance"]
    debtors_one_year = data["Balance Sheet"][
        "Current assets"]["Debtors (due within one year)"]
    if (data["Balance Sheet"]["Current assets"]["Current assets balance"] == None):
        if (debtors_one_year == None):
            data["Balance Sheet"]["Current assets"]["Current assets balance"] = cash_balance
        elif (cash_balance == None):
            data["Balance Sheet"]["Current assets"]["Current assets balance"] = debtors_one_year
        else:
            # add
            data["Balance Sheet"]["Current assets"]["Current assets balance"] = cash_balance + debtors_one_year

    if (data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] == None):
        data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] = data[
            "Balance Sheet"]["Current liabilities"]["Creditors (due within one year)"]

    fixed_assets_balance = data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"]
    current_assets_balance = data["Balance Sheet"]["Current assets"]["Current assets balance"]
    current_liabilities_balance = data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"]
    if (data["Balance Sheet"]["Net assets/liabilities balance"] == None):
        if (fixed_assets_balance == None):
            if (current_assets_balance == None):
                data["Balance Sheet"]["Net assets/liabilities balance"] = current_liabilities_balance
            elif (current_liabilities_balance == None):
                data["Balance Sheet"]["Net assets/liabilities balance"] = current_assets_balance
            else:
                data["Balance Sheet"]["Net assets/liabilities balance"] = current_assets_balance - \
                    abs(current_liabilities_balance)
        elif (current_assets_balance == None):
            if (current_liabilities_balance == None):
                data["Balance Sheet"]["Net assets/liabilities balance"] = fixed_assets_balance
            else:
                data["Balance Sheet"]["Net assets/liabilities balance"] = fixed_assets_balance - \
                    abs(current_liabilities_balance)
        elif (current_liabilities_balance == None):
            data["Balance Sheet"]["Net assets/liabilities balance"] = current_assets_balance + \
                fixed_assets_balance
        else:
            data["Balance Sheet"]["Net assets/liabilities balance"] = fixed_assets_balance + \
                current_assets_balance - abs(current_liabilities_balance)

    turnover = data["Profit & Loss Account"]["Turnover"]
    if ((turnover != None) and (turnover != 0)):
        if (data["Profit & Loss Account"]["Gross profit/loss"] != None):
            data["Ratio Analysis Table"]["Gross profit margin"] = data["Profit & Loss Account"]["Gross profit/loss"] / turnover
        if (data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"] != None):
            data["Ratio Analysis Table"]["Debtor days"] = (
                365 * data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"]) / turnover

    if ((data["Balance Sheet"]["Current assets"]["Current assets balance"] != None) and (data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] != None) and (data["Balance Sheet"]["Current assets"]["Current assets balance"] != 0)):
        data["Ratio Analysis Table"]["Liquidity ratio"] = abs(
            data["Balance Sheet"]["Current assets"]["Current assets balance"]) / data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"]

    return data

def addAuditorsReport(input_path:pathlib.Path, data:json)->json:
    """
    If heading contains "AUDITORS??? REPORT" or similar, append everything underneath it
    until next heading (span on same level)
    """

    with open(input_path, encoding="utf8") as file:
        soup = BeautifulSoup(file,"html.parser")
    spans = soup.find_all("span")  # get all span elements
    report_spans = list(filter(lambda span: re.search(
        "(INDEPENDENT )?AUDITORS(????) REPORT", span.text, re.IGNORECASE), spans))

    report = []
    
    if report_spans != []:
        for match in report_spans:
            span_class = match['class']

            level_spans = soup.find_all('span', {'class' : span_class})
            next_level = level_spans[level_spans.index(match) + 1]
            rep_spans = spans[spans.index(match):spans.index(next_level)]

            prev_level = None
            rep = []
            join_next = False
            for l in rep_spans:
                if (l.text != "-") and (l.text != ""):
                    if (l['class'] != prev_level) and (len(rep) != 0):
                        rep.append("\n")
                        rep.append(l.text)
                    elif (join_next == True) and (len(rep) != 0):
                        rep[-1] = rep[-1] + " " + l.text
                        join_next = False
                    else:
                        rep.append(l.text)
                    prev_level = l['class']
                elif (l.text == "-"):
                    join_next = True

            rep_string = "\n".join(rep)
            report.append(rep_string)   
            
            data["Auditors\' Report"] = report
            return data


def createJSON(input_path:pathlib.Path, destination_path:pathlib.Path)->None:
    """
    Creates the JSON object of the mined data then puts it into an actual JSON file.
    """
    data = getJSON(input_path)

    # Write to json file
    with open(destination_path, "w") as destination_file:
        json.dump(data, destination_file,indent=4)


def checkPaths(input_path :pathlib.Path, destination_path : pathlib.Path=None) -> bool:
    """
    Checks for conflicts with paths and raises relevant errors/warnings. returns True if no errors. 
    """
    if not destination_path is None:
        if destination_path.exists():
            print(f"Overwriting {destination_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"File '{input_path}' not found")
    return True


def checkAndcreateJSON(input_path:pathlib.Path, destination_path:pathlib.Path)->None:
    """
    Checks for errors in the input path and raises relevant warnings/errors if there are conflicts.
    Then calls createJSON.
    """
    if checkPaths(input_path, destination_path):
        createJSON(input_path, destination_path)


def checkAndGetJSON(input_path:pathlib.Path)->json:
    """
    Checks for errors in the input path and raises relevant warnings/errors if there are conflicts.
    Then calls getJSON.
    """
    if checkPaths(input_path):
        return getJSON(input_path)


def getJSON(input_path :pathlib.Path)->json:
    """
    INPUT: input_path - the path of the input file to be mined
    OUTPUT: json object of all mined data
    """
    ixbrl_file = None
    with open(input_path, encoding="utf8") as file:
        ixbrl_file = IXBRL(file)

    data = {
        "People": {"Chairman": None, "ChiefExecutive": None, "Directors": {}},
        "Company Name": None,
        "UK Companies House Registered Number": None,
        "Start date covered by report": None,
        "End date covered by report": None,
        "Profit & Loss Account": {"Turnover": None, "Gross profit/loss": None, "Net profit/loss": None},
        "Balance Sheet": {
            "Fixed assets": {"Tangible fixed assets": None, "Investments fixed assets": None, "Fixed assets balance": None},
            "Current assets": {"Debtors (due within one year)": None, "Cash balance": None, "Current assets balance": None},
            "Current liabilities": {"Creditors (due within one year)": None, "Current liabilities balance": None},
            "Net assets/liabilities balance": None},
        "Ratio Analysis Table": {"Gross profit margin": None, "Liquidity ratio": None, "Debtor days": None},
        "Auditors' Report":None
    }

    data = addNonnumericTags(ixbrl_file, data)
    data = addSICAndTag(data)
    data = addDirectorTurnover(data)
    data = addNumericTags(ixbrl_file, data)
    data = addAuditorsReport(input_path, data)

    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected 2 argument : python <ixbrl-file-path> <destination-json-path>")
    else:
        input_path = pathlib.Path(sys.argv[1])
        destination_path = pathlib.Path(sys.argv[2])
        checkAndcreateJSON(input_path, destination_path)
