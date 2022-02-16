import sys
import json
import os

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.ixbrl_testing import checkAndcreateJSON,checkAndGetJSON


#Input should be the name of a file rather than a path, assuming that all the
#data files are extracted from the same folder, can be changed later to match
#the actual name
def readFromDataFolder(file_name):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir1 = dir.replace('data_analysis', 'data_mining')
    os.chdir(dir1)
    data = checkAndGetJSON(file_name)
    os.chdir(dir)
    return data

def main():
    data = readFromDataFolder('CE Statutory-Accounts-FY14-15.html')
    

if __name__ == "__main__":
    main()