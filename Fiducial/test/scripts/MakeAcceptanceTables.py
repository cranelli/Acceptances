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


# Generator Files
GEN_DIR="../Histograms/CommonFiducial_wMT_Skim_PUReweights_PDFReweights/"
WEIGHTED_GEN_FILE= TFile(GEN_DIR+"WeightedTotal_GenCategoryHistograms.root", "READ")

HIST_DIR="../Histograms/NLO_LepGammaGammaFinalElandMu_2015_6_26_ScaleFactors_PDFReweights/"

# Reco Files (w/ Scale Factor)
#RECO_PREFIX="LepGammaGammaFinalElandMuUnblindAll_2015_4_19"
WEIGHTED_RECO_FILE= TFile(HIST_DIR+"WeightedTotal_RecoCategoryHistograms.root", "READ")

# Acceptance Files
ACCEPTANCE_FILE=TFile(HIST_DIR+"Acceptances.root")

# Scale Factor Systematic File
SCALEFACTOR_SYSTEMATIC_FILE=TFile(HIST_DIR+"ScaleFactorSystematics.root")

# PDF Systematic File
PDF_SYSTEMATIC_FILE = TFile(HIST_DIR+"PDFSystematics.root")

#Factorization Renormalization File
#FACTORIZATIONRENORMALIZATION_SYSTEMATIC_FILE = TFile(HIST_DIR+"FactorizationRenormalizationSystematics.root")

# Total Systematic File
TOTAL_SYSTEMATIC_FILE = TFile(HIST_DIR+"TotalSystematics.root")

def MakeAcceptanceTables():
    # Hold Histograms in Dictionaries
    GenHistograms = {}
    RecoHistograms = {}
    AcceptanceHistograms = {}
    PDFSystematicHistograms = {}
    ScaleFactorSystematicHistograms={}
    #RenormalizationFactorizationHistograms={}
    TotalSystematicHistograms={}
    GetHistograms(GenHistograms, RecoHistograms, AcceptanceHistograms, PDFSystematicHistograms, ScaleFactorSystematicHistograms, TotalSystematicHistograms)
    
    #Loop over all the lines in the input file (Table Template)
    for line in fileinput.input():
        line = Replace(line, GenHistograms, RecoHistograms, AcceptanceHistograms, PDFSystematicHistograms, ScaleFactorSystematicHistograms, TotalSystematicHistograms)
        print line,


################### Get Histograms ##########################################################

# From the Global Files, gets the needed Histograms to fill the Acceptance Tables.
def GetHistograms(GenHistograms, RecoHistograms, AcceptanceHistograms, PDFSystematicHistograms, ScaleFactorSystematicHistograms, TotalSystematicHistograms):
    samples = ["WEIGHTED"]
    for sample_type in samples:
        GetGenHistogramsbySample(GenHistograms, sample_type, WEIGHTED_GEN_FILE)
        GetRecoHistogramsBySample(RecoHistograms, sample_type, WEIGHTED_RECO_FILE)

    GetAcceptanceHistograms(AcceptanceHistograms, ACCEPTANCE_FILE)
    GetPDFSystematicHistograms(PDFSystematicHistograms,PDF_SYSTEMATIC_FILE)
    GetScaleFactorSystematicHistograms(ScaleFactorSystematicHistograms, SCALEFACTOR_SYSTEMATIC_FILE)
    #GetFactorizationRenormalizationSystematicHistograms(FactorizationRenormalizationHistograms, FACTORIZATIONRENORMALIZATION_SYSTEMATIC_FILE)
    GetTotalSystematicHistograms(TotalSystematicHistograms, TOTAL_SYSTEMATIC_FILE)

