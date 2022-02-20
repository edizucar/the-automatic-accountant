from pickle import NONE
import sys
import json
import os
from xml.etree.ElementPath import get_parent_map
import matplotlib.pyplot as plt
from enum import Enum, IntEnum, auto

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.data_mine import checkAndGetJSON

#Find out percentage change of a specific index, eg. gross profit,
#from data1 to data2
def change(index1, index2):
    if(index1 == 0):
        return 0
    return (index2 - index1) / (index1)

#Just some examples of indices where we can look at the change over time
def checkIfSuspicious(comparison, indices):
    drastic_changes = {}
    none_values = {}
    for index in indices:
        diff = comparison[index]["Relative Change"]
        if diff is None:
            none_values[index] = diff
        elif abs(diff) > 0.2:
            drastic_changes[index] = diff
    return {"Drastic Changes": drastic_changes, "None values": none_values}

#Plot graphs of specific indices over time
def plotOverTime(data, index, name):
    plt.plot(data["name"], index)
    plt.savefig('graphs/' + name + '.png')

def returnCompare(data1, data2, index):
    company1 = data1[index]
    company2 = data2[index]
    if company1 is None or company2 is None:
        absolute_change = None
    else:
        absolute_change = company2 - company1
    if absolute_change is None: 
        relative_change = None
    else:
        relative_change = change(company1, company2)
    return {"Company1": company1, "Company2": company2, "Absolute Change": absolute_change, \
        "Relative Change": relative_change}

def company_details(data):
    d = {}
    for x in ["Company Name", "UK Companies House Registered Number", "Start date covered by report", "End date covered by report"]:
        d[x] = data[x]
    d["SIC"] = data["SIC And Tag Pairs"][0][0]
    d["Industry"] = data["SIC And Tag Pairs"][0][1]
    d["Sector"] = sectors[getSector(d["SIC"])]
    return d



#Compare two sets of data, returns a dictionary which has all the data, absolute changes, relative changes, as well as points that are worth reporting 
#(including over 20% change in certain indices, certain indices being negative when they shouldn't be)
def compare(data1, data2):
    #Temporary replace None values by 0 function, should update analysis function in the future to handle None values instead of this
    profit_and_loss1 = data1["Profit & Loss Account"]
    profit_and_loss2 = data2["Profit & Loss Account"]
    turnover = returnCompare(profit_and_loss1, profit_and_loss2, "Turnover")
    gross_profit = returnCompare(profit_and_loss1, profit_and_loss2, "Gross profit/loss")
    net_profit = returnCompare(profit_and_loss1, profit_and_loss2, "Net profit/loss")
    balance1 = data1["Balance Sheet"]
    balance2 = data2["Balance Sheet"]
    fixed_assets1 = balance1["Fixed assets"]
    fixed_assets2 = balance2["Fixed assets"]
    tangible_fixed_assets = returnCompare(fixed_assets1, fixed_assets2, "Tangible fixed assets")
    investment_fixed_assets = returnCompare(fixed_assets1, fixed_assets2, "Investments fixed assets")
    fixed_asset_balance = returnCompare(fixed_assets1, fixed_assets2, "Fixed assets balance")
    current_assets1 = balance1["Current assets"]
    current_assets2 = balance2["Current assets"]
    debtors = returnCompare(current_assets1, current_assets2, "Debtors (due within one year)")
    cash_balance = returnCompare(current_assets1, current_assets2, "Cash balance")
    current_assets_balance = returnCompare(current_assets1, current_assets2, "Current assets balance")

    current_liabilities1 = balance1["Current liabilities"]
    current_liabilities2 = balance2["Current liabilities"]
    creditors = returnCompare(current_liabilities1, current_liabilities2, "Creditors (due within one year)")

    current_liabilities_balance = returnCompare(current_liabilities1, current_liabilities2, \
        "Current liabilities balance")
    net_al_balance = returnCompare(balance1, balance2, \
        "Net assets/liabilities balance")
    ratio1 = data1["Ratio Analysis Table"]
    ratio2 = data2["Ratio Analysis Table"]
    gross_profit_margin = returnCompare(ratio1, ratio2, "Gross profit margin")
    liquidity_ratio = returnCompare(ratio1, ratio2, "Liquidity ratio")
    debtor_days = returnCompare(ratio1, ratio2, "Debtor days")
    comparison = {"Turnover": turnover, "Gross profit/loss": gross_profit, \
        "Net profit/loss": net_profit, "Tangible fixed assets": tangible_fixed_assets, "Investments fixed assets": investment_fixed_assets, "Fixed assets balance": \
            fixed_asset_balance, "Debtors (due within one year)": debtors, "Cash balance": cash_balance, "Current assets balance": current_assets_balance, \
                "Creditors (due within one year)": creditors, "Current liabilities balance": current_liabilities_balance, "Net assets/liabilities balance": \
                    net_al_balance, "Gross profit margin": gross_profit_margin, "Liquidity ratio": liquidity_ratio, "Debtor days": debtor_days}

    #Checking for indicies that report a 20%+ change 
    suspicious_changes = checkIfSuspicious(comparison, comparison.keys())
    comparison["Suspicious Changes"] = suspicious_changes

    #Checking for indicies that shouldn't be negative, but are
    negative_indices = {}
    for positive_index in ["Turnover", "Tangible fixed assets", "Investments fixed assets", "Fixed assets balance", "Debtors (due within one year)", "Cash balance", "Current assets balance",\
        "Creditors (due within one year)", "Current liabilities balance", "Net assets/liabilities balance"]:
        companies = {}
        if comparison[positive_index]["Company1"] is not None and comparison[positive_index]["Company1"] < 0:
            companies["Company1"] = True
        if comparison[positive_index]["Company2"] is not None and comparison[positive_index]["Company2"]< 0:
            companies["Company2"] = True
        if(len(companies) > 0):
            negative_indices[positive_index] = companies
    comparison["Indices that are negative but should not be"] = negative_indices
    comparison["Company1"] = company_details(data1)
    comparison["Company2"] = company_details(data2)

    return comparison

