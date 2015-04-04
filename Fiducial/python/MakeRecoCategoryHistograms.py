# Python Code for Histograming events based on their
# RECO values.  Splits signal events between the different
# channels and our different categories.
# 
# Example execution from command line:
#python MakeRecoCategoryHistograms.py ../test/AnalysisRecoCuts_ScaleFactors_Wgg_FSR.root AnalysisRecoCuts_ScaleFactors_Wgg_FSR_CategoryHistograms.root


import sys

from ROOT import TFile
from ROOT import TTree

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histogramBuilder

#inFileDir="../test/"
treeLoc="ggNtuplizer/EventTree"

outFileDir="../test/"


def MakeRecoCategoryHistograms(inFileLoc="ggTree_mc_ISR.root", outFileName="test.root"):

    # In File, Out File, and Tree
    inFile = TFile(inFileLoc)
    tree = inFile.Get(treeLoc)
    outFile = TFile(outFileDir + outFileName, "RECREATE")
    
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)

        #Calculate Weight Using Scale Factors
        scalefactor =1;
        isElectronChannel=(tree.el_passtrig_n> 0 and tree.el_n==1 and tree.mu_n==0)
        isMuonChannel=(tree.mu_passtrig25_n>0 and tree.mu_n==1 and tree.el_n==0)
        if(isElectronChannel):
            channel="ElectronChannel"
            scalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.PUWeight
            MakeHistograms(tree, channel, scalefactor)
        if(isMuonChannel):
            channel="MuonChannel"
            scalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
            MakeHistograms(tree, channel, scalefactor)

        #if(not isElectronChannel and not isMuonChannel):
            
    outFile.Write()

def MakeHistograms(tree, channel, scalefactor):
    
    histogramBuilder.fillCountHistograms(channel)
    histogramBuilder.fillCountHistograms(channel+"_ScaleFactorWeight", scalefactor)
    histogramBuilder.fillScaleFactorHistograms("ScaleFactors_"+channel, scalefactor)
    histogramBuilder.fillPtHistograms(channel+"_ScaleFactorWeight", tree.pt_leadph12, scalefactor)
    histogramBuilder.fillPtCategoryHistograms(channel+"_ScaleFactorWeight", tree.pt_leadph12, scalefactor)
    histogramBuilder.fillPhotonLocationCategoryHistograms(channel+"_ScaleFactorWeight", findPhotonLocations(tree),scalefactor)
    histogramBuilder.fillPtAndLocationCategoryHistograms(channel+"_ScaleFactorWeight", findPhotonLocations(tree),
                                                         tree.pt_leadph12, scalefactor)
    histogramBuilder.fillPtAndLocationCategoryHistograms(channel, findPhotonLocations(tree),
                                                         tree.pt_leadph12)


# Generator Particle Identification Step
    
    #Select W's children
#    wChildren = []
    
    #PdgIds
#    electronPdgId = 11
#    muonPdgId = 13
#    tauPdgId = 15
#    wPdgId = 24

    #Status
#    hardScatterStatus=3
#    finalStateStatus=1

    # Select Taus
    # Require the Event has a Tau from a W decay,
    # with status 3 (Hard Scatter)
    
#    particleIdentification.assignParticleByParentID(tree, wChildren, wPdgId)
   
    #for wChild in wChildren:
     #   if abs(wChild.PID()) == tauPdgId and wChild.Status() == hardScatterStatus:
            #histogramBuilder.fillCountHistograms("Count_TauDecay_"+channel)
            #histogramBuilder.fillCountHistograms("Count_ScaleFactorWeight_TauDecay_"+channel, scalefactor)
      #  if abs(wChild.PID()) == electronPdgId and wChild.Status() == finalStateStatus:
            #histogramBuilder.fillCountHistograms("Count_ElectronDecay_"+channel)
            #histogramBuilder.fillCountHistograms("Count_ScaleFactorWeight_ElectronDecay_"+channel, scalefactor)
       # if abs(wChild.PID()) == muonPdgId and wChild.Status() == finalStateStatus:
            #histogramBuilder.fillCountHistograms("Count_MuonDecay_"+channel)
            #histogramBuilder.fillCountHistograms("Count_ScaleFactorWeight_MuonDecay_"+channel, scalefactor)



#Separate Lead and Sub Lead Photons between Barrel and EndCap.
# 0 is EBEB, 1 EBEE, 2 EEEB, 3 is all others
def findPhotonLocations(tree):
    #Both in Barrel
    if(tree.isEB_leadph12 and tree.isEB_sublph12):
        return 0
    #Lead in Barrel Sub in EndCap
    if(tree.isEB_leadph12 and tree.isEE_sublph12):
        return 1
    #Lead in EndCap Sub in Barrel
    if(tree.isEE_leadph12 and tree.isEB_sublph12):
        return 2
    #Both in EndCap
    if(tree.isEE_leadph12 and tree.isEE_sublph12):
        return 3
    

if __name__=="__main__":
        MakeRecoCategoryHistograms(sys.argv[1], sys.argv[2])
    
