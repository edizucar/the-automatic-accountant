
import os.path
from ixbrlparse import IXBRL
import re
import sys
import json


def matchAny(patterns, string):
    return len(filter(lambda pattern: re.match(pattern,string),patterns)) != 0

def searchAny(patterns, string):
    return len(filter(lambda pattern: re.search(pattern,string),patterns)) != 0

def sanitiseName(name):
    return re.sub(r"[^a-zA-Z\- ]","",name)

def maxDate(instant, start, end):
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

def createJSON(input_path,destination_path):
    with open(input_path, encoding="utf8") as file:
        ixbrl_file = IXBRL(file)
        
        
data = {
    "test_key":"test_value",
    "People":{"Chairman":None, "ChiefExecutive":None, "Directors":{}},
    "Company Name":None,
    "UK Companies House Registered Number":None,
    "Start date covered by report":None,
    "End date covered by report":None,
    "Profit & Loss Account": {"Turnover": None, "Gross profit/loss": None, "Net profit/loss": None},
    "Balance Sheet": {
        "Fixed assets": {"Tangible fixed assets": None, "Investments fixed assets": None, "Fixed assets balance": None},
        "Current assets": {"Debtors (due within one year)": None, "Cash balance": None, "Current assets balance": None},
        "Current liabilities": {"Creditors (due within one year)": None, "Current liabilities balance": None},
        "Net assets/liabilities balance": None },
    "Ratio Analysis Table": {"Gross profit margin": None, "Liquidity ratio": None, "Debtor days": None}
}
    

    # Get Company Name, Director Info etc

    
    important_role_patterns = ["Chairman","ChiefExecutive","Director[0-9]+"]
    important_people = set()

    for tag in ixbrl_file.nonnumeric:

        #Getting important people from document 
        if tag.name == "NameEntityOfficer":
            val = tag.context.segments[0]["value"]
            san_name = sanitiseName(tag.value) #tag.value is the string of the chairman's name
            #Exhaust the different relevant roles
            if re.search("Chairman",val):
                data["People"]["Chairman"] = san_name
            elif re.search("ChiefExecutive",val):
                data["People"]["ChiefExecutive"] = san_name
            elif re.search("Director[0-9]+",val):
                director_number = int(re.findall('\d+', val)[-1]) # Each director is assigned a number from 1-40, so I extract this number
                data["People"]["Directors"][director_number] = san_name

        elif tag.name == "EntityCurrentLegalOrRegisteredName":
            data["Company Name"] = tag.value

        elif tag.name == "UKCompaniesHouseRegisteredNumber":
            data["UK Companies House Registered Number"] = tag.value

        elif tag.name == "StartDateForPeriodCoveredByReport":
            if re.match(r"^\d{4}-\d{2}-\d{2}$",tag.value):
                year,month,day = [int(x) for x in tag.value.split("-")] #TODO: We can separate y,m,d or leave as yyyy-mm-dd.
                data["Start date covered by report"] = tag.value

        elif tag.name == "EndDateForPeriodCoveredByReport":
            if re.match(r"^\d{4}-\d{2}-\d{2}$",tag.value):
                year,month,day = [int(x) for x in tag.value.split("-")] #TODO: We can separate y,m,d or leave as yyyy-mm-dd.
                data["End date covered by report"] = tag.value

                
        ############ Get Balance Sheet Info

        latest = {"turnover":None, "gpl":None, "npl":None, "fixed":None, "t fixed": None, "i fixed": None,
                  "debtors":None, "debtors 1y":None, "c assets":None, "c liabilities":None,
                  "creditors":None, "creditors 1y":None, "cash":None, "net al":None}

        #1. date sweep:
        for tag in ixbrl_file.numeric:
            date = maxDate(tag.context.instant, tag.context.startdate, tag.context.enddate)
            if (date != None):
                if tag.name == "TurnoverGrossOperatingRevenue":
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

        #2. contents sweep
        for tag in ixbrl_file.numeric:
            date = maxDate(tag.context.instant, tag.context.startdate, tag.context.enddate)

            if tag.name == "TurnoverGrossOperatingRevenue":
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
                    data["Balance Sheet"]["Current liabilities"]["Creditors (due within one year)"] = tag.value
            elif (tag.name == "Creditors"):
                if (date == latest["creditors"]):
                     data["Balance Sheet"]["Current liabilities"]["Creditors (due within one year)"] = tag.value      

            if tag.name == "NetCurrentAssetsLiabilities":
                if (date == latest["net al"]):
                     data["Balance Sheet"]["Net assets/liabilities balance"] = tag.value

        #3. checks and additions

        tfa = data["Balance Sheet"]["Fixed assets"]["Tangible fixed assets"]
        ifa = data["Balance Sheet"]["Fixed assets"]["Investments fixed assets"]
        if (data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] == None):
            if (tfa == None):
                data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = ifa
            elif (ifa == None):
                data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = tfa
            else:
                #add
                data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"] = tfa + ifa

        csh = data["Balance Sheet"]["Current assets"]["Cash balance"]
        dbt = data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"]
        if (data["Balance Sheet"]["Current assets"]["Current assets balance"] == None):
            if (dbt == None):
                data["Balance Sheet"]["Current assets"]["Current assets balance"] = csh
            elif (csh == None):
                data["Balance Sheet"]["Current assets"]["Current assets balance"] = dbt
            else:
                #add
                data["Balance Sheet"]["Current assets"]["Current assets balance"] = csh + dbt

        if (data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] == None):
            data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] = data["Balance Sheet"]["Current liabilities"]["Creditors (due within one year)"]

        fa = data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"]
        ca = data["Balance Sheet"]["Current assets"]["Current assets balance"]
        cl = data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"]
        if (data["Balance Sheet"]["Net assets/liabilities balance"] == None):
            if (fa == None):
                if (ca == None):
                    data["Balance Sheet"]["Net assets/liabilities balance"] = cl
                elif (cl == None):
                    data["Balance Sheet"]["Net assets/liabilities balance"] = ca
                else:
                    data["Balance Sheet"]["Net assets/liabilities balance"] = ca - abs(cl)
            elif (ca == None):
                if (cl == None):
                    data["Balance Sheet"]["Net assets/liabilities balance"] = fa
                else:
                    data["Balance Sheet"]["Net assets/liabilities balance"] = fa - abs(cl)
            elif (cl == None):
                data["Balance Sheet"]["Net assets/liabilities balance"] = ca + fa
            else:
                data["Balance Sheet"]["Net assets/liabilities balance"] = fa + ca - abs(cl)

        tno = data["Profit & Loss Account"]["Turnover"]
        if ((tno != None) and (tno != 0)):
            if (data["Profit & Loss Account"]["Gross profit/loss"] != None):
                data["Ratio Analysis Table"]["Gross profit margin"] = data["Profit & Loss Account"]["Gross profit/loss"] / tno
            if (data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"] != None):
                data["Ratio Analysis Table"]["Debtor days"] = (365 * data["Balance Sheet"]["Current assets"]["Debtors (due within one year)"]) / tno

        if ((data["Balance Sheet"]["Current assets"]["Current assets balance"] != None) and (data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"] != None) and (data["Balance Sheet"]["Current assets"]["Current assets balance"] != 0)):
            data["Ratio Analysis Table"]["Liquidity ratio"] = abs(data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"]) / data["Balance Sheet"]["Current assets"]["Current assets balance"]




    #Write to json file
    if True:
        with open(destination_path,"w") as destination_file:
            json.dump(data,destination_file)
        
def checkPaths(input_path,destination_path):
    if os.path.exists(destination_path):
            print(f"Overwriting {destination_path}")
    if not os.path.exists(input_path):
        print(f"File '{input_path}' not found")
        return False
    return True

def checkAndcreateJSON(input_path,destination_path):
    if checkPaths(input_path,destination_path):
        createJSON(input_path,destination_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected 2 argument : python <ixbrl-file-path> <destination-json-path>")
    else:
        input_path = sys.argv[1]
        destination_path = sys.argv[2]
        checkAndcreateJSON(input_path,destination_path)


            