def main():
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir1 = dir.replace('data_analysis', 'data_mining\input-files')
    os.chdir(dir1)
    data1 = checkAndGetJSON('CE Statutory Accounts FY14-15.html')
    data2 = checkAndGetJSON('CUTS Statutory Accounts FY14-15.html')
    comparison = compare(data1,data2)
    os.chdir(dir)
    with open('comparison.json', 'w') as fp:
        json.dump(comparison, fp)
    print(comparison)
    
    
if __name__ == "__main__":
    main()

class Flag(IntEnum):
    GREEN = auto()
    AMBER = auto()
    RED = auto()

def getSector(SIC):
    if 1110 <= SIC <= 3220:
        return "A"
    elif 5101 <= SIC <= 9900:
        return "B"
    elif 10110 <= SIC <= 33200:
        return "C"
    elif 35110 <= SIC <= 35300:
        return "D"
    elif 36000 <= SIC <= 39000:
        return "E"
    elif 41100 <= SIC <= 43999:
        return "F"
    elif 45111 <= SIC <= 47990:
        return "G"
    elif 49100 <= SIC <= 53202:
        return "H"
    elif 55100 <= SIC <= 56302:
        return "I"
    elif 58110 <= SIC <= 63990:
        return "J"
    elif 64110 <= SIC <= 66300:
        return "K"
    elif 68100 <= SIC <= 68320:
        return "L"
    elif 69101 <= SIC <= 7500:
        return "M"
    elif 77110 <= SIC <= 82990:
        return "N"
    elif 84110 <= SIC <= 84300:
        return "O"
    elif 85100 <= SIC <= 85600:
        return "P"
    elif 86101 <= SIC <= 88990:
        return "Q"
    elif 90010 <= SIC <= 93290:
        return "R"
    elif 94110 <= SIC <= 96090:
        return "S"
    elif 97000 <= SIC <= 98200:
        return "T"
    elif 99000 <= SIC <= 99999:
        return "U"
    raise Exception("Invalid SIC")

sectors = {
    "A" : "Agriculture, Forestry and Fishing",
    "B" : "Mining and Quarrying",
    "C" : "Manufacturing",
    "D" : "Electricity, gas, steam and air conditioning supply",
    "E" : "Water supply, sewerage, waste management and remediation activities",
    "F" : "Construction",
    "G" : "Wholesale and retail trade; repair of motor vehicles and motorcycles",
    "H" : "Transportation and storage",
    "I" : "Accommodation and food service activities",
    "J" : "Information and communication",
    "K" : "Financial and insurance activities",
    "L" : "Real estate activities",
    "M" : "Professional, scientific and technical activities",
    "N" : "Administrative and support service activities",
    "O" : "Public administration and defence; compulsory social security",
    "P" : "Education",
    "Q" : "Human health and social work activities",
    "R" : "Arts, entertainment and recreation",
    "S" : "Other service activities",
    "T" : "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
    "U" : "Activities of extraterritorial organisations and bodies"
} 


#TODO: dind reasonable values for these two dictionaries

