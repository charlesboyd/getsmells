import sys
import platform
import statistics

if platform.system() == "Windows":
    sys.path.append('C:/Program Files/SciTools/bin/pc-win64/Python')
else:
    sys.path.append('/Applications/Understand.app/Contents/MacOS/Python')

# Relevant Understand API Documentation:
# https://scitools.com/sup/api-2/
# https://scitools.com/documents/manuals/python/understand.html
# help(understand)
import understand

def getATFD(classObj):
    classATFD = 0
    for amethod in classObj.ents("Define", "Method"):
        # https://scitools.com/documents/manuals/html/understand_api/kindApp121.html
        # https://scitools.com/documents/manuals/html/understand_api/kindApp158.html
        # NOTE: Includes all foreign methods called, even if not a getter or setter
        for aent in amethod.ents("Call, Use, Set", "Method ~unresolved ~unknown, Variable ~unresolved ~unknown"):
            if classObj.longname() not in aent.longname():
                classATFD += 1
    return classATFD


def getWMC(classObj):
    return classObj.metric(["SumCyclomaticModified"])['SumCyclomaticModified'] or 0


def getTCC(classObj):
    methods = classObj.ents("Define", "Method")
    numberOfPairs = 0
    numberOfShares = 0
    for x in range(0, len(methods)):
        for y in range(x + 1, len(methods)):
            numberOfPairs += 1
            atrrsAccessedInMethodX = methods[x].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodY = methods[y].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodXNames = set()
            atrrsAccessedInMethodYNames = set()
            for attr in atrrsAccessedInMethodX:
                atrrsAccessedInMethodXNames.add(attr.longname())
            for attr in atrrsAccessedInMethodY:
                atrrsAccessedInMethodYNames.add(attr.longname())
            commonAttrs = atrrsAccessedInMethodXNames.intersection(atrrsAccessedInMethodYNames)
            for atrrName in commonAttrs:
                if classObj.longname() in atrrName:
                    numberOfShares += 1
                    break
    if numberOfPairs == 0:
        # NOTE: Default is currently 0.0
        return 0.0
    else:
        return (numberOfShares / numberOfPairs) * 1.0


def extractSmells(projectPath, csvOutputPath, log):
    delm = ","

    FEW = 4
    ONE_THIRD = 1/3

    db = understand.open(projectPath)

    outputFile = open(csvOutputPath, "w")
    outputData = "Class" + delm + "God Class" + "\n"
    outputFile.write(outputData)

    print("\tCalculating complex metrics for "+str(len(db.ents("Class"))) + " classes...")

    classLib = list()
    allWMC = set()
    godClasses = set()

    for aclass in db.ents("Class"):
        classLongName = aclass.longname()

        classMetricATFD = getATFD(aclass)
        classMetricWMC = getWMC(aclass)
        classMetricTCC = getTCC(aclass)

        allWMC.add(classMetricWMC)

        classLib.append({"name": classLongName, "ATFD": classMetricATFD, "WMC": classMetricWMC, "TCC": classMetricTCC})

    print("\tApplying code smell thresholds")

    meanWMC = statistics.mean(allWMC)
    devWMC = statistics.pstdev(allWMC)
    veryHighWMC = meanWMC + (1.5 * devWMC) # 1.5 std. dev. above the mean (upper ~15%)

    log.write("\n\nWMC: mean = " + str(meanWMC) + ", pstdev = " + str(devWMC) + ", VERY_HIGH = " + str(veryHighWMC) + "\n")

    for aclass in classLib:
        # God Class
        # - ATFD (Access to Foreign Data) > Few
        # - WMC (Weighted Method Count) >= Very High
        # - TCC (Tight Class Cohesion) < 1/3
        classSmellGod = (aclass["ATFD"] > FEW) and (aclass["WMC"] >= veryHighWMC) and (aclass["TCC"] < ONE_THIRD)

        if classSmellGod:
            godClasses.add(aclass["name"])

        log.write("God Class = " + str(classSmellGod) + "\tATFD = " + str(aclass["ATFD"]) + "\tWMC = " + 
                  str(aclass["WMC"]) + "\tTCC = " + str(aclass["TCC"]) + "\t" + aclass["name"] + "\n")

        outputFile.write(aclass["name"] + delm + str(classSmellGod) + "\n")

    log.write("\n\nGod Classes (count = " + str(len(godClasses)) + "): " + str(godClasses) + "\n\n")

    outputFile.close()

    log.write("Code smell extraction complete\n")

    print("\tCode smell extraction complete")
    print("\tGod Class = " + str(len(godClasses)))


if __name__ == '__main__':
    print("Running code smell extraction on an Understand project standalone using defaults")

    # Default project and output path
    if platform.system() == "Windows":
        logFile = open("C:/Users/cb1782/understandapi-log.txt", "w+")
        extractSmells("C:/Users/cb1782/MyUnderstandProject.udb",
                      "C:/Users/cb1782/understandapi-csv.csv",
                      logFile)
    else:
        logFile = open("/Users/charles/Documents/DIS/understandapi-log.txt", "w+")
        extractSmells("/Users/charles/Documents/DIS/understandproject.udb",
                    "/Users/charles/Documents/DIS/understandapi-csv.csv",
                    logFile)

