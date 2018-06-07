import sys
import platform
import statistics
import numpy as np

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

def getLAA(classObj):
    # TODO: Calculate LAA
    return 1

def getFDP(classObj):
    # TODO: Calculate FDP
    return 1

def getLOC(classObj):
    return classObj.metric(["CountLineCode"])['CountLineCode'] or 0
    
def extractSmells(projectPath, csvOutputPath, log):
    delm = ","
    includeMetricsInCsv = True

    FEW = 4
    ONE_THIRD = 1/3

    db = understand.open(projectPath)

    totalClassesCount = len(db.ents("Class"))

    print("\tCalculating complex metrics for "+str(totalClassesCount) + " classes...")

    classLib = list()

    # TODO: Improve such that 1st quartile can be cacluated without storing all
    # observations (http://www.cs.wustl.edu/~jain/papers/ftp/psqr.pdf) for "Lazy Class"
    allLOC = list()
    allWMC = list()

    godClasses = set()
    lazyClasses = set()
    featureEnvyClasses = set()

    for aclass in db.ents("Class"):
        if (len(classLib)+1) % 250 == 0:
            print("\t\t" + str(round((len(classLib)/totalClassesCount)*100)) + "% complete" ) 

        classLongName = aclass.longname()

        classMetricATFD = getATFD(aclass)
        classMetricWMC = getWMC(aclass)
        classMetricTCC = getTCC(aclass)
        classMetricLAA = getLAA(aclass)
        classMetricFDP = getFDP(aclass)
        classMetricLOC = getLOC(aclass)

        allWMC.append(classMetricWMC)
        allLOC.append(classMetricLOC)

        classLib.append({"name": classLongName, "ATFD": classMetricATFD, "WMC": classMetricWMC, "TCC": classMetricTCC,
            "LAA": classMetricLAA, "FDP": classMetricFDP, "LOC": classMetricLOC})

    print("\tCalculating system-wide averages and metrics")

    meanWMC = statistics.mean(allWMC)
    devWMC = statistics.pstdev(allWMC)
    veryHighWMC = meanWMC + (1.5 * devWMC) # 1.5 std. dev. above the mean (upper ~15%)
    firstQuartileLOC = np.percentile(allLOC, 25)

    log.write("WMC: mean = " + str(meanWMC) + ", pstdev = " + str(devWMC) + ", VERY_HIGH = " + str(veryHighWMC) + "\n")
    log.write("LOC: 1st Quartile = " + str(firstQuartileLOC) + "\n")

    print("\tApplying code smell thresholds")

    outputFile = open(csvOutputPath, "w")
    outputData = delm.join(["Class", "God Class", "Lazy Class", "Feature Envy"])
    if includeMetricsInCsv:
            outputData += delm + delm.join(["Metric: ATFD", "Metric: WMC", "Metric: TCC", "Metric: LOC"])
    outputFile.write(outputData + "\n")

    for aclass in classLib:
        # God Class
        # - ATFD (Access to Foreign Data) > Few
        # - WMC (Weighted Method Count) >= Very High
        # - TCC (Tight Class Cohesion) < 1/3
        classSmellGod = (aclass["ATFD"] > FEW) and (aclass["WMC"] >= veryHighWMC) and (aclass["TCC"] < ONE_THIRD)

        # Lazy Class
        # - LOC (Lines of Code) < 1st quartile of system
        classSmellLazy = (aclass["LOC"] < firstQuartileLOC)

        # Feature Envy
        # - ATFD (Access to Foreign Data) > Few
        # - LAA (Locality of Attribute Accesses) < 1/3
        # - FDP (Foreign Data Providers) <= FEW
        classSmellFeatureEnvy = (aclass["ATFD"] > FEW) and (aclass["LAA"] < ONE_THIRD) and (aclass["FDP"] <= FEW )

        if classSmellGod:
            godClasses.add(aclass["name"])
        if classSmellLazy:
            lazyClasses.add(aclass["name"])
        if classSmellFeatureEnvy:
            featureEnvyClasses.add(aclass["name"])

        csvLine = delm.join([aclass["name"], str(classSmellGod), str(classSmellLazy), str(classSmellFeatureEnvy)])
        if includeMetricsInCsv:
            csvLine += delm + delm.join([str(aclass["ATFD"]), str(aclass["WMC"]), str(aclass["TCC"]), str(aclass["LOC"])])
        outputFile.write(csvLine + "\n")

    outputFile.close()

    #log.write("\n\nGod Classes (count = " + str(len(godClasses)) + "): " + str(godClasses) + "\n\n")
    #log.write("\n\nLazy Classes (count = " + str(len(lazyClasses)) + "): " + str(lazyClasses) + "\n\n")
    #log.write("\n\nFeature Envy (count = " + str(len(featureEnvyClasses)) + "): " + str(featureEnvyClasses) + "\n\n")

    summaryData = "\tCode smell extraction complete"
    summaryData += "\n\t\tGod Class = " + str(len(godClasses))
    summaryData += "\n\t\tLazy Class = " + str(len(lazyClasses))
    summaryData += "\n\t\tFeature Envy = " + str(len(featureEnvyClasses))

    log.write("\n" + summaryData)
    print(summaryData + "\n")


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

