from cProfile import label
from pickle import NONE
import sys
import json
import os
from turtle import color
from xml.etree.ElementPath import get_parent_map
import matplotlib.pyplot as plt
from enum import Enum, IntEnum, auto
from datetime import datetime
from pathlib import Path
from numpy import sort

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
def checkIfSuspicious(comparison, indices, factor=365):
    drastic_changes = {}
    none_values = {}
    for index in indices:
        diff = comparison[index]["Relative Change"]
        if diff is None:
            continue
        #this is equal to 0.20 for one year, i.e. a factor of 365 days
        elif abs(diff) > 1.0005**factor-1:
            drastic_changes[index] = diff
    return drastic_changes


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

def companyDetails(data):
    d = {}
    for x in ["Company Name", "UK Companies House Registered Number", "Start date covered by report", "End date covered by report"]:
        d[x] = data[x]
    d["SIC"] = data["SIC And Tag Pairs"][0][0]
    d["Industry"] = data["SIC And Tag Pairs"][0][1]
    d["Sector"] =  None if d["SIC"] is None else sectors[getSector(d["SIC"])]
    return d



#Compare two sets of data, returns a dictionary which has all the data, absolute changes, relative changes, as well as points that are worth reporting 
#(including over 20% change in certain indices, certain indices being negative when they shouldn't be)
def compare(data1, data2, factor=365):
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

    #Checking for indices that report a 20%+ change 
    suspicious_changes = checkIfSuspicious(comparison, comparison.keys(), factor)
    comparison["Suspicious Changes"] = suspicious_changes

    return comparison
    
def getNegativeIndices(data):
    negative_indices = {}
    for positive_index, ind in [(data["Balance Sheet"]["Fixed assets"]["Tangible fixed assets"], "Tangible fixed assets"),
                                (data["Balance Sheet"]["Fixed assets"]["Investments fixed assets"], "Investments fixed assets"),
                                (data["Balance Sheet"]["Fixed assets"]["Fixed assets balance"], "Fixed assets balance"),
                                (data["Balance Sheet"]["Current assets"]["Cash balance"], "Cash balance"),
                                (data["Balance Sheet"]["Current assets"]["Current assets balance"], "Current assets balance"),
                                (data["Balance Sheet"]["Current liabilities"]["Creditors (due within one year)"], "Creditors (due within one year)"),
                                (data["Balance Sheet"]["Current liabilities"]["Current liabilities balance"], "Current liabilities balance"),
                                (data["Balance Sheet"]["Net assets/liabilities balance"], "Net assets/liabilities balance")]:
        if positive_index is not None and positive_index < 0:
            negative_indices[ind] = positive_index
    return negative_indices

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
    elif 69101 <= SIC <= 75000:
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

#TODO: change all instances of exception to be of a more appropriate, specific exception type

#TODO: find reasonable values for these two dictionaries

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

def getInvalidTuple(feature):
    return (None, Flag.RED, feature + " missing or inappropriately tagged.")

def getNegativeTuple(feature, value):
    return (value, Flag.RED, feature + " cannot be negative")

def getDirectors(data):
    if data["People"]["Directors"] is None:
        return getInvalidTuple("Directors list")
    return (len(data["People"]["Directors"]), Flag.GREEN, None)

def getDirectorTurnover(data, directors):
    appointed = data["Number of Assignments"]
    resigned = data["Number of Resignations"]
    if directors is None:
        return getInvalidTuple("Directors list")
    if appointed is None or resigned is None:
        return getInvalidTuple("Director appointments/resignations")
    if appointed < 0 or resigned < 0:
        return getNegativeTuple()
    else:
        turnover = appointed + resigned
        if ((turnover / directors > 0.25 and directors > 12) or turnover / directors > 0.4 ):
            if appointed/resigned < 1:
                return ([turnover, appointed] , Flag.RED, "Increased turnover including many resignations")
            elif appointed/resigned < 1.2:
                return ([turnover, appointed], Flag.AMBER, "Increased turnover including some resignations")
    return ([turnover, appointed], Flag.GREEN, None)