#
# From the input files, adds the generator histograms to the "Histograms" dictionairy.  Their keys correspond
# with the LaTeX placeholder names.
#
def GetGenHistogramsbySample(Histograms, sample_type, file):
    #Decay_Pair=[("ELECTRON", "ElectronDecay"), ("MUON", "MuonDecay"), ("TAUTOELECTRON", "TauToElectronDecay"), ("TAUTOMUON", "TauToMuonDecay")]
    #for key_decay, decay in Decay_Pair:
    
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]
    for key_hist_type, hist_type in hist_type_pair:

        Histograms[sample_type+"_GEN_ELECTRON_"+key_hist_type]=WEIGHTED_GEN_FILE.Get("ElectronDecay_unweighted_"+hist_type)
        Histograms[sample_type+"_GEN_TAUTOELECTRON_"+key_hist_type]=WEIGHTED_GEN_FILE.Get("TauToElectronDecay_unweighted_"+hist_type)
        Histograms[sample_type+"_GEN_MUON_"+ key_hist_type]=WEIGHTED_GEN_FILE.Get("MuonDecay_unweighted_"+hist_type)
        Histograms[sample_type+"_GEN_TAUTOMUON_"+ key_hist_type]=WEIGHTED_GEN_FILE.Get("TauToMuonDecay_unweighted_"+hist_type)

#
# From the input files, adds the reco histograms to the "Histograms" dictionairy.  Their keys correspond
# with the LaTeX placeholder names.
#
def GetRecoHistogramsBySample(Histograms, sample_type, file):
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]
    for key_hist_type, hist_type in hist_type_pair:
        
        Histograms[sample_type+"_RECO_ELECTRON_" + key_hist_type]=WEIGHTED_RECO_FILE.Get("ElectronChannel_ScaleFactor_"+hist_type)
        Histograms[sample_type+"_RECO_MUON_" + key_hist_type]=WEIGHTED_RECO_FILE.Get("MuonChannel_ScaleFactor_"+hist_type)

#
# From the input file, get the Acceptance Histograms.
#
def GetAcceptanceHistograms(Histograms, file):
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]

    for key_hist_type, hist_type in hist_type_pair:
        
        Histograms["ACCEPTANCE_ELECTRON_TAUBKGD_"+key_hist_type] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauBkgd_"+hist_type)
        Histograms["ACCEPTANCE_ELECTRON_TAUSIG_"+key_hist_type] = ACCEPTANCE_FILE.Get("ElectronChannel_Acceptance_TauSig_"+hist_type)
        Histograms["ACCEPTANCE_MUON_TAUBKGD_"+ key_hist_type] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauBkgd_"+hist_type)
        Histograms["ACCEPTANCE_MUON_TAUSIG_" + key_hist_type] = ACCEPTANCE_FILE.Get("MuonChannel_Acceptance_TauSig_"+hist_type)

#
# From the input file, get the PDF Systematic Histogram.
#
def GetPDFSystematicHistograms(Histograms, file):
    dirs = ["UP", "DN"]
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]
    for key_hist_type, hist_type in hist_type_pair:
    
        Histograms["PDF_SYSTEMATIC_ELECTRON_TAUSIG_SET_" + key_hist_type]=PDF_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_PDFSetSystematic_" + hist_type)
        Histograms["PDF_SYSTEMATIC_MUON_TAUSIG_SET_" + key_hist_type]=PDF_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_PDFSetSystematic_" + hist_type)

        for dir in dirs:
            Histograms["PDF_SYSTEMATIC_ELECTRON_TAUSIG_EIGENVECTOR_"+dir+"_" + key_hist_type]= PDF_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_PDFEigenvectorSystematic"+dir+"_" + hist_type)
            
            Histograms["PDF_SYSTEMATIC_MUON_TAUSIG_EIGENVECTOR_"+dir+"_" + key_hist_type]= PDF_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_PDFEigenvectorSystematic"+dir+"_" + hist_type)


#
# From the input file, get the Scale Factor Systematic Histograms, Different Histograms for Electron and Muon Channel.
#
def GetScaleFactorSystematicHistograms(Histograms, file):
   
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]
    dirs = ["UP", "DN"]
    for key_hist_type, hist_type in hist_type_pair:
        for dir in dirs:

            #Electron Channel
            Histograms["SCALEFACTOR_SYSTEMATIC_ELECTRON_TAUSIG_ELTRIGSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_el_trigSF_ScaleFactorSystematic"+dir+ "_" + hist_type)

            Histograms["SCALEFACTOR_SYSTEMATIC_ELECTRON_TAUSIG_PHIDSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_ph_idSF_ScaleFactorSystematic"+dir+ "_" + hist_type)

            Histograms["SCALEFACTOR_SYSTEMATIC_ELECTRON_TAUSIG_PHEVETOSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_ph_evetoSF_ScaleFactorSystematic"+dir+ "_" + hist_type)

