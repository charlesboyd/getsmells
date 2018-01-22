import understand
# https://scitools.com/sup/api-2/
# https://scitools.com/documents/manuals/python/understand.html
# help (understand)

print("hello!")

db = understand.open("C:\\Users\\cb1782\\MyUnderstandProject.udb")

def getATFD(classObj):
    classATFD = 0
    for amethod in aclass.ents("Define", "Method"):
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        for aent in amethod.ents("Call, Use, Set", "Method ~unresolved ~unknown, Variable ~unresolved ~unknown"):
            if aclass.longname() not in aent.longname():
                classATFD += 1
    return classATFD


def getWMC(classObj):
    return classObj.metric(["SumCyclomaticModified"])['SumCyclomaticModified'] or 0


def getTCC(classObj):
    #TODO
    return 0

print(db.metrics())

# God Class
# - ATFD (Access to Foreign Data) > Few
# - WMC (Weighted Method Count) >= Very High --- 'SumCyclomaticModified'
# - TCC (Tight Class Cohesion) < 1/3
#

for aclass in db.ents("Class"):
    classMetricATFD = getATFD(aclass)
    classMetricWMC = getWMC(aclass)
    classMetricTCC = getTCC(aclass)
    classSmellGod = (classMetricATFD > 100) and (classMetricWMC >= 10) and (classMetricTCC < 0.33)

    print("God Class = " + str(classSmellGod) + "\tATFD = " + str(classMetricATFD) + "\tWMC = " + str(classMetricWMC) + "\tTCC = " + str(classMetricTCC) + "\t" + aclass.longname())