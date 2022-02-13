
import os.path
from unicodedata import name
from ixbrlparse import IXBRL
import re
import sys
import json


def matchAny(patterns, string):
    return len(filter(lambda pattern: re.match(pattern,string),patterns)) != 0

def searchAny(patterns, string):
    return len(filter(lambda pattern: re.search(pattern,string),patterns)) != 0

def createJSON(input_path,destination_path):
    with open(input_path, encoding="utf8") as file:
        ixbrl_file = IXBRL(file)

    data = {"test_key":"test_value"}

    # Get Company Name, Director Info etc


    # Get Balance Sheet Info

    #Get etc etc

    #Write to json file
    with open(destination_path,"w") as destination_file:
        json.dump(data,destination_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected 2 argument : python <ixbrl-file-path> <destination-json-path>")
    else:
        input_path = sys.argv[1]
        destination_path = sys.argv[2]
        if os.path.exists(destination_path):
            print(f"Overwriting {destination_path}")
        if not os.path.exists(input_path):
            print(f"File '{input_path}' not found")
        else:
            createJSON(input_path,destination_path)

            


if False:
#root = ""
#f = root + "/Bilitech Ltd.xhtml"
#f = root + "CE Statutory-Accounts-FY14-15.html"

#x.contexts

    for c in x.numeric:
        print(c.name)
        if c.context.instant != None:
            print("instant: ", c.context.instant)
        if c.context.startdate != None:
            print("startdate: ", c.context.startdate)
        if c.context.enddate != None:
            print("enddate: ", c.context.enddate)
        print(c.value)
        print()




    #getting director names
    important_role_patterns = ["Chairman","ChiefExecutive","Director[0-9]+"]
    important_people = []
    nonnumeric_names=set()
    director_pattern = "Director[0-9]+"
    for a in x.nonnumeric:
        
        if a.name == "NameEntityOfficer":
            val = a.context.segments[0]["value"]
            if matchAny(important_role_patterns,val):
                important_people.append(a)


    for director in list(important_people):
        c = director.context
        val = c.segments[0]["value"]
        print(f"value:{director.value}, segments:{val}")
        print()