#Histograms["SCALEFACTOR_SYSTEMATIC_ELECTRON_TAUSIG_TOTALSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("ElectronChannel_TauSig_ScaleFactorTotalSystematic"+dir+ "_" + hist_type)
            

            #Muon Channel
            Histograms["SCALEFACTOR_SYSTEMATIC_MUON_TAUSIG_MUTRIGSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_mu_trigSF_ScaleFactorSystematic"+dir+"_" + hist_type)
            Histograms["SCALEFACTOR_SYSTEMATIC_MUON_TAUSIG_PHIDSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_ph_idSF_ScaleFactorSystematic"+dir+"_" + hist_type)
            Histograms["SCALEFACTOR_SYSTEMATIC_MUON_TAUSIG_MUIDSF_"+dir+"_" + key_hist_type] = SCALEFACTOR_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_mu_idSF_ScaleFactorSystematic"+dir+"_" + hist_type)
            Histograms["SCALEFACTOR_SYSTEMATIC_MUON_TAUSIG_MUISOSF_"+dir+"_" + key_hist_type] = SCALEFACTOR_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_mu_isoSF_ScaleFactorSystematic"+dir+"_" + hist_type)
#Histograms["SCALEFACTOR_SYSTEMATIC_MUON_TAUSIG_TOTALSF_"+dir+"_" + key_hist_type]= SCALEFACTOR_SYSTEMATIC_FILE.Get("MuonChannel_TauSig_ScaleFactorTotalSystematic"+dir+ "_" + hist_type)

def GetTotalSystematicHistograms(Histograms, file):
    channel_pair = [("ELECTRON", "ElectronChannel"), ("MUON", "MuonChannel")]
    hist_type_pair = [("PT", "Category_Pt"), ("COUNT", "Count")]
    acceptance_type_pair=[("TAUSIG","TauSig"), ("TAUBKGD","TauBkgd")]
    
    dirs = ["UP", "DN"]
    for key_channel, channel in channel_pair:
        for key_acceptance_type, acceptance_type in acceptance_type_pair:
            for key_hist_type, hist_type in hist_type_pair:
                for dir in dirs:
                    #Total ScaleFactor
                    Histograms["TOTAL_SCALEFACTOR_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_ScaleFactorTotalSystematic"+dir+"_"+hist_type)
                        #Total PDF
                    Histograms["TOTAL_PDF_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_PDFTotalSystematic"+dir+"_"+hist_type)
                    #Total Pile Up
                    Histograms["TOTAL_PU_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_PUTotalSystematic"+dir+"_"+hist_type)
                    #Total Renormalization
                    Histograms["TOTAL_RENORMALIZATION_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_RenormalizationTotalSystematic"+dir+"_"+hist_type)
                    #Total Factorization
                    Histograms["TOTAL_FACTORIZATION_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_FactorizationTotalSystematic"+dir+"_"+hist_type)

                    Histograms["TOTAL_SYSTEMATIC_"+dir+"_"+key_channel+"_"+key_acceptance_type+"_"+key_hist_type]= TOTAL_SYSTEMATIC_FILE.Get(channel+"_"+acceptance_type+"_TotalSystematic"+dir+"_"+hist_type)





                                                  
##################################################################################

############### Replace Place Holders ############################################

# Replace Place Holders
def Replace(line, GenHistograms, RecoHistograms, AcceptanceHistograms, PDFSystematicHistograms, ScaleFactorSystematicHistograms, TotalSystematicHistograms):
    line = ReplaceGen(line, GenHistograms)
    line = ReplaceReco(line, RecoHistograms)
    line = ReplaceAcceptance(line, AcceptanceHistograms)
    line = ReplacePDFSystematic(line, PDFSystematicHistograms)
    line = ReplaceScaleFactorSystematic(line, ScaleFactorSystematicHistograms)
    line = ReplaceTotalSystematic(line, TotalSystematicHistograms)
    return line