def getGrossProfitMargin(data, sector):
    gross_profit_margin = data["Ratio Analysis Table"]["Gross profit margin"]
    if gross_profit_margin is None:
        return getInvalidTuple("Gross profit or turnover")
    if abs(change(average_gross_profit_by_sector[sector], gross_profit_margin)) > 1.5:
        return (gross_profit_margin, Flag.RED, 
        "Gross profit margin (" + str(gross_profit_margin) + ") deviates significantly from industry average (" + str(average_gross_profit_by_sector[sector]) + ").")
    if abs(change(average_gross_profit_by_sector[sector], gross_profit_margin)) > 0.8:
        return(gross_profit_margin, Flag.AMBER, 
            "Gross profit margin (" + str(gross_profit_margin) + ") deviates from industry average (" + str(average_gross_profit_by_sector[sector]) + ").")
    return (gross_profit_margin, Flag.GREEN, None)

def getNetProfitMargin(data, sector, net_profit):
    turnover = data["Profit & Loss Account"]["Turnover"]
    if net_profit is None or turnover is None:
        return getInvalidTuple("Net profit or turnover")
    if turnover < 0:
        return (turnover, Flag.RED, "Turnover cannot be negative")
    net_profit_margin = net_profit / turnover
    if abs(change(average_net_profit_by_sector[sector], net_profit_margin)) > 1.5:
        return (net_profit_margin, Flag.RED, 
        "Net profit margin (" + str(net_profit_margin) + ") deviates significantly from industry average (" + str(average_net_profit_by_sector[sector]) + ").")
    if abs(change(average_net_profit_by_sector[sector], net_profit_margin)) > 0.8:
        return(net_profit_margin, Flag.AMBER, 
            "Net profit margin (" + str(net_profit_margin) + ") deviates from industry average (" + str(average_net_profit_by_sector[sector]) + ").")
    return (net_profit_margin, Flag.GREEN, None)

def getLiquidityRatio(data):
    liquidity_ratio = data["Ratio Analysis Table"]["Liquidity ratio"]
    if liquidity_ratio is None:
        return getInvalidTuple("Current assets or current liabilities")
    liquidity_ratio = 1 / liquidity_ratio
    if liquidity_ratio < 1:
        return (liquidity_ratio, Flag.RED, "Current liabilities outweigh assets")
    if liquidity_ratio < 1.2:
        return (liquidity_ratio, Flag.AMBER, "Current assets only slightly outweigh liabilities")
    return (liquidity_ratio, Flag.GREEN, None)

def getDebtorDays(data):
    debtorDays = data["Ratio Analysis Table"]["Debtor days"]
    if debtorDays is None:
        return getInvalidTuple("Debtors within a year")
    if debtorDays > 200:
        return (debtorDays, Flag.RED, "Debtor days too high")
    if debtorDays > 100:
        return (debtorDays, Flag.AMBER, "Debtor days high")
    if debtorDays < 0:
        return (debtorDays, Flag.RED, "Debtor days cannot be negative")
    return (debtorDays, Flag.GREEN, None)
    
class Type(IntEnum):
    ONE_YEAR_ONE_COMPANY = auto()
    MULTIPLE_YEARS_ONE_COMPANY = auto()
    ONE_YEAR_TWO_COMPANIES = auto()

#TODO: add turnover by region if mining team manages to extract that
#TODO: add in every field the corresponding note or a summary if the mining team manages to extract that
#TODO: clear up code - comments, argument types etc
#TODO: add auditors report that was added by data mining team

