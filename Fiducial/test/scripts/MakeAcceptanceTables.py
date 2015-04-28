# Python Code for looking at the Histograms in root
# files, to make the Acceptances tables for the WGamGam 
# Analysis.
# Example Execution
# python MakeAcceptanceTables AcceptanceTable_Temp.tex
import sys
import fileinput
import re #regular expression module

from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

#fileLoc ="../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"
#outFileDir="../Tables/Weighted_GEN_StatErrors/"


HIST_DIR="../Histograms/"

# Generator Files
GEN_PREFIX="CommonFiducial_wMT_Skim_PDFReweights"
WEIGHTED_GEN_FILE= TFile(HIST_DIR+GEN_PREFIX+"/"+"WeightedTotal_GenCategoryHistograms.root", "READ")


# Reco Files (w/ Scale Factor)
RECO_PREFIX="LepGammaGammaFinalElandMuUnblindAll_2015_4_19"
WEIGHTED_RECO_FILE= TFile(HIST_DIR+RECO_PREFIX+"/"+RECO_PREFIX+"_ScaleFactors_PDFReweights_WeightedTotal_RecoCategoryHistograms.root", "READ")

# Acceptance Files
ACCEPTANCE_FILE=TFile(HIST_DIR+"LepGammaGammaFinalElandMuUnblindAll_2015_4_19_ScaleFactors_PDFReweights/Acceptances_test.root")


def MakeAcceptanceTables():
    # Hold Histograms in Dictionaries
    GenHistograms = {}
    RecoHistograms = {}
    AcceptanceHistograms = {}
    GetHistograms(GenHistograms, RecoHistograms, AcceptanceHistograms)
    
    #Loop over all the lines in the input file (Table Template)
    for line in fileinput.input():
        line = Replace(line, GenHistograms, RecoHistograms, AcceptanceHistograms)
        print line,


################### Get Histograms ##########################################################

# From the Global Files, gets the needed Histograms to fill the Acceptance Tables.
def GetHistograms(GenHistograms, RecoHistograms, AcceptanceHistograms):
    samples = ["WEIGHTED"]
    for sample_type in samples:
        GetGenHistogramsbySample(GenHistograms, sample_type, WEIGHTED_GEN_FILE)
        GetRecoHistogramsBySample(RecoHistograms, sample_type, WEIGHTED_RECO_FILE)
    GetAcceptanceHistograms(AcceptanceHistograms, ACCEPTANCE_FILE)


# From the input files, adds the generator histograms to the "Histograms" dictionairy.  Their keys correspond
# with the LaTeX placeholder names.
def GetGenHistogramsbySample(Histograms, sample_type, file):
    #Pt Hists
    Histograms[sample_type+"_GEN_ELECTRON_PT"]=WEIGHTED_GEN_FILE.Get("ElectronDecay_unweighted_Category_Pt")
    Histograms[sample_type+"_GEN_TAUTOELECTRON_PT"]=WEIGHTED_GEN_FILE.Get("TauToElectronDecay_unweighted_Category_Pt")
    Histograms[sample_type+"_GEN_MUON_PT"]=WEIGHTED_GEN_FILE.Get("MuonDecay_unweighted_Category_Pt")
    Histograms[sample_type+"_GEN_TAUTOMUON_PT"]=WEIGHTED_GEN_FILE.Get("TauToMuonDecay_unweighted_Category_Pt")
    
    #Counting Hists
    Histograms[sample_type+"_GEN_ELECTRON_TOTAL"]=WEIGHTED_GEN_FILE.Get("ElectronDecay_unweighted_Count")
    Histograms[sample_type+"_GEN_TAUTOELECTRON_TOTAL"]=WEIGHTED_GEN_FILE.Get("TauToElectronDecay_unweighted_Count")
    Histograms[sample_type+"_GEN_MUON_TOTAL"]=WEIGHTED_GEN_FILE.Get("MuonDecay_unweighted_Count")
    Histograms[sample_type+"_GEN_TAUTOMUON_TOTAL"]=WEIGHTED_GEN_FILE.Get("TauToMuonDecay_unweighted_Count")

# From the input files, adds the reco histograms to the "Histograms" dictionairy.  Their keys correspond
# with the LaTeX placeholder names.
def GetRecoHistogramsBySample(Histograms, sample_type, file):
    #Pt Hists
    Histograms[sample_type+"_RECO_ELECTRON_PT"]=WEIGHTED_RECO_FILE.Get("ElectronChannel_ScaleFactor_Category_Pt")
    Histograms[sample_type+"_RECO_MUON_PT"]=WEIGHTED_RECO_FILE.Get("MuonChannel_ScaleFactor_Category_Pt")
    #Counting Hists
    Histograms[sample_type+"_RECO_ELECTRON_TOTAL"]=WEIGHTED_RECO_FILE.Get("ElectronChannel_ScaleFactor_Count")
    Histograms[sample_type+"_RECO_MUON_TOTAL"]=WEIGHTED_RECO_FILE.Get("MuonChannel_ScaleFactor_Count")

# From the input files, get the Acceptance Histograms.
def GetAcceptanceHistograms(Histograms, file):
    Histograms["ACCEPTANCE_ELECTRON_TAUBKGD_PT"] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauBkgd_Category_Pt")
    Histograms["ACCEPTANCE_ELECTRON_TAUSIG_PT"] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauSig_Category_Pt")
    Histograms["ACCEPTANCE_MUON_TAUBKGD_PT"] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauBkgd_Category_Pt")
    Histograms["ACCEPTANCE_MUON_TAUSIG_PT"] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauSig_Category_Pt")

    Histograms["ACCEPTANCE_ELECTRON_TAUBKGD_TOTAL"] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauBkgd_Count")
    Histograms["ACCEPTANCE_ELECTRON_TAUSIG_TOTAL"] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauSig_Count")
    Histograms["ACCEPTANCE_MUON_TAUBKGD_TOTAL"] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauBkgd_Count")
    Histograms["ACCEPTANCE_MUON_TAUSIG_TOTAL"] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauSig_Count")
                                                  
                                                  
