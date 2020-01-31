import csv
import time
import numpy as np
import Analysis.LEMASEngine as LEMASEngine

LabsListFile = "LabsMonitored.list"

with open(LabsListFile, "r") as openedfile:
    data = list(zip(*csv.reader(openedfile)))

glist = np.array(data[0])
AllGroups = np.unique(glist)

Groups = {}
for _, val in enumerate(AllGroups):
    Groups[val] = LEMASEngine.CreateGroup(val, LabsListFile)
    Groups[val].StartAllThreads()

End = False
while not End:
    test = input("Enter 'stop' to end LEMASDataAnalysis: ")
    if test.lower() == "stop":
        End = True