# Replaces the PlaceHolders Corresponding to Generator Quantities
def ReplaceGen(line, Histograms):
    for key in Histograms:
        line = ReplaceRecoGenPlaceHolders(line, Histograms,key)
    return line

# Replaces the PlaceHolders Corresponding to Reco Quantities
def ReplaceReco(line, Histograms):
    for key in Histograms:
        line = ReplaceRecoGenPlaceHolders(line, Histograms, key)
    return line

#Replaces the PlaceHolders Corresponding to Acceptance Quantities
def ReplaceAcceptance(line, Histograms):
    for key in Histograms:
        line = ReplaceAcceptancePlaceHolders(line, Histograms,key)
    return line

# Replaces the PlaceHolders Corresponding to PDF Systematics:
def ReplacePDFSystematic(line, Histograms):
    for key in Histograms:
        line = ReplacePDFSystematicPlaceHolders(line, Histograms, key)
    return line

# Replaces the PlaceHolders Corresponding to Scale Factor Systematics:
def ReplaceScaleFactorSystematic(line, Histograms):
    for key in Histograms:
        line = ReplaceScaleFactorSystematicPlaceHolders(line, Histograms, key)
    return line

# Replaces the PlaceHolders Corresponding to Total Systematics:
def ReplaceTotalSystematic(line, Histograms):
    for key in Histograms:
        line = ReplaceTotalSystematicPlaceHolders(line, Histograms, key)
    return line

# Handles the Formating for Both Reco and Gen Place Holders
def ReplaceRecoGenPlaceHolders(line, Histograms, key):
    if "PT" in key:
        pts = GetPtBins(key, Histograms)
        for i in range(0, len(pts)):
            line = re.sub(key+str(i+1),str(format(pts[i],'.1f')), line)
    
    if "COUNT" in key:
        total = GetTotalBin(key, Histograms)
        line = re.sub(key,str(format(total,'.1f')), line)
    return line

#Handles the Formatting for the Acceptances (Includes the Statistical Uncertainties)
def ReplaceAcceptancePlaceHolders(line, Histograms, key):
    if "PT" in key:
        pts = GetPtBins(key, Histograms)
        pt_errors = GetPtErrors(key, Histograms)
        for i in range(0, len(pts)):
            line = re.sub(key+str(i+1),str(format(pts[i]*100,'.2f'))+ " $\pm$ " + str(format(pt_errors[i]*100,'.2f')), line)
    
    if "COUNT" in key:
        total = GetTotalBin(key, Histograms)
        total_error = GetTotalError(key, Histograms)
    
        line = re.sub(key,str(format(total*100,'.2f')) + " $\pm$ " + str(format(total_error*100,'.2f')), line)

    return line

#Handles the Formatting for the PDF Systematics
def ReplacePDFSystematicPlaceHolders(line, Histograms, key):
    if "COUNT" in key:
        total = GetTotalBin(key, Histograms)

        line = re.sub(key,str(format(total*100,'.2f')), line)
    return line

#Handles the Formatting for the Scale Factor Systematics
def ReplaceScaleFactorSystematicPlaceHolders(line, Histograms, key):
    if "COUNT" in key:
        total = GetTotalBin(key, Histograms)
        line = re.sub(key,str(format(total*100,'.2f')), line)
    return line

#Handles the Formatting for the Total Systematics
def ReplaceTotalSystematicPlaceHolders(line, Histograms, key):
    if "COUNT" in key:
        total = GetTotalBin(key, Histograms)
        line = re.sub(key,str(format(total*100,'.2f')), line)
    if "PT" in key:
        pt_systs = GetPtBins(key, Histograms)
        for i in range(0, len(pt_systs)):
            line = re.sub(key+str(i+1),str(format(pt_systs[i]*100,'.2f')), line)

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