def oneYearOneCompany(data):
    directors, director_flag, director_message = getDirectors(data)
    (turnover, appointed), turnover_flag, turnover_message = getDirectorTurnover(data, directors)

    sector = getSector(data["SIC And Tag Pairs"][0][0])
    gross_profit = data["Profit & Loss Account"]["Gross profit/loss"]
    gross_profit_margin, gross_profit_flag, gross_profit_message = getGrossProfitMargin(data, sector)

    net_profit = data["Profit & Loss Account"]["Net profit/loss"]
    net_profit_margin, net_profit_flag, net_profit_message = getNetProfitMargin(data, sector, net_profit)

    liquidity_ratio, liquidity_ratio_flag, liquidity_ratio_message = getLiquidityRatio(data)

    debtor_days, debtor_flag, debtor_message = getDebtorDays(data)

    return {
        "Type" : Type.ONE_YEAR_ONE_COMPANY,

        "Company Details" : companyDetails(data),

        "Directors" : {
            "Number of directors" : directors,
            "Flag" : director_flag,
            "Message" : director_message
        },

        "Director Turnover" : {
            "Turnover" : turnover,
            "Appointments" : appointed,
            "Flag" : turnover_flag,
            "Message" : turnover_message 
        },

        "Gross Profit" : {
            "Gross Profit" : gross_profit,
            "Gross Profit Margin" : gross_profit_margin,
            "Flag" : gross_profit_flag,
            "Message" : gross_profit_message
        },

        "Net Profit" : {
            "Net Profit" : net_profit,
            "Net Profit Margin" : net_profit_margin,
            "Flag" : net_profit_flag,
            "Message" : net_profit_message
        },

        "Liquidity Ratio" : {
            "Liquidity Ratio" : liquidity_ratio,
            "Flag" : liquidity_ratio_flag,
            "Message" : liquidity_ratio_message
        },

        "Debtor Days" : {
            "Debtor Days": debtor_days,
            "Flag" : debtor_flag,
            "Message" : debtor_message
        },

        "Negative Indices" : getNegativeIndices(data)
    }

def oneYearTwoCompanies(data1, data2):
    analysis = {"Type" : Type.ONE_YEAR_TWO_COMPANIES, "Company 1" : oneYearOneCompany(data1), "Company 2" : oneYearOneCompany(data2), "Comparison" : compare(data1, data2) }
    return analysis

