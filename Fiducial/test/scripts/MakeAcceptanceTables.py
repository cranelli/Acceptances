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

fileLoc ="../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"
outFileDir="../Tables/Weighted_GEN_StatErrors/"


HIST_DIR="../Histograms/"
Header= " \n"

NUM_PT_BINS=4

#
# Generator Information
#
GEN_PREFIX="CommonFiducial_wMT_Skim"
WEIGHTED_GEN_FILE= TFile(HIST_DIR+GEN_PREFIX+"/"+GEN_PREFIX+"_PDFReweights_WeightedTotal_GenCategoryHistograms.root", "READ")
WEIGHTED_GEN_ELECTRON_PT_HIST=WEIGHTED_GEN_FILE.Get("ElectronDecay_unweighted_Category_Pt")
WEIGHTED_GEN_ELECTRON_COUNT_HIST=WEIGHTED_GEN_FILE.Get("ElectronDecay_unweighted_Count")
WEIGHTED_GEN_MUON_PT_HIST=WEIGHTED_GEN_FILE.Get("MuonDecay_unweighted_Category_Pt")
WEIGHTED_GEN_MUON_COUNT_HIST=WEIGHTED_GEN_FILE.Get("MuonDecay_unweighted_Count")

#
# Reco Information (w/ Scale Factor)
#
RECO_PREFIX="LepGammaGammaFinalElandMuUnblindAll_2015_4_19"
WEIGHTED_RECO_FILE= TFile(HIST_DIR+RECO_PREFIX+"/"+RECO_PREFIX+"_ScaleFactors_PDFReweights_WeightedTotal_RecoCategoryHistograms.root", "READ")
WEIGHTED_RECO_ELECTRON_PT_HIST=WEIGHTED_RECO_FILE.Get("ElectronChannel_ScaleFactor_Category_Pt")
WEIGHTED_RECO_ELECTRON_COUNT_HIST=WEIGHTED_RECO_FILE.Get("ElectronChannel_ScaleFactor_Count")
WEIGHTED_RECO_MUON_PT_HIST=WEIGHTED_RECO_FILE.Get("MuonChannel_ScaleFactor_Category_Pt")
WEIGHTED_RECO_MUON_COUNT_HIST=WEIGHTED_RECO_FILE.Get("MuonChannel_ScaleFactor_Count")


def MakeAcceptanceTables():
    # Gen Information
    weighted_gen_electron_pt=getPtBins(WEIGHTED_GEN_ELECTRON_PT_HIST)
    weighted_gen_electron_total=getTotalBin(WEIGHTED_GEN_ELECTRON_COUNT_HIST)
    weighted_gen_muon_pt=getPtBins(WEIGHTED_GEN_MUON_PT_HIST)
    weighted_gen_muon_total=getTotalBin(WEIGHTED_GEN_MUON_COUNT_HIST)
    # Reco Information
    weighted_reco_electron_pt=getPtBins(WEIGHTED_RECO_ELECTRON_PT_HIST)
    weighted_reco_electron_total=getTotalBin(WEIGHTED_RECO_ELECTRON_COUNT_HIST)
    weighted_reco_muon_pt=getPtBins(WEIGHTED_RECO_MUON_PT_HIST)
    weighted_reco_muon_total=getTotalBin(WEIGHTED_RECO_MUON_COUNT_HIST)
    
    #Loop over all the lines in the input file (Table Template)
    for line in fileinput.input():
        # Gen Replacements
        line = ReplaceWeightPt(line, weighted_gen_electron_pt, "GEN", "ELECTRON")
        line = ReplaceWeightTotal(line, weighted_gen_electron_total, "GEN", "ELECTRON")
        line = ReplaceWeightPt(line, weighted_gen_muon_pt, "GEN", "MUON")
        line = ReplaceWeightTotal(line, weighted_gen_muon_total, "GEN", "MUON")
        # Reco Replacements
        line = ReplaceWeightPt(line, weighted_reco_electron_pt, "RECO", "ELECTRON")
        line = ReplaceWeightTotal(line, weighted_reco_electron_total, "RECO", "ELECTRON")
        line = ReplaceWeightPt(line, weighted_reco_muon_pt, "RECO", "MUON")
        line = ReplaceWeightTotal(line, weighted_reco_muon_total, "RECO", "MUON")
        print line,

# Given the line, a list of Pt Counts, and the decay name, replaces the Pt placeholders
# in the latex file, with the match Pt Counts
def ReplaceWeightPt(line, weighted_pt, sim_type, lepton):
    for i in range(0,4):
        line = re.sub('WEIGHTED_'+ sim_type +'_'+lepton+'_PT'+str(i+1),str(format(weighted_pt[i],'.1f')), line)
    return line

#Replaces the Total placeholders with the Total Counts for each decay
def ReplaceWeightTotal(line, weighted_gen_total, sim_type, lepton):
    line = re.sub('WEIGHTED_'+sim_type+'_'+lepton+'_TOTAL',str(format(weighted_gen_total,'.1f')), line)
    return line

# Given a Pt Histogram, returns a list of the Bin Contents
def getPtBins(pt_hist):
    pts=[]
    for i in range(0,4):
        pts.append(pt_hist.GetBinContent(i+1))
    # For the Last Bin Add on the Overflow
    #pts[i]+=pt_hist.GetBinContent(i+2)
    return pts

# Given a Count Histogram, returns the total number of events
def getTotalBin(count_hist):
    return count_hist.GetBinContent(2)

    
                                                                                                 
    
if __name__=="__main__":
    MakeAcceptanceTables()
