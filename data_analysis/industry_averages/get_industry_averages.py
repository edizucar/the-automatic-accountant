import json

def get_averages() -> dict:
    """
    Returns the averages of gross profits and net profits for each industry, parsed from the files.
    """
    industry_averages = {}
    with open("data_analysis/industry_averages/industry_names.txt") as f:
        industry_names = f.readlines()
    with open("data_analysis/industry_averages/industry_gross_profit.txt") as f:
        industry_gross_profit = f.readlines()
    with open("data_analysis/industry_averages/industry_net_profit.txt") as f:
        industry_net_profit = f.readlines()   
    for x in range(len(industry_names)):
        industry_averages[industry_names[x].rstrip()] = {"Gross Profit Margin": float(industry_gross_profit[x].rstrip()),"Net Profit Margin": float(industry_net_profit[x].rstrip())}
    with open('data_analysis/industry_averages/industry_averages.json', 'w') as fp:
        json.dump(industry_averages, fp)
    return industry_averages

if __name__ == '__main__':
    get_averages()