def getDate(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d")

def plot(x, y, index):
    plt.plot(x,y)
    plt.title(index)
    plt.xlabel("Date")
    plt.ylabel(index)
    plt.savefig(index + ".png")

def plotDirectors(x,directors, turnover, appointments, resignations):
    plt.plot(x, directors, label = "Number of Directors", color = "b")
    plt.plot(x, turnover, label = "Director Turnover", color = "c")
    plt.plot(x, appointments, label = "Director appintments", color = "g")
    plt.plot(x, resignations, label = "Director resignations", color = "r")
    plt.title("Directors and Director turnover")
    plt.xlabel("Date")
    plt.ylabel("Number of Directors")
    plt.legend()
    plt.savefig("directors.png")

def plotProfit(x, turnover, gross_profit, net_profit):
    plt.plot(x, turnover, label = "Turnover")
    plt.plot(x, gross_profit, label = "Gross profit")
    plt.plot(x, net_profit, label = "Net profit")
    plt.title("Turnover and profit")
    plt.xlabel("Date")
    plt.ylabel("Amount (£)")
    plt.legend()
    plt.savefig("profit.png")

def plotProfitMargins(x, gross_profit_margin, gross_profit_margin_average, net_profit_margin, net_profit_margin_average):
    plt.plot(x, gross_profit_margin, label = "Gross profit margin")
    plt.plot(x, net_profit_margin, label = "Net profit margin")
    plt.axhline(y=gross_profit_margin_average, linestyle='--', label = "Gross profit margin industry average")
    plt.axhline(y=net_profit_margin_average, linestyle='--', label = "Net profit margin industry average")
    plt.title("Profit margins")
    plt.xlabel("Date")
    plt.ylabel("Profit margins")
    plt.legend()
    plt.savefig("profit_margin.png")

def plotGraphs(analysis):
    axes = [(getDate(a["Company Details"]["End date covered by report"]),
            a["Directors"]["Number of directors"],
            a["Director Turnover"]["Turnover"],
            a["Director Turnover"]["Appointments"],
            a["Director Turnover"]["Turnover"] - a["Director Turnover"]["Appointments"]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Directors"]["Number of directors"] is not None 
            and a["Director Turnover"]["Turnover"] is not None 
            and a["Director Turnover"]["Appointments"] is not None
        ]
    if axes != []:
        (x, directors, turnover, appointments, resignations) = list(zip(*axes))
        plotDirectors(x,directors, turnover, appointments, resignations)

    axes = [(getDate(a["Company Details"]["End date covered by report"]),
            a["Turnover"]["Turnover"],
            a["Gross Profit"]["Gross Profit"],
            a["Net Profit"]["Net Profit"],
            a["Director Turnover"]["Turnover"] - a["Director Turnover"]["Appointments"]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Turnover"]["Turnover"] is not None 
            and a["Gross Profit"]["Gross Profit"] is not None 
            and a["Net Profit"]["Net Profit"] is not None
    ]
    if axes != []:
        (x, turnover, gross_profit, net_profit) = list(zip(*axes))
        plotProfit(x, turnover, gross_profit, net_profit)
    
    axes = [(getDate(a["Company Details"]["End date covered by report"]),
            a["Gross Profit"]["Gross Profit Margin"],
            a["Net Profit"]["Net Profit Margin "]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Gross Profit"]["Gross Profit Margin"] is not None 
            and a["Net Profit"]["Net Profit Margin"] is not None
    ]
    if axes != [] and analysis[0]["Company Details"]["SIC"]:
        (x, gross_profit_margin , net_profit_margin) = list(zip(*axes))
        SIC = analysis[0]["Company Details"]["SIC"]
        gross_profit_margin_average = average_gross_profit_by_sector[getSector(SIC)]
        net_profit_margin_average = average_net_profit_by_sector[getSector(SIC)]
        plotProfitMargins(x, gross_profit_margin, gross_profit_margin_average, net_profit_margin, net_profit_margin_average)
    
    axes = [(getDate(a["Company Details"]["End date covered by report"]),
            a["Liquidity Ratio"]["Liquidity Ratio"]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Liquidity Ratio"]["Liquidity Ratio"] is not None
    ]
    if axes != []:
        x, liq_ratio = list(zip(*axes))
        plot(x, liq_ratio, "Liquidity Ratio")
    
    axes = [(getDate(a["Company Details"]["End date covered by report"]),
            a["Debtor Days"]["Debtor Days"]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Debtor Days"]["Debtor Days"] is not None
    ]
    if axes != []:
        x, liq_ratio = list(zip(*axes))
        plot(x, liq_ratio, "Liquidity Ratio")
    

def multipleYearsOneCompany(data_li):
    data_li = [d for d in data_li if d["Start date covered by report"] is not None and d["End date covered by report"]]
    data_li = sorted(data_li, key= lambda x:getDate(x["Start date covered by report"]))
    analysis = [oneYearOneCompany(d) for d in data_li]
    comparisons = []
    missing_reports = []
    for d in range(len(data_li)-1):
        start = getDate(data_li[d+1]["Start date covered by report"])
        end = getDate(data_li[d]["End date covered by report"])
        if not ((start-end).days == 1):
            missing_reports.append((end + datetime.timedeleta(days = 1)).strftime("%Y-%m-%d") + " to " + 
                (start - datetime.timedeleta(days = 1)).strftime("%Y-%m-%d"))    
        else:
            comparisons.append(compare(data_li[d], data_li[d+1]), (data_li[d+1]["End date covered by report"] - end).days)
    plotGraphs(analysis)
    return {
        "Type" : Type.MULTIPLE_YEARS_ONE_COMPANY, 
        "Yearly Analysis" : analysis, 
        "Comparisons" : comparisons, 
        "Missing Reports" : missing_reports,
    }

'''if __name__ == "__main__":
    main()

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
        json.dump(comparison, fp,indent=4)
    print(comparison)'''

def main(path):
    dir1 = os.path.realpath(path)
    files = os.listdir(dir1)
    print(files)
    length = len(files)
    if length == 0:
        raise Exception("No files provided")
    if length == 1:
        data = checkAndGetJSON(Path(path + "\\" + files[0]))
        print(data)
        return oneYearOneCompany(data)
    if length == 2:
        data1 = checkAndGetJSON(Path(path + "\\" + files[0]))
        data2 = checkAndGetJSON(Path(path + "\\" + files[1]))
        if data1["Company Name"] != data2["Company Name"]:
            return oneYearTwoCompanies(data1, data2)

    data_li = []
    comp_name = None
    for f in files:
        data = checkAndGetJSON(Path(path + "\\" + f))
        if comp_name is None:
            comp_name = data["Company Name"]
        elif comp_name != data["Company Name"]:
            raise Exception("Cannot compare multiple companies for multiple years")
        data_li.append(checkAndGetJSON(Path(path + "\\" + f)))
    return multipleYearsOneCompany(data_li)

print(main("..\\the-automatic-accountant\\data_analysis\\input-files"))