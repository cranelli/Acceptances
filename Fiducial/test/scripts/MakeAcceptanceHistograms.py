#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F
from ROOT import TH2F
from collections import namedtuple


##########################################################
#Global Variables

# (Reco File Name)
RECO_FILE_LOC = "../Histograms/LepGammaGammaFinalElandMuUnblindAll_2015_4_19_ScaleFactors_PDFReweights/WeightedTotal_RecoCategoryHistograms.root"
# (Gen File Name)
GEN_FILE_LOC = "../Histograms/CommonFiducial_wMT_Skim_PDFReweights/WeightedTotal_GenCategoryHistograms.root"
# (Out File Name)
OUT_FILE_LOC= "../Histograms/Acceptances_test.root"

RECO_FILE = TFile(RECO_FILE_LOC, 'READ')
GEN_FILE = TFile(GEN_FILE_LOC, 'READ')
OUT_FILE = TFile(OUT_FILE_LOC, "RECREATE")

# Specify the Channels and Hist Types to calculate Acceptances for
ChannelPair = namedtuple('ChannelPair','reco_channel gen_decay')
RECO_GEN_PAIRS=[ChannelPair('MuonChannel', 'MuonDecay'), ChannelPair('ElectronChannel', 'ElectronDecay')]

HIST_TYPES=["Count", "Pt", "Category_Pt"]


#For Scale Factor Uncertainties
DO_SCALEFACTORS_UPDN=True
# Channel name must match choice in RECO_GEN_PAIRS
SFS={ 'MuonChannel': ["mu_trigSF", "mu_isoSF", "mu_idSF", "ph_idSF"],
    'ElectronChannel': ["el_trigSF", "ph_idSF", "ph_evetoSF"] }

# PDF Reweighting
DO_PDFSET_REWEIGHT=True
PDFSET_NAMES =[ "cteq6l1", "MSTW2008lo68cl", "cteq66" ]

DO_PDFEIGENVECTOR_REWEIGHT=True
PDFEIGENVECTOR_NAME= "cteq66"
NUM_EIGENVECTORS=45

####################################################################




def MakeAcceptanceHistograms():

    for pair in RECO_GEN_PAIRS:
        for hist_type in HIST_TYPES:
            MakeBasicAcceptanceHistograms(pair, hist_type)
            
            # These Additional Acceptance Histograms,
            # are for use in calculating systematic uncertainties.
            if DO_SCALEFACTORS_UPDN:
                MakeScaleFactorUpDnAcceptanceHistograms(pair, hist_type)
            if DO_PDFSET_REWEIGHT:
                MakePDFSetReweightAcceptanceHistograms(pair, hist_type)
            if DO_PDFEIGENVECTOR_REWEIGHT:
                MakePDFEigenvectorReweightAcceptanceHistograms(pair, hist_type)



# Makes Histograms: Acceptance with Tau as Background, Acceptance with Tau as Signal
def MakeHistograms(recoHistName, genHistName, acceptances_prefix, hist_type):
    recoHist = RECO_FILE.Get(recoHistName)
    genHist = GEN_FILE.Get(genHistName)
    genPlusTauHist = GetGenPlusTauHist(genHistName)
    
    acceptanceTauBkgdName = acceptances_prefix+"_TauBkgd_"+hist_type
    acceptanceTauBkgd = DivideHistograms(recoHist, genHist, acceptanceTauBkgdName)
    acceptanceTauBkgd.Print()
    acceptanceTauBkgd.Write()
    
    acceptanceTauSigName = acceptances_prefix+"_TauSig_"+hist_type
    acceptanceTauSig = DivideHistograms(recoHist, genPlusTauHist, acceptanceTauSigName)
    acceptanceTauSig.Print()
    acceptanceTauSig.Write()
    
    # oneMinusFtau= genHist.GetName()+"_OneMinusFtau"
    # oneMinusFtau = DivideHistograms(genHist, genHistPlustau)
    # oneMinusFtau.Write()


