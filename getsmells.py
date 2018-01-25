import understandapi
import understandcli
import sys
import os

def printCliHelp():
    print("Usage:\npython3 getsmells.py [sourcePath] [outputPile (optional)] [projectCachePath (optional)]\n")
    print("sourcePath: The path to the directory with a single project's code")
    print("outputPile: The CSV output file path (defaults to 'smells.csv' in the current directory)")
    print("projectCachePath: The path to store Understand Projects during processing (by default, creates "
          "'/UnderstandProjects' in the current directory)")


def cli(args):
    if len(args) < 2:
        printCliHelp()
        return

    sourcePath = args[1]

    if len(args) >= 3:
        outputPile = args[2]
    else:
        outputPile = "smells.csv"

    if len(args) >= 4:
        projectCachePath = args[3]
    else:
        projectCachePath = "//UnderstandProjects"
        if not os.path.exists(projectCachePath):
            os.makedirs(projectCachePath)

    # understandcli.analyzeCode(sourcePath, projectCachePath)
    # understandapi.extractSmells(projectCachePath, outputPile)


if __name__ == '__main__':
    cli(sys.argv)
