#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F
from ROOT import TH2F

# (Reco Info)
file1Loc = "../LepGammaGammaNoPhIDWithoutTrigger_WeightedTotal_ScaleFactors_RecoCategoryHistograms.root"

# (Gen Info)
file2Loc= "../job_summer12_LNuGG_WeightedTotal_CommonFiducialSkim_GenCategoryHistograms.root"

outFileLoc= "../Acceptances_LepGammaGammaNoPhIDWithoutTrigger"

numerators=["ScaleFactorWeight_Count", "ScaleFactorWeight_Category_PtAndLocation", "ScaleFactorWeight_Category_Pt", "ScaleFactorWeight_Pt"]
channels=["MuonChannel", "ElectronChannel"]
denominators=["Count", "Category_PtAndLocation", "Category_Pt", "Pt"]
decays=["MuonDecay", "ElectronDecay"]

#For Scale Factor Uncertainties

doScaleFactors=False

sfs=[["mu_TrigSFUP", "mu_TrigSFDN", "ph_idSFUP", "ph_idSFDN"],
    ["el_TrigSFUP", "el_TrigSFDN", "ph_idSFUP", "ph_idSFDN", "ph_evetoSFUP", "ph_evetoSFDN"]]

# PDF Reweighting

doReweight=False

pdf_reweight_name="MSTW2008lo68cl_PDFReweight"
if doReweight:
    for index, channel in enumerate(channels):
        channels[index]=channel+"_"+pdf_reweight_name
    for index, decay in enumerate(decays):
        decays[index]=decay+"_"+pdf_reweight_name



def divideHistograms():
    file1 = TFile(file1Loc, 'READ')
    
    file2 = TFile(file2Loc, 'READ')
    outFile = TFile(outFileLoc, "RECREATE")
    
    for i in range(len(numerators)):
        for j in range(len(channels)):
            print channels[j]+"_"+numerators[i]
            hist1Name=channels[j]+"_"+numerators[i]
            print "Numerator Name:" + hist1Name
            hist1 = file1.Get(hist1Name)
            hist1.Print()
            hist2Name = decays[j] +"_"+denominators[i]
            print "Denominator Name:" +hist2Name 
            hist2 = file2.Get(hist2Name)
            hist2.Print()
            divideHist = hist1.Clone(channels[j]+"_"+numerators[i]+"_Acceptances")
            divideHist.Divide(hist2)
            divideHist.Write()

            # Scale Factors
            if doScaleFactors:
                for k in range(len(sfs[j])):
                    print channels[j]+"_"+sfs[j][k]+"_"+numerators[i]
                    hist1 = file1.Get(channels[j]+"_"+sfs[j][k]+"_"+numerators[i])
                    hist1.Print()
                    hist2 = file2.Get( decays[j]+"_"+denominators[i])
                    hist2.Print()
                    divideHist = hist1.Clone(channels[j]+"_" +numerators[i]+"_"+sfs[j][k]+"_Acceptances")
                    divideHist.Divide(hist2)
                    divideHist.Write()
    
           
if __name__=="__main__":
    divideHistograms()
