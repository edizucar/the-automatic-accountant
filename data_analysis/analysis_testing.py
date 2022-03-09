from cProfile import label
from pickle import NONE
import sys
import json
import os
from turtle import color
from xml.etree.ElementPath import get_parent_map
import matplotlib.pyplot as plt
from enum import Enum, IntEnum, auto
from datetime import datetime, timedelta
from pathlib import Path
from numpy import sort
from typing import List, Dict, Tuple
from requests import post

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.data_mine import checkAndGetJSON
from data_analysis.industry_averages.get_industry_averages import get_averages

average_industry_margins = get_averages()

def change(data1: float, data2: float) -> float:
    """
    Find out percentage change of a specific index, eg. gross profit, from data1 to data2.
    """
    if(data1 == 0):
        return 0
    return (data2 - data1) / (data1)

def checkIfSuspicious(comparison: Dict, indices: List[str], factor=365) -> Dict:
    """
    Checks if a given set of indices are suspicious given a comparison dictionary.
    Suspicious here means that the specific index has changed for over 0.2 for every year.
    """
    drastic_changes = {}
    for index in indices:
        diff = comparison[index]["Relative Change"]
        if diff is None:
            continue
        #this is equal to 0.20 for one year, i.e. a factor of 365 days
        elif abs(diff) > 1.0005**factor-1:
            drastic_changes[index] = diff
    return drastic_changes


def returnCompare(data1:Dict, data2:Dict, index:str) -> Dict:
    """
    Returns a dictionary containing the absolute change and relative change for a two sets of data for a specific index.
    """
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


def companyDetails(data:Dict) -> Dict:
    """
    Returns a dictionary comtaining the non-numeric company information such as name, industry etc extracted from the data.
    """
    d = {}
    for x in ["Company Name", "UK Companies House Registered Number", "Start date covered by report", "End date covered by report"]:
        d[x] = data[x]
    d["SIC"] = data["SIC And Tag Pairs"][0][0]
    d["Industry"] = data["SIC And Tag Pairs"][0][1]
    d["Sector"] =  None if d["SIC"] is None else sectors[getSector(d["SIC"])]
    return d




def compare(data1:Dict, data2:Dict, factor=365) -> Dict:
    """
    Compare two sets of data, returns a dictionary which has all the data, absolute changes, relative changes, as well as points that are worth reporting.
    """
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
    
def getNegativeIndices(data) -> Dict:
    """
    Returns the set of indices that are negative, but shouldn't be, for example fixed assets.
    """
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
    """
    Flag to help label how worth looking into some information is, for example red means that there is something very wrong/interesting with this piece of data 
    and needs to be looked into ASAP.
    """
    GREEN = auto()
    AMBER = auto()
    RED = auto()

def getSector(SIC: int) -> str:
    """
    Returns the sector of a company given its SIC number.
    """
    SICs = [(1110,3220,"A"), (5101,9900,"B"), (10110,33200,"C"), (35110, 35300, "D"), (36000, 39000, "E"), (41100,43999,"F"), (45111,47990,"G"), 
            (49100,53202,"H"), (55100,56302,"I"), (58110,63990,"J"), (64110,66300,"K"), (68100,68320,"L"), (69101,75000,"M"), (77110,82990,"N"), 
            (84110,84300,"O"), (85100,85600,"P"), (86101,88990,"Q"), (90010,93290,"R"), (94110,96090,"S"), (97000,98200,"T"), (99000,99999,"U")]
    for s in SICs:
        if s[0] <= SIC <= s[1]:
            return s[2]
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


def getInvalidTuple(feature: str) -> Tuple:
    """
    Returns a tuple containing a description for invalid data.
    """
    return (None, Flag.RED, feature + " missing or inappropriately tagged.")

def getNegativeTuple(feature: str, value: List[float]) -> Tuple:
    """
    Returns a tuple containing a description for data that is negative but cannot be.
    """
    return (value, Flag.RED, feature + " cannot be negative")

def getDirectors(data: Dict) -> Tuple:
    """
    Return a tuple containing a description for the Director list entry in data.
    """
    if data["People"] is None or data["People"]["Directors"] is None:
        return getInvalidTuple("Directors list")
    return (len(data["People"]["Directors"]), Flag.GREEN, None)

