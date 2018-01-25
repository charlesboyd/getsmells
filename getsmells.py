import understandapi
import understandcli
import sys
import os


def printCliHelp():
    print("Usage:\npython3 getsmells.py [sourcePath] [outputPath (optional)]\n")
    print("sourcePath: The path to the directory with a single project's code")
    print("outputPath: The directory to output the CSV with code smells, the debug output, and the Understand Projects "
          "(defaults to the current directory)")


def cli(args):
    if len(args) < 2:
        printCliHelp()
        return

    sourcePath = args[1]

    if not os.path.isdir(sourcePath):
        print("Error: The specified source path either does not exist or is not a directory")
        return
    sourcePath = os.path.normcase(os.path.join(sourcePath, ''))  # fix slash direction and trailing slash

    runName = os.path.split(os.path.split(sourcePath)[0])[1]

    outputPath = os.path.dirname(os.path.realpath(__file__))
    if len(args) >= 3:
        outputPath = args[2]
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

    outputPath = os.path.normcase(os.path.join(outputPath, ''))  # fix slash direction and trailing slash

    outputCsvFile = os.path.join(outputPath, runName + "-smells.csv")
    outputLogFile = os.path.join(outputPath, runName + "-log.txt")

    welcomeMsg = "Starting GetSmells on '" + sourcePath + ' (output at ' + outputPath + ")"
    print(welcomeMsg)
    log = open(outputLogFile, "w+")
    log.write(welcomeMsg + "\n")

    projectDirectoryPath = os.path.join(outputPath, "UnderstandProjects")
    if not os.path.exists(projectDirectoryPath):
        os.makedirs(projectDirectoryPath)
    projectPath = os.path.join(projectDirectoryPath, runName + ".udb")

    print("Step 1/2: Creating an Understand Project for '" + runName + "'")
    if understandcli.analyzeCode(sourcePath, projectPath, log) == 1:
        log.close()
        return

    print("Step 2/2: Extracting code smells from metrics on '" + runName + "'")
    if understandapi.extractSmells(projectPath, outputCsvFile, log) == 1:
        log.close()
        return

    print("GetSmells complete!")
    log.write("GetSmells Complete! (End of log)")
    log.close()


if __name__ == '__main__':
    # cli(sys.argv)

    # For testing
    cli(["",
         "C:/Users/cb1782/Downloads/apache-tomcat-7.0.82-src/apache-tomcat-7.0.82-src",
         "C:/Users/cb1782/output1/"])