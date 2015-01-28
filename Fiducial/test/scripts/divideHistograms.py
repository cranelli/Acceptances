#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F
from ROOT import TH2F


file1Loc = "../AnalysisRecoCuts_ScaleFactors_WeightedTotal_CategoryHistograms.root"
file2Loc= "../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"
outFileLoc= "../Acceptances.root"

numerators=["Count_ScaleFactorWeight", "Category_PtAndLocation_ScaleFactorWeight"]
channels=["MuonChannel", "ElectronChannel"]
denominators=["Count", "Category_PtAndLocation"]
decays=["MuonDecay", "ElectronDecay"]
#hist1Name="Category_PtAndLocation_MuonChannel"
#hist2Name="Category_PtAndLocation_MuonDecay"
#histOutName="Acceptances"
#doCalcC=True


def divideHistograms():
    file1 = TFile(file1Loc, 'READ')
    
    file2 = TFile(file2Loc, 'READ')
    outFile = TFile(outFileLoc, "RECREATE")
    
    for i in range(len(numerators)):
        for j in range(len(channels)):
            print numerators[i]+"_"+channels[j]
            hist1 = file1.Get(numerators[i]+"_" +channels[j])
            
            hist2 = file2.Get(denominators[i]+"_"+ decays[j])
            divideHist = hist1.Clone(numerators[i]+"_Acceptances_"+channels[j])
            divideHist.Divide(hist2)
            divideHist.Write()
    #weightedSumHist.Add(hist1, hist2, weight1, weight2)
    
           
if __name__=="__main__":
    divideHistograms()