def getDirectorTurnover(data:Dict , directors: int) -> Tuple:
    """
    Return a tuple containing a description for the Director turnover entry in data.
    """
    appointed = data["Number of Assignments"]
    resigned = data["Number of Resignations"]
    if directors is None:
        return getInvalidTuple("Directors list")
    if appointed is None or resigned is None:
        return getInvalidTuple("Director appointments/resignations")
    if appointed < 0 or resigned < 0:
        negative = []
        if appointed < 0:
            negative.append(appointed)
        if appointed < 0:
            negative.append(resigned)
        return getNegativeTuple("Director appointments/resignations", negative)
    else:
        turnover = appointed + resigned
        if ((turnover / directors > 0.25 and directors > 12) or turnover / directors > 0.4 ):
            if appointed/resigned < 1:
                return ([turnover, appointed] , Flag.RED, "Increased turnover including many resignations")
            elif appointed/resigned < 1.2:
                return ([turnover, appointed], Flag.AMBER, "Increased turnover including some resignations")
    return ([turnover, appointed], Flag.GREEN, None)

def getGrossProfitMargin(data: Dict, sector_industry: str) -> Tuple:
    """
    Return a tuple containing a description for the Gross Profit Margin entry in data.
    """
    gross_profit_margin = data["Ratio Analysis Table"]["Gross profit margin"]

    if gross_profit_margin is None:
        return getInvalidTuple("Gross profit or turnover")
    if abs(change(average_industry_margins[sector_industry]["Gross Profit Margin"], gross_profit_margin)) > 0.5:
        return (gross_profit_margin, Flag.RED, 
        "Gross profit margin (" + str(gross_profit_margin) + ") deviates significantly from industry average (" + str(average_industry_margins[sector_industry]["Gross Profit Margin"]) + ").")
    if abs(change(average_industry_margins[sector_industry]["Gross Profit Margin"], gross_profit_margin)) > 0.2:
        return(gross_profit_margin, Flag.AMBER, 
            "Gross profit margin (" + str(gross_profit_margin) + ") deviates from industry average (" + str(average_industry_margins[sector_industry]["Gross Profit Margin"]) + ").")
    return (gross_profit_margin, Flag.GREEN, None)

def getNetProfitMargin(data: Dict, sector_industry: str, net_profit: float) -> Tuple:
    """
    Return a tuple containing a description for the Net Profit Margin entry in data.
    """
    turnover = data["Profit & Loss Account"]["Turnover"]
    if net_profit is None or turnover is None:
        return getInvalidTuple("Net profit or turnover")
    if turnover < 0:
        return (turnover, Flag.RED, "Turnover cannot be negative")
    net_profit_margin = net_profit / turnover
    if abs(change(average_industry_margins[sector_industry]["Net Profit Margin"], net_profit_margin)) > 0.5:
        return (net_profit_margin, Flag.RED, 
        "Net profit margin (" + str(net_profit_margin) + ") deviates significantly from industry average (" + str(average_industry_margins[sector_industry]["Net Profit Margin"]) + ").")
    if abs(change(average_industry_margins[sector_industry]["Net Profit Margin"], net_profit_margin)) > 0.2:
        return(net_profit_margin, Flag.AMBER, 
            "Net profit margin (" + str(net_profit_margin) + ") deviates from industry average (" + str(average_industry_margins[sector_industry]["Net Profit Margin"]) + ").")
    return (net_profit_margin, Flag.GREEN, None)

def getLiquidityRatio(data: Dict) -> Tuple:
    """
    Return a tuple containing a description for the Liquidity ratio entry in data.
    """
    liquidity_ratio = data["Ratio Analysis Table"]["Liquidity ratio"]
    if liquidity_ratio is None:
        return getInvalidTuple("Current assets or current liabilities")
    liquidity_ratio = 1 / liquidity_ratio
    if liquidity_ratio < 1:
        return (liquidity_ratio, Flag.RED, "Current liabilities outweigh assets")
    if liquidity_ratio < 1.2:
        return (liquidity_ratio, Flag.AMBER, "Current assets only slightly outweigh liabilities")
    return (liquidity_ratio, Flag.GREEN, None)

def getDebtorDays(data: Dict) -> Tuple:
    """
    Return a tuple containing a description for the Debtor Days entry in data.
    """
    debtor_days = data["Ratio Analysis Table"]["Debtor days"]
    if debtor_days is None:
        return getInvalidTuple("Debtors within a year")
    if debtor_days > 200:
        return (debtor_days, Flag.RED, "Debtor days too high")
    if debtor_days > 100:
        return (debtor_days, Flag.AMBER, "Debtor days high")
    if debtor_days < 0:
        return (debtor_days, Flag.RED, "Debtor days cannot be negative")
    return (debtor_days, Flag.GREEN, None)

def getAuditorsReport(data: Dict) -> Tuple:
    """
    Return a tuple containing a description for the Auditors' Report entry in data.
    """
    if data["Auditors\' Report"] is None:
        return getInvalidTuple("Auditors' Report")
    auditors_report = post(
        "https://api.deepai.org/api/summarization",
        data={
            'text': data["Auditors\' Report"],
        },
        headers={'api-key': '1d79475c-a116-4e1a-ac1b-892e3d2c7aeb'}
    ).json()['output']
    return (auditors_report, Flag.GREEN, None)
