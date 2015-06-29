#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

CHANNELS=["MuonChannel", "ElectronChannel"]
HIST_TYPES=["Category_Pt", "Count"]
ACCEPTANCE_TYPES=["TauSig", "TauBkgd"]


def MakeFactorizationRenormalizationSystematicHistograms(hist_dir):

    file_loc =hist_dir+"Acceptances.root"
    file = TFile(file_loc, 'READ')

    outfile_loc=hist_dir+"FactorizationRenormalizationSystematics.root"
    outfile=TFile(outfile_loc, 'RECREATE')
    
    for channel in CHANNELS:
        for acceptance_type in ACCEPTANCE_TYPES:
            for hist_type in HIST_TYPES:
                MakeFactorizationSystematicHistograms(file, outfile, channel, acceptance_type, hist_type)
                MakeRenormalizationSystematicHistograms(file, outfile, channel, acceptance_type, hist_type)



# Goes over each channel's factorization weights,and makes the factorization Syst Histogram.
# The master equation is used to calculate the upper and lower bounds.
def MakeFactorizationSystematicHistograms(file, outfile, channel, acceptance_type, hist_type):
    expectedHistName=channel+"_Acceptance_"+acceptance_type+"_"+hist_type
    expectedHist = file.Get(expectedHistName)
    
    # Histogram of Acceptances with Half Factorization Scale
    
    factorizationHistHalfName = channel+"_"+"Half_Factorization"+"_Acceptance_"+acceptance_type+"_"+hist_type
    factorizationHistHalf= file.Get(factorizationHistHalfName)
    
    factorizationHistDoubleName = channel+"_"+"Double_Factorization"+"_Acceptance_"+acceptance_type+"_"+hist_type
    factorizationHistDouble= file.Get(factorizationHistDoubleName)
    
    # Up Factorization Systematics
    factorizationSystematicUPHistName=channel+"_"+acceptance_type+"_FactorizationSystematicUP"+"_"+hist_type
    factorizationSystematicUPHist = expectedHist.Clone(factorizationSystematicUPHistName)
    factorizationSystematicUPHist.Reset("ICE")
    
    # DN Factorization Systematics
    factorizationSystematicDNHistName=channel+"_"+acceptance_type+"_FactorizationSystematicDN"+"_"+hist_type
    factorizationSystematicDNHist = expectedHist.Clone(factorizationSystematicDNHistName)
    factorizationSystematicDNHist.Reset("ICE")
    
    
    # Loop over All bins in the Histogram, including the overflow bin.
    # Use Master equation because change in factorization changes both
    # the numerator and denominator of the Acceptance
    for bin_index in range(1, expectedHist.GetNbinsX()+2):
        central_value =expectedHist.GetBinContent(bin_index)
        half_value = factorizationHistHalf.GetBinContent(bin_index)
        double_value = factorizationHistDouble.GetBinContent(bin_index)
        
        factorizationSystUP = abs(masterDifferenceUP(central_value, double_value, half_value))
        factorizationSystDN = abs(masterDifferenceDN(central_value, double_value, half_value))
        
        factorizationSystematicUPHist.SetBinContent(bin_index, factorizationSystUP)
        factorizationSystematicDNHist.SetBinContent(bin_index, factorizationSystDN)
    
    
    factorizationSystematicUPHist.Print("all")
    factorizationSystematicUPHist.Write()

    factorizationSystematicDNHist.Print("all")
    factorizationSystematicDNHist.Write()



# Goes over each channel's renormalization weights,and makes the renormalization Syst Histogram.
# The master equation is used to calculate the upper and lower bounds.
def MakeRenormalizationSystematicHistograms(file, outfile, channel, acceptance_type, hist_type):
    expectedHistName=channel+"_Acceptance_"+acceptance_type+"_"+hist_type
    expectedHist = file.Get(expectedHistName)
        #for renormalization_variation in RENORMALIZATION_VARIATIONS:
        # Histogram of Acceptances with Half Renormalization Scale
        
    renormalizationHistHalfName = channel+"_"+"Half_Renormalization"+"_Acceptance_"+acceptance_type+"_"+hist_type
    renormalizationHistHalf= file.Get(renormalizationHistHalfName)

    renormalizationHistDoubleName = channel+"_"+"Double_Renormalization"+"_Acceptance_"+acceptance_type+"_"+hist_type
    renormalizationHistDouble= file.Get(renormalizationHistDoubleName)

    # Up Renormalization Systematics
    renormalizationSystematicUPHistName=channel+"_"+acceptance_type+"_RenormalizationSystematicUP"+"_"+hist_type
    renormalizationSystematicUPHist = expectedHist.Clone(renormalizationSystematicUPHistName)
    renormalizationSystematicUPHist.Reset("ICE")
              
    # DN Renormalization Systematics
    renormalizationSystematicDNHistName=channel+"_"+acceptance_type+"_RenormalizationSystematicDN"+"_"+hist_type
    renormalizationSystematicDNHist = expectedHist.Clone(renormalizationSystematicDNHistName)
    renormalizationSystematicDNHist.Reset("ICE")
                                                  
    # Loop over All bins in the Histogram, including the overflow bin.
    # Use Master equation because change in renormalization changes both
    # the numerator and denominator of the Acceptance
    for bin_index in range(1, expectedHist.GetNbinsX()+2):
        central_value =expectedHist.GetBinContent(bin_index)
        half_value = renormalizationHistHalf.GetBinContent(bin_index)
        double_value = renormalizationHistDouble.GetBinContent(bin_index)
            
        renormalizationSystUP = abs(masterDifferenceUP(central_value, double_value, half_value))
        renormalizationSystDN = abs(masterDifferenceDN(central_value, double_value, half_value))
            
        renormalizationSystematicUPHist.SetBinContent(bin_index, renormalizationSystUP)
        renormalizationSystematicDNHist.SetBinContent(bin_index, renormalizationSystDN)
                
    renormalizationSystematicUPHist.Print("all")
    renormalizationSystematicUPHist.Write()
                        
    renormalizationSystematicDNHist.Print("all")
    renormalizationSystematicDNHist.Write()


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
    MakeFactorizationRenormalizationSystematicHistograms(sys.argv[1])
