#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

HIST_DIR="../Histograms/NLO_LepGammaGammaFinalElandMu_2015_6_26_ScaleFactors_PDFReweights/"

CHANNELS=["MuonChannel", "ElectronChannel"]
ACCEPTANCE_TYPES=["TauSig", "TauBkgd"]
HIST_TYPES=["Category_Pt", "Count"]
DIRS = ["UP", "DN"]

# Scale Factor Systematics
SCALEFACTOR_SYST_FILE_LOC=HIST_DIR + "ScaleFactorSystematics.root"
SCALEFACTOR_SYST_FILE = TFile(SCALEFACTOR_SYST_FILE_LOC, 'READ')

SCALEFACTOR_SYSTEMATICS={ 'MuonChannel': ["mu_trigSF", "mu_isoSF", "mu_idSF", "ph_idSF"],
    'ElectronChannel': ["el_trigSF", "ph_idSF", "ph_evetoSF"] }

# PDF Systematics
PDF_SYST_FILE_LOC = HIST_DIR+"PDFSystematics.root"
PDF_SYST_FILE = TFile(PDF_SYST_FILE_LOC, 'READ')
PDF_SYSTEMATICS={'UP':["PDFSetSystematic", "PDFEigenvectorSystematicUP"], 'DN':["PDFSetSystematic", "PDFEigenvectorSystematicUP"]}

# PileUp Systematics
PILEUP_SYST_FILE_LOC= HIST_DIR+"PileUpSystematics.root"
PILEUP_SYST_FILE = TFile(PILEUP_SYST_FILE_LOC, 'READ')
PILEUP_NUM= "5"

# RenormalizationFactorization_Systematics
FACTORIZATION_RENORMALIZATION_SYST_FILE_LOC=HIST_DIR+"FactorizationRenormalizationSystematics.root"
FACTORIZATION_RENORMALIZATION_SYST_FILE= TFile(FACTORIZATION_RENORMALIZATION_SYST_FILE_LOC, 'READ')

# Out File
OUTFILELOC=HIST_DIR+"TotalSystematics.root"
OUTFILE=TFile(OUTFILELOC, 'RECREATE')


def MakeTotalSystematicHistograms_All():
    
    #list = file.GetListOfKeys()
    for channel in CHANNELS:
        for acceptance_type in ACCEPTANCE_TYPES:
            for hist_type in HIST_TYPES:
                MakeTotalSystematicHistograms(channel, acceptance_type, hist_type)


# Makes and Writes the Scale Factor, PDF, PileUp, and Penultement Total Histograms (Both Upper and Lower)
def MakeTotalSystematicHistograms(channel, acceptance_type, hist_type):
    
    for dir in DIRS:
        hists = []
        # Scale Factor
        total_scalefactor_syst_hist = MakeTotalSFSystematicHistogram(channel, acceptance_type, dir, hist_type)
        total_scalefactor_syst_hist.Write()
        hists.append(total_scalefactor_syst_hist)
        
        # PDF
        total_pdf_syst_hist = MakeTotalPDFSystematicHistogram(channel, acceptance_type, dir, hist_type);
        total_pdf_syst_hist.Write()
        hists.append(total_pdf_syst_hist)

        #Pile Up
        total_pileup_syst_hist = MakeTotalPileUpSystematicHistogram(channel, acceptance_type, dir, hist_type)
        total_pileup_syst_hist.Write()
        hists.append(total_pileup_syst_hist)

        #Renormalization
        total_renormalization_syst_hist = MakeTotalRenormalizationHistogram(channel, acceptance_type, dir, hist_type)
        total_renormalization_syst_hist.Write()
        hists.append(total_renormalization_syst_hist)

        #Factorization
        total_factorization_syst_hist = MakeTotalFactorizationSystematicHistogram(channel, acceptance_type, dir, hist_type)
        total_factorization_syst_hist.Write()
        hists.append(total_factorization_syst_hist)

        total_syst_hist=SumHistsInQuadrature(hists,channel+"_"+acceptance_type+"_TotalSystematic"+dir+"_"+hist_type)
        total_syst_hist.Write()


