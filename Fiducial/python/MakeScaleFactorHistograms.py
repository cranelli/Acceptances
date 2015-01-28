# Python Code for Skimming a root file, and making a new root file,
# where only events from W decays to a tau are included.
# Example execution from command line:
# python TauSkim.py startRange endRange inFile outFile

import sys

from ROOT import TFile
from ROOT import TTree

#import particleIdentification
#import objectCuts
#import eventCuts
#import parentCuts

import histogramBuilder

origFileDir="/home/cranelli/WGamGam/Acceptances/CMSSW_5_3_12/src/Acceptances/Fiducial/test/"
treeLoc="ggNtuplizer/EventTree"

outFileDir="/home/cranelli/WGamGam/Acceptances/CMSSW_5_3_12/src/Acceptances/Fiducial/test/"
#newFileLoc="ggtree_ISR_Tau.root"

#histDirLoc = 'histOutput/'

def MakeScaleFactorHistograms(inFileName="ggTree_mc_ISR.root", outFileName="test.root"):
    # Original File
    origFile = TFile(origFileDir+inFileName)
    tree = origFile.Get(treeLoc)
    # New File
    outFile = TFile(outFileDir + outFileName, "RECREATE")
    #outTreeDirectory = outFile.mkdir("ggNtuplizer")
    #outTreeDirectory.cd()
    
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)

        #Calculate Weight Using Scale Factors
        scalefactor =1;
        if(tree.el_passtrig_n>0 and tree.el_n==1 and tree.mu_n==0):
            channel="ElectronChannel"
            histogramBuilder.fillScaleFactorHistograms("EleTrigSF_"+channel, tree.el_trigSF)
            histogramBuilder.fillScaleFactorHistograms("PhoIDSF_"+channel, tree.ph_idSF)
            histogramBuilder.fillScaleFactorHistograms("PhoEVetoSF_"+channel, tree.ph_evetoSF)
            histogramBuilder.fillScaleFactorHistograms("PUWeight_"+channel, tree.PUWeight)
            totalscalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.PUWeight
            histogramBuilder.fillScaleFactorHistograms("TotalSF_"+channel, totalscalefactor)
            #MakeHistograms(tree, channel, scalefactor)
        if(tree.mu_passtrig25_n > 0 and tree.mu_n==1 and tree.el_n==0):
            channel="MuonChannel"
            histogramBuilder.fillScaleFactorHistograms("MuTrigSF_"+channel, tree.mu_trigSF)
            histogramBuilder.fillScaleFactorHistograms("MuIsoSF_"+channel, tree.mu_isoSF)
            histogramBuilder.fillScaleFactorHistograms("MuIdSF_"+channel, tree.mu_idSF)
            histogramBuilder.fillScaleFactorHistograms("PhoIDSF_"+channel, tree.ph_idSF)
            histogramBuilder.fillScaleFactorHistograms("PUWeight_"+channel, tree.PUWeight)
            totalscalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
            histogramBuilder.fillScaleFactorHistograms("TotalSF_"+channel, totalscalefactor)
            #MakeHistograms(tree, channel, scalefactor)
        #if(tree.mu_passtrig25_n==1 and tree.el_passtrig_n==1):
        #    channel="ElectronAndMuonChannel"
        #    totalscalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.mu_trigSF*tree.mu_isoSF*tree.PUWeight
        #    histogramBuilder.fillScaleFactorHistograms("TotalSF_"+channel, totalscalefactor)
            #MakeHistograms(tree, channel, scalefactor)
        #print scalefactor
    outFile.Write()

if __name__=="__main__":
        MakeScaleFactorHistograms(sys.argv[1], sys.argv[2])
    
