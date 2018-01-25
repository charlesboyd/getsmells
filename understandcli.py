import subprocess

# Relevant Understand CLI Documentation:
# https://scitools.com/support/commandline/


def analyzeCode(sourcePath, projectPath):

    print(subprocess.check_output(['ipconfig']))


if __name__ == '__main__':
    print("Running code analysis and project output on a directory standalone using defaults")

    # Default project and output path
    analyzeCode("C:\\Users\\cb1782\\MyUnderstandProject.udb", "C:\\Users\\cb1782\\reportoutput.csv")