# Adds the systematics for each scale factor in quadrature to get the total scale factor systematic.
# Stores in a Histogram
def MakeTotalSFSystematicHistogram(channel, acceptance_type, dir, hist_type):
    
    #SCALEFACTOR_SYST_FILE.Print()
    
    scalefactor_syst_hists=[]
    for scalefactor in SCALEFACTOR_SYSTEMATICS[channel]:
        scalefactor_syst_hist_name = channel+"_"+acceptance_type+"_"+scalefactor+"_ScaleFactorSystematic"+dir+"_"+hist_type
        scalefactor_syst_hist = SCALEFACTOR_SYST_FILE.Get(scalefactor_syst_hist_name)
        scalefactor_syst_hists.append(scalefactor_syst_hist)
    
    total_scalefactor_syst = SumHistsInQuadrature(scalefactor_syst_hists, channel+"_"+acceptance_type+"_ScaleFactorTotalSystematic"+dir+"_"+hist_type)
    return total_scalefactor_syst

# Adds the systematics for each PDF in quadrature to get the total scale factor systematic.
# Stores in a Histogram
def MakeTotalPDFSystematicHistogram(channel, acceptance_type, dir, hist_type):
    pdf_syst_hists=[]
    for pdf in PDF_SYSTEMATICS[dir]:
        pdf_syst_hist_name = channel+"_"+acceptance_type+"_"+pdf+"_"+hist_type
        pdf_syst_hist = PDF_SYST_FILE.Get(pdf_syst_hist_name)
        pdf_syst_hists.append(pdf_syst_hist)
    
    total_pdf_syst = SumHistsInQuadrature(pdf_syst_hists, channel+"_"+acceptance_type+"_PDFTotalSystematic"+dir+"_"+hist_type)
    return total_pdf_syst

# Only One Systematic for the PileUp so it is easy to Total
def MakeTotalPileUpSystematicHistogram(channel, acceptance_type, dir, hist_type):
    pileup_syst_hist = PILEUP_SYST_FILE.Get(channel+"_"+acceptance_type+"_PUWeight_"+PILEUP_NUM+"_pileupSystematic"+dir+"_"+hist_type)
    total_pileup_syst_hist = pileup_syst_hist.Clone(channel+"_"+acceptance_type+"_PUTotalSystematic"+dir+"_"+hist_type)
    return total_pileup_syst_hist

# Only One Systematic for the Renormalization so it is easy to Total
def MakeTotalRenormalizationHistogram(channel, acceptance_type, dir, hist_type):
    renormalization_syst_hist = FACTORIZATION_RENORMALIZATION_SYST_FILE.Get(channel+"_"+acceptance_type+"_RenormalizationSystematic"+dir+"_"+hist_type)
    total_renormalization_syst_hist = renormalization_syst_hist.Clone(channel+"_"+acceptance_type+"_RenormalizationTotalSystematic"+dir+"_"+hist_type)
    return total_renormalization_syst_hist

# Only One Systematic for the Factorization so it is easy to Total
def MakeTotalFactorizationSystematicHistogram(channel, acceptance_type, dir, hist_type):
    factorization_syst_hist = FACTORIZATION_RENORMALIZATION_SYST_FILE.Get(channel+"_"+acceptance_type+"_FactorizationSystematic"+dir+"_"+hist_type)
    total_factorization_syst_hist = factorization_syst_hist.Clone(channel+"_"+acceptance_type+"_FactorizationTotalSystematic"+dir+"_"+hist_type)
    return total_factorization_syst_hist


# Takes a List of Hists and returns a Histogram, with the values from each bin summed in quadrature
def SumHistsInQuadrature(hists, name):
    hist_template = hists[0]
    hist_summed_in_quad = hist_template.Clone(name)
    hist_summed_in_quad.Reset("ICE")

    # Include Overflow
    for bin_index in range(1, hist_summed_in_quad.GetNbinsX()+2):
        systematics=[]
        for hist in hists:
            systematics.append(hist.GetBinContent(bin_index))

        total_syst = sumInQuadrature(systematics)
        hist_summed_in_quad.SetBinContent(bin_index, total_syst)

    return hist_summed_in_quad


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
    MakeTotalSystematicHistograms_All()
