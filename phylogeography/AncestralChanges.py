"""
Created on Tue 9 April 2019 

@authors: david & eduan

Edited on Sat 25 January 2026
by moise christian junior MEKA
"""
import baltic as bt
import pandas as pd

import argparse

description = (
            "AncestralChanges.py : "
            "This script allows us to draw all sample movements from a migration tree. It is useful for outbreaks introduction analysis between countries."
        )

parser = argparse.ArgumentParser(description=description)
        
parser.add_argument("--treeFile", "-t", required=True, type=argparse.FileType('r'), help="Path to the file containing tree.")
parser.add_argument("--outFile", "-o", required=True, type=argparse.FileType('w'), help="path to the output csv file")
parser.add_argument("--lastDate", "-d", required=True, type=float, help="time of last sampled tip eg : 2025.3369863014 for 2025-05-03")

args = parser.parse_args()

treeFile = args.treeFile
outFile = args.outFile
lastDate = args.lastDate

myTree=bt.loadNewick(treeFile, absoluteTime=False)
myTree.setAbsoluteTime(lastDate) # need to set this to time of last sampled tip

myTree.traverse_tree() ## required to set heights
myTree.treeStats() ## report stats about tree

changes = 0
times = []
origins = []
destinations = []
for k in myTree.Objects: ## iterate over a flat list of branches
    
    "Assign node UNKNOWN country if not give"
    if 'country' in k.traits:
        country = k.traits['country']
    else:
        country = 'UNKNOWN'
        k.traits['country'] = country 
    
    "Find parent country if given"
    if k.parent.traits:
        parent_country = k.parent.traits['country']
    else:
        parent_country = 'UNKNOWN'
        
    if country != parent_country:
        changes += 1
        times = times + [k.absoluteTime]
        origins = origins + [parent_country]
        destinations = destinations + [country]
        
        
print("Total number of state changes: " + str(changes))

df = pd.DataFrame({'EventTime' : times})
df['Origin'] = origins
df['Destination'] = destinations

df.to_csv(outFile)  
    

