import sys
import json
import os
import matplotlib.pyplot as plt

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.ixbrl_testing import checkAndcreateJSON,checkAndGetJSON

#Find out percentage change of a specific index, eg. gross profit,
#from data1 to data2
def change(data1, data2, index):
    index1 = data1[index]
    index2 = data2[index]
    return (index2 - index1) / (index1)

#Just some examples of indices where we can look at the change over time
def checkIfSuspicious(comparison, indices):
    suspicious = []
    for index in indices:
        diff = comparison[index]["Relative Change"]
        if abs(diff) > 0.2:
            suspicious[index] = diff
    return suspicious

#Plot graphs of specific indices over time
def plotOverTime(data, index, name):
    plt.plot(data["name"], index)
    plt.savefig('graphs/' + name + '.png')

#Compare two sets of data, returns a dictionary which has all the data, absolute changes, relative changes, as well as points that are worth reporting 
#(including over 20% change in certain indices, certain indices being negative when they shouldn't be)
def compare(data1, data2):
    company1 = data1["Company name"] + data1["Start date covered by report"] + " to " + data1["End date covered by report"]
    company2 = data2["Company name"] + data2["Start date covered by report"] + " to " + data2["End date covered by report"]
    directors1 = data1["Directors"]
    directors2 = data2["Directors"]
    director_no1 = directors1["No. of directors"]
    director_no2 = directors2["No. of directors"]
    director_no_change = director_no2 - director_no1
    director_no_change_relative = change(directors1, directors2, "No. of directors")
    director_no = {company1: director_no1, company2: director_no2, "Absolute Change": \
        director_no_change, "Relative Change": director_no_change_relative}
    director_turnover1 = directors1["Director turnover in year"]
    director_turnover2 = directors2["Director turnover in year"]
    director_turnover_change = director_turnover2 - director_turnover1
    director_turnover_change_relative = change(directors1, directors2, "Director turnover in year")
    director_turnover = {company1: director_turnover1, company2: director_turnover2, \
        "Absolute Change": director_turnover_change, "Relative Change": director_turnover_change_relative}
    profit_and_loss1 = data1["Profit & Loss Account"]
    profit_and_loss2 = data2["Profit & Loss Account"]
    turnover1 = profit_and_loss1["Turnover"]
    turnover2 = profit_and_loss2["Turnover"]
    turnover_change = turnover2 - turnover1
    turnover_change_relative = change(profit_and_loss1, profit_and_loss2, "Turnover")
    turnover = {company1: turnover1, company2: turnover2, "Absolute Change": turnover_change,\
        "Relative Change": turnover_change_relative}
    gross_profit1 = profit_and_loss1["Gross profit/loss"]
    gross_profit2 = profit_and_loss2["Gross profit/loss"]
    gross_profit_change = gross_profit2 - gross_profit1
    gross_profit_change_relative = change(profit_and_loss1, profit_and_loss2, "Gross profit/loss")
    gross_profit = {company1: gross_profit1, company2: gross_profit2, "Absolute Change": \
        gross_profit_change, "Relative Change": gross_profit_change_relative}
    net_profit1 = profit_and_loss1["Net profit/loss"]
    net_profit2 = profit_and_loss2["Net profit/loss"]
    net_profit_change = net_profit2 - net_profit1
    net_profit_change_relative = change(profit_and_loss1, profit_and_loss2, "Net profit/loss")
    net_profit = {company1: net_profit1, company2: net_profit2, "Absolute Change": \
        net_profit_change, "Relative Change": net_profit_change_relative}
    balance1 = data1["Balance Sheet"]
    balance2 = data2["Balance Sheet"]
    fixed_assets1 = balance1["Fixed assets"]
    fixed_assets2 = balance2["Fixed assets"]
    tangible_fixed_assets1 = fixed_assets1["Tangible fixed assets"]
    tangible_fixed_assets2 = fixed_assets2["Tangible fixed assets"]
    tangible_fixed_assets_change = tangible_fixed_assets2 - tangible_fixed_assets1
    tangible_fixed_assets_change_relative = change(fixed_assets1, fixed_assets2, "Tangible fixed assets")
    tangible_fixed_assets = {company1: tangible_fixed_assets2, company2: tangible_fixed_assets1, "Absolute Change": \
        tangible_fixed_assets_change, "Relative Change": tangible_fixed_assets_change_relative}
    investment_fixed_assets1 = fixed_assets1["Investments fixed assets"]
    investment_fixed_assets2 = fixed_assets2["Investments fixed assets"]
    investment_fixed_assets_change = investment_fixed_assets2 - investment_fixed_assets1
    investment_fixed_assets_change_relative = change(fixed_assets1, fixed_assets2, "Investments fixed assets")
    investment_fixed_assets = {company1: investment_fixed_assets1, company2: investment_fixed_assets2, "Absolute Change": \
        investment_fixed_assets_change, "Relative Change": investment_fixed_assets_change_relative}
    fixed_asset_balance1 = fixed_assets1["Fixed assets balance"]
    fixed_asset_balance2 = fixed_assets2["Fixed assets balance"]
    fixed_asset_balance_change = fixed_asset_balance2 - fixed_asset_balance1
    fixed_asset_balance_change_relative = change(fixed_assets1, fixed_assets2, "Fixed assets balance")
    fixed_asset_balance = {company1: fixed_asset_balance1, company2: fixed_asset_balance2, "Absolute Change": \
        fixed_asset_balance_change, "Relative Change": fixed_asset_balance_change_relative}
    current_assets1 = balance1["Current assets"]
    current_assets2 = balance2["Current assets"]
    debtors1 = current_assets1["Debtors (due within one year)"]
    debtors2 = current_assets2["Debtors (due within one year)"]
    debtors_change = debtors2 - debtors1
    debtors_change_relative = change(current_assets1, current_assets2, \
        "Debtors (due within one year)")
    debtors = {company1: debtors1, company2: debtors2, "Absolute Change": debtors_change, \
        "Relative Change": debtors_change_relative}
    cash_balance1 = current_assets1["Cash balance"]
    cash_balance2 = current_assets2["Cash balance"]
    cash_balance_change = cash_balance2 - cash_balance1
    cash_balance_change_relative = change(current_assets1, current_assets2, "Cash balance")
    cash_balance = {company1: cash_balance1, company2: cash_balance2, "Absolute Change": \
        cash_balance_change, "Relative Change": cash_balance_change_relative}
    current_assets_balance1 = current_assets1["Current assets balance"]
    current_assets_balance2 = current_assets2["Current assets balance"]
    current_assets_balance_change = current_assets_balance2 - current_assets_balance1
    current_assets_balance_change_relative = change(current_assets1, current_assets2, "Current assets balance")
    current_assets_balance = {company1: current_assets_balance1, company2: current_assets_balance2, "Absolute Change": \
        current_assets_balance_change, "Relative Change": current_assets_balance_change_relative}
    current_liabilities1 = balance1["Current liabilities"]
    current_liabilities2 = balance2["Current liabilities"]
    creditors1 = current_liabilities1["Creditors (due within one year)"]
    creditors2 = current_liabilities2["Creditors (due within one year)"]
    creditors_change = creditors2 - creditors1
    creditors_change_relative = change(current_liabilities2, current_liabilities1, \
        "Creditors (due within one year)")
    creditors = {company1: creditors1, company2: creditors2, "Absolute Change": \
        creditors_change, "Relative Change": creditors_change_relative}
    current_liabilities_balance1 = current_liabilities1["Current liabilities balance"]
    current_liabilities_balance2 = current_liabilities2["Current liabilities balance"]
    current_liabilities_balance_change = current_liabilities_balance2 - current_liabilities_balance1
    current_liabilities_balance_change_relative = change(current_liabilities2, current_liabilities1, \
        "Current liabilities balance")
    current_liabilities_balance = {company1: current_liabilities_balance1, company2: current_liabilities_balance2, \
        "Absolute Change": current_liabilities_balance_change, "Relative Change": current_liabilities_balance_change_relative}
    net_al_balance1 = balance1["Net assets/liabilities balance"]
    net_al_balance2 = balance2["Net assets/liabilities balance"]
    net_al_balance_change = net_al_balance2 - net_al_balance1
    net_al_balance_change_relative = change(balance2, balance1, "Net assets/liabilities balance")
    net_al_balance = {company1: net_al_balance1, company2: net_al_balance2, \
        "Absolute Change": net_al_balance_change, "Relative Change": net_al_balance_change_relative}
    ratio1 = data1["Ratio Analysis Table"]
    ratio2 = data2["Ratio Analysis Table"]
    gross_profit_margin1 = ratio1["Gross profit margin"]
    gross_profit_margin2 = ratio2["Gross profit margin"]
    gross_profit_margin_change = gross_profit_margin2 - gross_profit_margin1
    gross_profit_margin_change_relative = change(ratio1, ratio2, "Gross profit margin")
    gross_profit_margin = {company1: gross_profit_margin1, company2: gross_profit_margin2, "Absolute Change"\
        : gross_profit_margin_change, "Relative Change": gross_profit_margin_change_relative}
    liquidity_ratio1 = ratio1["Liquidity ratio"]
    liquidity_ratio2 = ratio2["Liquidity ratio"]
    liquidity_ratio_change = liquidity_ratio2 - liquidity_ratio1
    liquidity_ratio_change_relative = change(ratio1, ratio2, "Liquidity ratio")
    liquidity_ratio = {company1: liquidity_ratio1, company2: liquidity_ratio2, "Absolute Change": \
        liquidity_ratio_change, "Relative Change": liquidity_ratio_change_relative}
    debtor_days1 = ratio1["Debtor days"]
    debtor_days2 = ratio2["Debtor days"]
    debtor_days_change = debtor_days2 - debtor_days1
    debtor_days_change_relative = change(ratio1, ratio2, "Debtor days")
    debtor_days = {company1: debtor_days1, company2: debtor_days2, "Absolute Change": \
        debtor_days_change, "Relative Change": debtor_days_change_relative}
    comparison = {"No. of directors": director_no, "Director turnover in year": director_turnover, "Turnover": turnover, "Gross profit/loss": gross_profit, \
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
        companies = set()
        if comparison[positive_index][company1] < 0:
            companies.add(company1)
        if comparison[positive_index][company2] < 0:
            companies.add(company2)
        if(len(companies) > 0):
            negative_indices[positive_index] = companies
    comparison["Indices that are negative but should not be"] = negative_indices
    return comparison

def main():
    data1 = checkAndGetJSON('data-files\\CE Statutory-Accounts-FY14-15.html')
    data2 = checkAndGetJSON('data-files\\CUTS Statutory-Accounts-FY14-15.html')
    comparison = compare(data1,data2)
    print(comparison)
    
    
if __name__ == "__main__":
    main()