##################################################################################

############### Replace Place Holders ############################################

# Replace Place Holders
def Replace(line, GenHistograms, RecoHistograms, AcceptanceHistograms):
    samples = ["WEIGHTED"]
    for sample_type in samples:
        line = ReplaceGen(line, GenHistograms, sample_type)
        line = ReplaceReco(line, RecoHistograms, sample_type)
    line = ReplaceAcceptance(line, AcceptanceHistograms)
    return line

# Replaces the PlaceHolders Corresponding to Generator Quantities
def ReplaceGen(line, Histograms, sample_type):
    sim_type = "GEN"
    lepton_decays = ["ELECTRON", "TAUTOELECTRON","MUON","TAUTOMUON"]
    for lepton_type in lepton_decays:
        key_prefix = sample_type+"_"+sim_type+"_"+lepton_type
        line = ReplaceRecoGenPlaceHolders(line, Histograms,key_prefix)
    return line

# Replaces the PlaceHolders Corresponding to Reco Quantities
def ReplaceReco(line, Histograms, sample_type):
    sim_type = "RECO"
    lepton_channels = ["ELECTRON","MUON"]
    for lepton_type in lepton_channels:
        key_prefix = sample_type+"_"+sim_type+"_"+lepton_type
        line = ReplaceRecoGenPlaceHolders(line, Histograms,key_prefix)
    return line

#Replaces the PlaceHolders Corresponding to Acceptance Quantities
def ReplaceAcceptance(line, Histograms):
    lepton_channels = ["ELECTRON","MUON"]
    tau_handlers = ["TAUSIG", "TAUBKGD"]
    for lepton_type in lepton_channels:
        for acceptance_type in tau_handlers:
            key_prefix = "ACCEPTANCE_"+lepton_type+"_"+acceptance_type
            line = ReplaceAcceptancePlaceHolders(line, Histograms,key_prefix)
    return line

# Handles the Formating for Both Reco and Gen Place Holders
def ReplaceRecoGenPlaceHolders(line, Histograms, key_prefix):
    pt_key = key_prefix+"_PT"
    total_key = key_prefix+"_TOTAL"
    pts = GetPtBins(pt_key, Histograms)
    total = GetTotalBin(total_key, Histograms)

    for i in range(0, len(pts)):
        line = re.sub(pt_key+str(i+1),str(format(pts[i],'.1f')), line)

    line = re.sub(total_key,str(format(total,'.1f')), line)
    return line

def ReplaceAcceptancePlaceHolders(line, Histograms, key_prefix):
    pt_key = key_prefix+"_PT"
    total_key = key_prefix+"_TOTAL"
    pts = GetPtBins(pt_key, Histograms)
    pt_errors = GetPtErrors(pt_key, Histograms)
    total = GetTotalBin(total_key, Histograms)
    total_error = GetTotalError(total_key, Histograms)
    
    for i in range(0, len(pts)):
        line = re.sub(pt_key+str(i+1),str(format(pts[i]*100,'.2f'))+ " $\pm$ " + str(format(pt_errors[i]*100,'.2f')), line)
    
    line = re.sub(total_key,str(format(total*100,'.2f')) + " $\pm$ " + str(format(total_error*100,'.2f')), line)
    return line


# Given a Pt Histogram, returns a list of the Bin Contents
def GetPtBins(key, Histograms):
    pts=[]
    pt_hist = Histograms[key]
    num_pt_bins =4
    for i in range(0,num_pt_bins):
        pts.append(pt_hist.GetBinContent(i+1))
    # For the Last Bin Add on the Overflow
    #pts[i]+=pt_hist.GetBinContent(i+2)
    return pts

# Given a Count Histogram, returns the total number of events
def GetTotalBin(key, Histograms):
    count_hist = Histograms[key]
    return count_hist.GetBinContent(2)

# Given a Pt Histogram, returns a list of the Bin Errors
def GetPtErrors(key, Histograms):
    pt_errors=[]
    pt_hist = Histograms[key]
    num_pt_bins =4
    for i in range(0,num_pt_bins):
        pt_errors.append(pt_hist.GetBinError(i+1))
    # For the Last Bin Add on the Overflow
    #pts[i]+=pt_hist.GetBinContent(i+2)
    return pt_errors

# Given a Count Histogram, returns the statistical error on the total number of events
def GetTotalError(key, Histograms):
    count_hist = Histograms[key]
    return count_hist.GetBinError(2)

# Given the line, a list of Pt Counts, and the decay name, replaces the Pt placeholders
# in the latex file, with the match Pt Counts
#def ReplacePtHolders(line, Histograms, key_prefix):
#    key = key_prefix+"_PT"
#    pt_hist = Histograms[key]
#    num_pt_bins =4
#    for i in range(0,num_pt_bins):
#        value = pt_hist.GetBinContent(i+1)
#        line = re.sub(key+str(i+1),str(format(value,'.1f')), line)
#    return line

#Replaces the Total placeholders with the Total Counts for each decay
#def ReplaceTotalHolders(line, Histograms,key_prefix):
#    key = key_prefix+"_TOTAL"
#    count_hist = Histograms[key]
#    value = count_hist.GetBinContent(2)
#    line = re.sub(key,str(format(value,'.1f')), line)
#    return line

    
                                                                                                 
    
if __name__=="__main__":
    MakeAcceptanceTables()
