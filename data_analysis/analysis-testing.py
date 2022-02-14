import sys
sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.TestingMiner.ixbrl_testing import checkAndcreateJSON

def main():
    checkAndcreateJSON()

if __name__ == "__main__":
    main()