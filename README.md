# GetSmells

GetSmells extracts code smells from Java source code using the 
[Understand API](https://scitools.com/support/understand-api-overview/).   

## Prerequisites
GetSmells is written to work on either Windows or MacOS (tested on Windows 7 and MacOS 10.12)
* Understand: You must have [Understand](https://scitools.com/features/) installed locally to run the script.
  * It should be installed in the default location for your OS (`C:\Program Files\SciTools\` for Windows or
`/Applications/Understand.app` on MacOS); if it is not in the default location, you can modify the paths at 
the top of both `understandapi.py` and `understandcli.py`.
  * You can request 1-year educational license for Understand [here](https://scitools.com/student/)
* Python 3.4+: The script is written for Python 3.4+ and, on Windows, your 32-bit/64-bit version of Python 3 should match the 
bit-ness of your Understand install (developed using Python 3.6 64-bit)
* Python Libraries
  * [NumPy](https://docs.scipy.org/doc/numpy/index.html): `pip3 install numpy`

## Usage
`python3 getsmells.py [sourcePath] [outputPath (optional)]`   

**Example**   
`python3 getsmells.py c:/Users/you/path/to/code c:/Users/you/output`   

**Parameters**   
`sourcePath`: The path to the directory with a single project's code   
`outputPath`: The directory to output the CSV with code smells, the debug output, and the Understand Projects 
(defaults to the current directory)   


## Smells
Some extracted smells are based off the criteria outlined in [Object-Oriented Metrics in Practice](http://www.springer.com/us/book/9783540244295) by
 [Michele Lanza](http://www.inf.usi.ch/lanza/index.html) and [Radu Marinescu](http://loose.upt.ro/reengineering/research/), while others are described
 in [On the diffuseness and the impact on maintainability of code smells: a large scale empirical investigation](https://link.springer.com/article/10.1007/s10664-017-9535-z).

**God Class**
- ATFD (Access to Foreign Data) > Few
- WMC (Weighted Method Count) >= Very High
- TCC (Tight Class Cohesion) < 1/3

**Lazy Class**
- LOC (Lines of Code) < 1st quartile of system

## Useful Links
**Understand API Documentation**   
* https://scitools.com/sup/api-2/  
* https://scitools.com/documents/manuals/python/understand.html  
* https://scitools.com/documents/manuals/html/understand_api/kindApp121.html  
* https://scitools.com/documents/manuals/html/understand_api/kindApp158.html   

**Understand CLI Documentation**
* https://scitools.com/support/commandline/   
