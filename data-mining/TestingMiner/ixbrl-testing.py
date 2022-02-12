
from ixbrlparse import IXBRL
import re

root = ""
#f = root + "/Bilitech Ltd.xhtml"
f = root + "CE Statutory-Accounts-FY14-15.html"

with open(f, encoding="utf8") as a:
    x = IXBRL(a)

        #x.contexts
if False:
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

def matchAny(patterns, string):
    for pattern in patterns:
        if re.search(pattern,string):
            return True
    return False


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