class Type(IntEnum):
    """
    An Enum class to help distinguish between different types of data we are dealing with. It could either be just looking at the data of one company at one year,
    or comparing the data of one company across different years, or comparing the data of two companies at the same year.
    """
    ONE_YEAR_ONE_COMPANY = 1
    MULTIPLE_YEARS_ONE_COMPANY = 2
    ONE_YEAR_TWO_COMPANIES = 3

def getSectorIndustry(sic: int) -> str:
    """
    Given an SIC compute a string of the form "[SECTOR LETTER][FIRST TWO DIGITS OF SIC].[LAST THREE DIGITS OF SIC]"
    e.g. for 1110 this returns "A01.110
    """
    return getSector(sic) + str(sic//10000) + str((sic%10000)//1000) + "." + str(sic%1000)

def oneYearOneCompany(data: Dict) -> Dict:
    """
    Return a dict containing the information and analysis for one company at a specific year.
    """
    directors, director_flag, director_message = getDirectors(data)
    (turnover, appointed), turnover_flag, turnover_message = getDirectorTurnover(data, directors)

    sic = data["SIC And Tag Pairs"][0][0]
    sector_industry = getSectorIndustry(sic)
    
    gross_profit = data["Profit & Loss Account"]["Gross profit/loss"]
    gross_profit_margin, gross_profit_flag, gross_profit_message = getGrossProfitMargin(data, sector_industry)

    net_profit = data["Profit & Loss Account"]["Net profit/loss"]
    net_profit_margin, net_profit_flag, net_profit_message = getNetProfitMargin(data, sector_industry, net_profit)

    liquidity_ratio, liquidity_ratio_flag, liquidity_ratio_message = getLiquidityRatio(data)

    debtor_days, debtor_flag, debtor_message = getDebtorDays(data)

    auditors_report = getAuditorsReport(data)

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

        "Auditors\' Report" : auditors_report,

        "Negative Indices" : getNegativeIndices(data)
    }

def oneYearTwoCompanies(data1: Dict, data2: Dict) -> Dict:
    """
    Return a dict containing the information, analysis and comparison for two companies at a specific year.
    """
    analysis = {"Type" : Type.ONE_YEAR_TWO_COMPANIES, "Company 1" : oneYearOneCompany(data1), "Company 2" : oneYearOneCompany(data2), "Comparison" : compare(data1, data2) }
    return analysis

def getDate(date_string: str) -> datetime:
    """
    Return a datetime object from a date string.
    """
    return datetime.strptime(date_string, "%Y-%m-%d")

def plot(x: List[datetime], y: List[float], index: str) -> None:
    """
    Plots a list of values against their corresponding datetime objects, and saves the graph as an image.
    """
    plt.figure()
    plt.plot(x,y)
    plt.title(index)
    plt.xlabel("Date")
    plt.ylabel(index)
    plt.savefig(index + ".png")

def plotDirectors(x: List[datetime], directors: List[int], turnover: List[int], appointments: List[int], resignations: List[int]) -> None:
    """
    Plots a list of directors, turnovers, appointments and resignations against their corresponding datetime objects, and saves the graph as an image.
    """
    plt.figure()
    plt.plot(x, directors, label = "Number of Directors", color = "b")
    plt.plot(x, turnover, label = "Director Turnover", color = "c")
    plt.plot(x, appointments, label = "Director appintments", color = "g")
    plt.plot(x, resignations, label = "Director resignations", color = "r")
    plt.title("Directors and Director turnover")
    plt.xlabel("Date")
    plt.ylabel("Number of Directors")
    plt.legend()
    plt.savefig("directors.png")

def plotProfit(x: List[datetime], turnover: List[float], gross_profit: List[float], net_profit: List[float]) -> None:
    """
    Plots a list of turnovers, gross profits, net profits against their corresponding datetime objects, and saves the graph as an image.
    """
    plt.figure()
    plt.plot(x, turnover, label = "Turnover")
    plt.plot(x, gross_profit, label = "Gross profit")
    plt.plot(x, net_profit, label = "Net profit")
    plt.title("Turnover and profit")
    plt.xlabel("Date")
    plt.ylabel("Amount (£)")
    plt.legend()
    plt.savefig("profit.png")

