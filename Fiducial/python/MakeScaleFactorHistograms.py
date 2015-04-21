# Python Code for Histograming events based on their
# RECO values.  Splits signal events between the different
# channels and our different categories.
# 
# Example execution from command line:
#python MakeScaleFactorHistograms.py AnalysisRecoCuts_ScaleFactors_Wgg_FSR.root Wgg_FSR_ScaleFactorHistograms.root


import sys

from ROOT import TFile
from ROOT import TTree

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histogramBuilder

inFileDir="../test/RootFiles/"
treeLoc="ggNtuplizer/EventTree"

outFileDir="../test/"


def MakeScaleFactorHistograms(inFileName="ggTree_mc_ISR.root", outFileName="test.root"):

    # In File, Out File, and Tree
    inFile = TFile(inFileDir+inFileName)
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
            # Separate by Lead Photon Pt
            if tree.pt_leadph12 > 15.0 and tree.pt_leadph12 < 25.0:
                channel+="_LeadPhotonPt15_25"
                MakeHistograms(tree, channel, scalefactor)
            if tree.pt_leadph12 > 25.0 and tree.pt_leadph12 < 40.0:
                channel+="_LeadPhotonPt25_40"
                MakeHistograms(tree, channel, scalefactor)
            if tree.pt_leadph12 > 40.0 and tree.pt_leadph12 < 70.0:
                channel+="_LeadPhotonPt40_70"
                MakeHistograms(tree, channel, scalefactor)
            if tree.pt_leadph12 > 70.0:
                channel+="_LeadPhotonPt70"
                MakeHistograms(tree, channel, scalefactor)
            
        if(isMuonChannel):
            channel="MuonChannel"
            scalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
            MakeHistograms(tree, channel, scalefactor)

        #if(not isElectronChannel and not isMuonChannel):
            
    outFile.Write()

def MakeHistograms(tree, channel, scalefactor):
    histogramBuilder.fillScaleFactorHistograms("ScaleFactors_"+channel, scalefactor)


    

if __name__=="__main__":
        MakeScaleFactorHistograms(sys.argv[1], sys.argv[2])
    
