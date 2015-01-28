# Python Code for Skimming a root file, and making a new root file,
# where only events from W decays to a tau are included.
# Example execution from command line:
# python TauSkim.py startRange endRange inFile outFile

import sys

from ROOT import TFile
from ROOT import TTree

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histogramBuilder

origFileDir="/data/users/cranelli/WGamGam/ggNtuples/"
origTreeLoc="ggNtuplizer/EventTree"

skimFileDir="/data/users/cranelli/WGamGam/ggNtuples/TauSkim/"
#newFileLoc="ggtree_ISR_Tau.root"

#histDirLoc = 'histOutput/'

def TauSkim(startRange=0, endRange=-1, inFileName="ggTree_mc_ISR.root", outFileName="test.root"):
    # Original File
    origFile = TFile(origFileDir+inFileName)
    origTree = origFile.Get(origTreeLoc)
    # New File
    skimFile = TFile(skimFileDir + outFileName, "RECREATE")
    skimTreeDirectory = skimFile.mkdir("ggNtuplizer")
    skimTreeDirectory.cd()
    skimTree = origTree.CloneTree(0)
    
    nentries = origTree.GetEntries()
    print "Number of Entries", nentries

    if endRange== -1: endRange=nentries
    for i in range(startRange, endRange):
        if(i%1000==0): print i
        origTree.GetEntry(i)
        
        keepEvent = False

        # Particle Identification Step
        
        #Select W's children
        wChildren = []
        
        #PdgIds
        electronPdgId = 11
        muonPdgId = 13
        tauPdgId = 15
        wPdgId = 24

        #Status
        hardScatterStatus=3
        finalStateStatus=1

        # Select Taus
        # Require the Event has a Tau from a W decay,
        # with status 3 (Hard Scatter)

        particleIdentification.assignParticleByParentID(origTree, wChildren, wPdgId)
        for wChild in wChildren:
            if abs(wChild.PID()) == tauPdgId and wChild.Status() == hardScatterStatus:
                keepEvent = True
                histogramBuilder.fillEventCountHistograms("Count_TauDecay")
            if abs(wChild.PID()) == electronPdgId and wChild.Status() == finalStateStatus:
                histogramBuilder.fillEventCountHistograms("Count_ElectronDecay")
            if abs(wChild.PID()) == muonPdgId and wChild.Status() == finalStateStatus:
                histogramBuilder.fillEventCountHistograms("Count_MuonDecay")


        # Without using particleIdentification Module
        #for index in xrange(origTree.nMC):
        #    if abs(origTree.mcPID[index]) == tauPdgId \
        #    and abs(origTree.mcMomPID[index]) ==wPdgId \
        #    and origTree.mcStatus[index] == hardScatterStatus:
        #        tauDecayCount+=1

        
        if(keepEvent): skimTree.Fill()

    #skimTree.Print()
    skimFile.Write()

#def isHardScatter(particles):
#    for particle in particles:
#        if particle.Status() == 3: return True
#    return False

# Passed 3 arguments from the Command Line, Start of Entry Range,
# End of Entry Range, and the InFile and OutFile.
if __name__=="__main__":
        TauSkim(int(sys.argv[1]),int(sys.argv[2]), sys.argv[3], sys.argv[4])
    