def plotProfitMargins(x: List[datetime], gross_profit_margin: List[float], gross_profit_margin_average: List[float], net_profit_margin: List[float], \
    net_profit_margin_average: List[float]) -> None:
    """
    Plots a list of gross profit margins, gross profit averages, net profit margins, net profit averages, against their corresponding datetime objects, 
    and saves the graph as an image.
    """
    plt.figure()
    plt.plot(x, gross_profit_margin, label = "Gross profit margin")
    plt.plot(x, net_profit_margin, label = "Net profit margin")
    plt.axhline(y=gross_profit_margin_average, linestyle='--', label = "Gross profit margin industry average")
    plt.axhline(y=net_profit_margin_average, linestyle='--', label = "Net profit margin industry average")
    plt.title("Profit margins")
    plt.xlabel("Date")
    plt.ylabel("Profit margins")
    plt.legend()
    plt.savefig("profit_margin.png")

def plotGraphs(analysis: List[Dict]) -> None:
    """
    Plot the corresponding graphs for a list of analysis of companies.
    """
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
            a["Gross Profit"]["Gross Profit"] / a["Gross Profit"]["Gross Profit Margin"],
            a["Gross Profit"]["Gross Profit"],
            a["Net Profit"]["Net Profit"],
            a["Director Turnover"]["Turnover"] - a["Director Turnover"]["Appointments"]) 
            for a in analysis
            if a["Company Details"]["End date covered by report"] is not None
            and a["Gross Profit"]["Gross Profit"] is not None 
            and a["Gross Profit"]["Gross Profit Margin"] is not None
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
        gross_profit_margin_average = average_industry_margins[getSectorIndustry(SIC)]["Gross Profit Margin"]
        net_profit_margin_average = average_industry_margins[getSectorIndustry(SIC)]["Net Profit Margin"]
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
    

def multipleYearsOneCompany(data_li: List[Dict]) -> Dict:
    """
    Plots the corresponding graphs for the analysis of the same company across multiple years, and also returns said analysis.
    """
    data_li = [d for d in data_li if d["Start date covered by report"] is not None and d["End date covered by report"]]
    data_li = sorted(data_li, key= lambda x:getDate(x["Start date covered by report"]))
    analysis = [oneYearOneCompany(d) for d in data_li]
    comparisons = []
    missing_reports = []
    for d in range(len(data_li)-1):
        start = getDate(data_li[d+1]["Start date covered by report"])
        end = getDate(data_li[d]["End date covered by report"])
        if not ((start-end).days == 1):
            missing_reports.append((end + timedelta(days = 1)).strftime("%Y-%m-%d") + " to " +
                (start - timedelta(days = 1)).strftime("%Y-%m-%d"))
        else:
            comparisons.append(compare(data_li[d], data_li[d+1], (getDate(data_li[d+1]["End date covered by report"]) - end).days))
    plotGraphs(analysis)
    return {
        "Type" : Type.MULTIPLE_YEARS_ONE_COMPANY, 
        "Yearly Analysis" : analysis, 
        "Comparisons" : comparisons, 
        "Missing Reports" : missing_reports,
    }



def main(paths: List[str]) -> None:
    """
    When provided with a list of paths, carry out the corresponding appropriate analysis for the input, for example if there is only one input then carry out analysis
    for one company at one year.
    """
    length = len(paths)
    if length == 0:
        raise Exception("No files provided")
    if length == 1:
        data = checkAndGetJSON(Path(paths[0]))
        return oneYearOneCompany(data)
    if length == 2:
        data1 = checkAndGetJSON(Path(paths[0]))
        data2 = checkAndGetJSON(Path(paths[1]))
        if data1["Company Name"] != data2["Company Name"]:
            return oneYearTwoCompanies(data1, data2)

    data_li = []
    comp_name = None
    for path in paths:
        data = checkAndGetJSON(Path(path))
        if comp_name is None:
            comp_name = data["Company Name"]
        elif comp_name != data["Company Name"]:
            raise Exception("Cannot compare multiple companies for multiple years")
        data_li.append(data)
    return multipleYearsOneCompany(data_li)

'''paths = [
    r"..\the-automatic-accountant\data_analysis\input_files\CE Statutory Accounts FY17-18.html",
    r"..\the-automatic-accountant\data_analysis\input_files\CE Statutory Accounts FY18-19.html",
    r"..\the-automatic-accountant\data_analysis\input_files\CE Statutory Accounts FY19-20.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\CUTS Statutory Accounts FY17-18.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\CUTS Statutory Accounts FY18-19.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\CUTS Statutory Accounts FY19-20.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\Aspuna Group Limited.xhtml",
    #r"..\the-automatic-accountant\data_analysis\input_files\AudioTelligence Limited.xhtml",
    #r"..\the-automatic-accountant\data_analysis\input_files\Bilitech Ltd.xhtml",
    #r"..\the-automatic-accountant\data_analysis\input_files\CE Statutory Accounts FY14-15.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\CUTS Statutory Accounts FY14-15.html",
    #r"..\the-automatic-accountant\data_analysis\input_files\Tarsis Technology Limited.xhtml",
    ]


print(main(paths))'''