# These are the basic acceptance histograms, gen events are unweighted and
# reco events have the ScaleFactor weights applied.
def MakeBasicAcceptanceHistograms(pair, hist_type):
    #Reco
    recoHistName=pair.reco_channel+"_ScaleFactor_"+hist_type
    #Gen
    genHistName = pair.gen_decay +"_unweighted_"+hist_type
    #Acceptance Prefix
    acceptances_prefix=pair.reco_channel+"_Acceptance"
    #acceptances_prefix=pair.reco_channel+"_over_"+pair.gen_decay+"_Acceptance"
    MakeHistograms(recoHistName, genHistName, acceptances_prefix, hist_type)


# Calculates the Acceptances for the different possilbe scale factors choices.
# Scale Factor change only effects the Reco Histograms.
# Used in calculating the scale factor systematics.
def MakeScaleFactorUpDnAcceptanceHistograms(pair, hist_type):
    directions = ['UP', 'DN']
    for scalefactor_name in SFS[pair.reco_channel]:
        for dir in directions:
            scalefactor_updn_suffix=scalefactor_name+dir
            #Reco
            recoHistName=pair.reco_channel+"_ScaleFactor_"+scalefactor_updn_suffix+"_"+hist_type
            #Gen
            genHistName = pair.gen_decay +"_unweighted_"+hist_type
            #Acceptance Prefix
            acceptance_prefix = pair.reco_channel+"_"+scalefactor_updn_suffix+"_Acceptance"
            MakeHistograms(recoHistName, genHistName, acceptance_prefix, hist_type)


# Calculate the Acceptances for events that have been reweighted to the central value
# of a different PDF set.
def  MakePDFSetReweightAcceptanceHistograms(pair, hist_type):
    for pdf_name in PDFSET_NAMES:
        pdfset_reweight_suffix=pdf_name+"_PDFReweight"
        # Reco
        recoHistName = pair.reco_channel+"_ScaleFactor_"+pdfset_reweight_suffix+"_"+hist_type
        # Gen
        genHistName = pair.gen_decay+"_"+pdfset_reweight_suffix+"_"+hist_type
        # Acceptance Prefix
        acceptance_prefix = pair.reco_channel+"_"+pdfset_reweight_suffix+"_Acceptance"
        MakeHistograms(recoHistName, genHistName, acceptance_prefix, hist_type)


# Calculate the Acceptances for events that have been reweighted from a PDF set's central value,
# to the same set's eigenvector deviation.
def MakePDFEigenvectorReweightAcceptanceHistograms(pair, hist_type):
    for eigenvector_index in range (0, NUM_EIGENVECTORS):
        pdf_eigenvector_reweight_suffix = PDFEIGENVECTOR_NAME+"_"+str(eigenvector_index)+"_PDFEigenvectorReweight"
        # Reco
        recoHistName = pair.reco_channel+"_ScaleFactor_"+pdf_eigenvector_reweight_suffix+"_"+hist_type
        # Gen
        genHistName = pair.gen_decay+"_"+pdf_eigenvector_reweight_suffix+"_"+hist_type
        # Acceptance Prefix
        acceptance_prefix = pair.reco_channel+"_"+pdf_eigenvector_reweight_suffix+"_Acceptance"
        MakeHistograms(recoHistName, genHistName, acceptance_prefix, hist_type)

#From the Generator Name, also gets the Generator Histogram for the same decay through the tau.
# Ie Muon and TauToMuon decay.  Then returns the sume of the two histograms.
def GetGenPlusTauHist(genHistName):
    genHist = GEN_FILE.Get(genHistName)
    
    
    genTauHistName = "TauTo" + genHistName
    genTauHist = GEN_FILE.Get(genTauHistName)
    
    
    genPlusTauHistName = genHistName+"_PlusTau"
    genPlusTauHist = genHist.Clone(genPlusTauHistName)
    genPlusTauHist.Add(genTauHist)

    return genPlusTauHist


# Given Two Histogrmas, divide them, and return the new histogram with the given name.
def DivideHistograms(num_hist, den_hist, divide_hist_name):
    divideHist = num_hist.Clone(divide_hist_name)
    divideHist.Divide(den_hist)
    return divideHist





if __name__=="__main__":
    MakeAcceptanceHistograms()