average_gross_profit_by_sector = {
    "A" : 1,
    "B" : 1,
    "C" : 1,
    "D" : 1,
    "E" : 1,
    "F" : 1,
    "G" : 1,
    "H" : 1,
    "I" : 1,
    "J" : 1,
    "K" : 1,
    "L" : 1,
    "M" : 1,
    "N" : 1,
    "O" : 1,
    "P" : 1,
    "Q" : 1,
    "R" : 1,
    "S" : 1,
    "T" : 1,
    "U" : 1
}

average_net_profit_by_sector = {
    "A" : 1,
    "B" : 1,
    "C" : 1,
    "D" : 1,
    "E" : 1,
    "F" : 1,
    "G" : 1,
    "H" : 1,
    "I" : 1,
    "J" : 1,
    "K" : 1,
    "L" : 1,
    "M" : 1,
    "N" : 1,
    "O" : 1,
    "P" : 1,
    "Q" : 1,
    "R" : 1,
    "S" : 1,
    "T" : 1,
    "U" : 1
}

def oneYearOneCompany(data):
    directors = len(data["People"]["Directors"])
    #TODO: once data mining team add appointments and resignations
    #change the next line to match the json
    turnover = data["Appointed"] + data["Resigned"]
    turnover_flag = Flag.GREEN
    turnover_message = None
    if ((turnover / directors > 0.25 and directors > 12) or turnover / directors > 0.4 ):
        if data["Appointed"]/data["Resigned"] < 1:
            turnover_flag = Flag.RED
            turnover_message = "Increased turnover including many resignations"
        elif data["Appointed"]/data["Resigned"] < 1.2:
            turnover_flag = Flag.AMBER
            turnover_message = "Increased turnover including some resignations"
    sector = getSector(data["SIC And Tag Pairs"][0][0])
    gross_profit = data["Profit & Loss Account"]["Gross profit/loss"]
    gross_profit_margin = data["Ratio Analysis Table"]["Gross profit margin"]
    gross_profit_flag = Flag.GREEN
    gross_profit_message = None
    if abs(change(average_gross_profit_by_sector[sector], gross_profit_margin)) > 0.8:
        gross_profit_flag = Flag.AMBER
        gross_profit_mesage = "Gross profit margin (" + str(gross_profit_margin) + ") deviates from industry average (" + str(average_gross_profit_by_sector[sector]) + ")."
    if abs(change(average_gross_profit_by_sector[sector], gross_profit_margin)) > 1.5:
        gross_profit_flag = Flag.RED
        gross_profit_mesage = "Gross profit margin (" + str(gross_profit_margin) + ") deviates significantly from industry average (" + str(average_gross_profit_by_sector[sector]) + ")."
    net_profit = data["Profit & Loss Account"]["Net profit/loss"]
    net_profit_margin = net_profit / data["Gross profit margin"]["Turnover"]
    net_profit_flag = Flag.GREEN
    net_profit_message = None
    if abs(change(average_net_profit_by_sector[sector], net_profit_margin)) > 0.8:
        net_profit_flag = Flag.AMBER
        net_profit_mesage = "Net profit margin (" + str(net_profit_margin) + ") deviates from industry average (" + str(average_net_profit_by_sector[sector]) + ")."
    if abs(change(average_net_profit_by_sector[sector], net_profit_margin)) > 1.5:
        net_profit_flag = Flag.RED
        net_profit_mesage = "Net profit margin (" + str(net_profit_margin) + ") deviates significantly from industry average (" + str(average_net_profit_by_sector[sector]) + ")."


    return {}

def multipleYearsOneCompany(data_li):
    return {}

'''def main(path):
    dir1 = os.path.dirname(path)
    files = os.listdir(dir1)
    length = len(files)
    if length == 0:
        raise Exception("No files provided")
    if length == 1:
        return oneYearOneCompany(checkAndGetJSON(path + files[0]))
    if length == 2:
        data1 = checkAndGetJSON(checkAndGetJSON(path + files[0]))
        data2 = checkAndGetJSON(checkAndGetJSON(path + files[1]))
        if data1["Company Name"] != data2["Comany Name"]:
            return compare(data1, data2)
        else:
            data_li = []
            comp_name = None
            for f in files:
                data = checkAndGetJSON(path + f)
                if comp_name is None:
                    comp_name = data["Company Name"]
                elif comp_name != data["Company Name"]:
                    raise Exception("Cannot compare multiple companies for multiple years")
                data_li.append(checkAndGetJSON(path + f))
            return multipleYearsOneCompany(data_li)
'''