#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F
from ROOT import TH2F


file1Loc = "../AnalysisRecoCuts_ScaleFactors_WeightedTotal_CategoryHistograms.root"
file2Loc= "../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"
outFileLoc= "../Acceptances.root"

numerators=["ScaleFactorWeight_Count", "ScaleFactorWeight_Category_PtAndLocation"]
channels=["MuonChannel", "ElectronChannel"]
sfs=[["mu_TrigSFUP", "mu_TrigSFDN", "ph_idSFUP", "ph_idSFDN"],
    ["el_TrigSFUP", "el_TrigSFDN", "ph_idSFUP", "ph_idSFDN", "ph_evetoSFUP", "ph_evetoSFDN"]]
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
            print channels[j]+"_"+numerators[i]
            hist1 = file1.Get(channels[j]+"_"+numerators[i])
            hist1.Print()
            hist2 = file2.Get(decays[j] +"_"+denominators[i])
            hist2.Print()
            divideHist = hist1.Clone(channels[j]+"_Acceptances_"+numerators[i])
            divideHist.Divide(hist2)
            divideHist.Write()
            for k in range(len(sfs[j])):
                print channels[j]+"_"+sfs[j][k]+"_"+numerators[i]
                hist1 = file1.Get(channels[j]+"_"+sfs[j][k]+"_"+numerators[i])
                hist1.Print()
                hist2 = file2.Get( decays[j]+"_"+denominators[i])
                hist2.Print()
                divideHist = hist1.Clone(channels[j]+"_Acceptances_"+"_"+sfs[j][k]+"_" +numerators[i])
                divideHist.Divide(hist2)
                divideHist.Write()
    #weightedSumHist.Add(hist1, hist2, weight1, weight2)
    
           
if __name__=="__main__":
    divideHistograms()
