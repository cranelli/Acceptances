#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

CHANNELS=["MuonChannel", "ElectronChannel"]
HIST_TYPES=["Category_Pt", "Count"]
ACCEPTANCE_TYPES=["TauSig", "TauBkgd"]
PU_WEIGHTS=["5"]
DIRS = ["UP", "DN"]


def MakePileUpSystematicHistograms(hist_dir):

    file_loc =hist_dir+"Acceptances.root"
    file = TFile(file_loc, 'READ')

    outfile_loc=hist_dir+"PileUpSystematics.root"
    outfile=TFile(outfile_loc, 'RECREATE')
    
    for channel in CHANNELS:
        for acceptance_type in ACCEPTANCE_TYPES:
            for hist_type in HIST_TYPES:
                MakeIndividualPileUpSystematicHistograms(file, outfile, channel, acceptance_type, hist_type)
                #MakeTotalSFSystematicHistograms(channel, acceptance_type, dir, hist_type)


# Goes over each channel's up down variations in the pile up weights,and makes the pileup Syst Histogram.
# NB the raised PU does not necessarily correspond with an increase in acceptance,
# so the master equation is used to calculate the upper and lower bounds.
def MakeIndividualPileUpSystematicHistograms(file, outfile, channel, acceptance_type, hist_type):
    expectedHistName=channel+"_Acceptance_"+acceptance_type+"_"+hist_type
    expectedHist = file.Get(expectedHistName)

    for pileup_num in PU_WEIGHTS:
        # Histogram of Acceptances with raised PU vertices
        pileupAcceptanceHistUPName = channel+"_"+"PUWeight_"+pileup_num+"UP"+"_Acceptance_"+acceptance_type+"_"+hist_type
        pileupAcceptanceHistUP = file.Get(pileupAcceptanceHistUPName)
        
        # Histogram of Acceptances with lowered PU vertices
        pileupAcceptanceHistDNName = channel+"_"+"PUWeight_"+pileup_num+"DN"+"_Acceptance_"+acceptance_type+"_"+hist_type
        pileupAcceptanceHistDN = file.Get(pileupAcceptanceHistDNName)
        
        # UP PU Systematics
        pileupSystematicUPHistName=channel+"_"+acceptance_type+"_PUWeight_"+pileup_num+"_pileupSystematicUP"+"_"+hist_type
        pileupSystematicUPHist = expectedHist.Clone(pileupSystematicUPHistName)
        pileupSystematicUPHist.Reset("ICE")
              
        # DN PU Systematics
        pileupSystematicDNHistName=channel+"_"+acceptance_type+"_PUWeight_"+pileup_num+"_pileupSystematicDN"+"_"+hist_type
        pileupSystematicDNHist = expectedHist.Clone(pileupSystematicDNHistName)
        pileupSystematicDNHist.Reset("ICE")
                                                  
        # Loop over All bins in the Histogram, including the overflow bin.
        # Use Master equation because change in pileup is anticorrelated with change
        #in acceptance.
        for bin_index in range(1, expectedHist.GetNbinsX()+2):
            central_value =expectedHist.GetBinContent(bin_index)
            up_value = pileupAcceptanceHistUP.GetBinContent(bin_index)
            dn_value = pileupAcceptanceHistDN.GetBinContent(bin_index)
            
            pileupSystUP = abs(masterDifferenceUP(central_value, up_value, dn_value))
            pileupSystDN = abs(masterDifferenceDN(central_value, up_value, dn_value))
    
            pileupSystematicUPHist.SetBinContent(bin_index, pileupSystUP)
            pileupSystematicDNHist.SetBinContent(bin_index, pileupSystDN)
                
        pileupSystematicUPHist.Print("all")
        pileupSystematicUPHist.Write()
                        
        pileupSystematicDNHist.Print("all")
        pileupSystematicDNHist.Write()


# up value comes from the "up eigenvector" and down from the "down eigenvector"
# But the master equation selects the one that actually causes the greatest difference
# up, unless both cause a downwards shift in which case 0 is taken.
def masterDifferenceUP(central, up, down):
    return max(up-central, down-central, 0)

# Same as masterDifferenceUp, but now selecting the largest downwards shift.
def masterDifferenceDN(central, up, down):
    return min(up - central, down - central, 0)

# Take the difference between the bins' of two histograms, and returns the absolute of the difference.
def CalcAbsDifference(hist1, hist2, bin_index):
    difference = hist1.GetBinContent(bin_index)-hist2.GetBinContent(bin_index)
    return abs(difference)

#Sum the differences in Quadrature
def sumInQuadrature(differences):
    sumdif2=0
    for difference in differences:
        sumdif2 += difference **2
    rootsumdif2= sumdif2 **0.5
    return rootsumdif2


    
if __name__=="__main__":
    MakePileUpSystematicHistograms(sys.argv[1])
