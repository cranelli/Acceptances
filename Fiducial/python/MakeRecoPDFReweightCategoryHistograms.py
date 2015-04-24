# Python Code for Histograming events based on their
# RECO values.  Splits signal events between the different
# channels and our different categories.
# 
# Example execution from command line:
# python MakeRecoPDFReweightCategoryHistograms.py /data/users/cranelli/WGamGam/Acceptances/AnalysisRECOCuts_Skim/LepGammaGammaFinalEl_2015_03_31_ScaleFactors_PDFReweights/job_summer12_WAA_ISR/tree.root test.root
#

import sys

from ROOT import TFile
from ROOT import TTree
from ROOT import vector

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histogramBuilder

# Define Global Variables

TREELOC="EventTree"
OUTDIR="../test/Histograms/"

# Unweighted Histograms
DO_UNWEIGHTED=True

# With Scale Factor Weight
DO_SCALEFACTOR = True


#Central PDF Reweighting
DO_CENTRAL_PDF_REWEIGHT=True
PDF_NAMES=['cteq6l1', 'MSTW2008lo68cl', 'cteq66'] #cteq6l1 is the original
ORIG_PDF_NAME = 'cteq6l1'

#Eigenvector PDF Reweighting
DO_EIGENVECTOR_PDF_REWEIGHT=True
EIGENVECTOR_PDF_NAME= 'cteq66'

#Make Reco Histograms
def MakeRecoPDFReweightCategoryHistograms(inFileLoc="", outFileName="test.root"):

    # In File, Out File, and Tree
    inFile = TFile(inFileLoc)
    tree = inFile.Get(TREELOC)
    # New File
    outFile = TFile(OUTDIR + outFileName, "RECREATE")


    # Holder for PDF Pair Information
    xfx_pair_dict = GetPDFPairInfo(tree)

    # Loop over Events
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)
        
        #Unweighted
        if DO_UNWEIGHTED:
            MakeRecoHistograms_Unweighted(tree)
        
        # Caclulate Scale Factor Weights
        if DO_SCALEFACTOR:
            MakeRecoHistograms_ScaleFactor(tree)
        
        #Calculate Central PDF Reweight (includes scale factor)
        if DO_CENTRAL_PDF_REWEIGHT:
            MakeRecoHistograms_CentralPDFReweight(xfx_pair_dict, tree)

        # Calculate Eigenvector PDF Reweights (includes scale factor)
        if DO_EIGENVECTOR_PDF_REWEIGHT:
            MakeRecoHistograms_EigenvectorPDFReweight(xfx_pair_dict, tree)

            
    outFile.Write()

# Returns a dictionary, for each pdf set, with a link to the first and second parton
# distribution function, xfx, information from the root tree.
def GetPDFPairInfo(tree):
    xfx_pair_dict = {}
    for pdf_name in PDF_NAMES:
        print pdf_name
        xfx_pair_dict[pdf_name] = [vector('double')(), vector('double')()]
        tree.SetBranchAddress('xfx_first_'+pdf_name, xfx_pair_dict[pdf_name][0])
        tree.SetBranchAddress('xfx_second_'+pdf_name, xfx_pair_dict[pdf_name][1])
    return xfx_pair_dict

# Unweighted Histograms
def MakeRecoHistograms_Unweighted(tree):
    suffix = "unweighted"
    weight = 1
    MakeHistogramsByChannelType(tree, suffix, weight)

# Scale Factor Weighted Histograms
def MakeRecoHistograms_ScaleFactor(tree):
    suffix = "ScaleFactor"
    scalefactor = CalcScaleFactor(tree)
    MakeHistogramsByChannelType(tree, suffix, scalefactor)

# Makes the Reco Histograms for the Central PDF Reweightings. Uses the stored parton distribution
# functions to calculate the reweighting from the central value of the original pdf to the new pdf.
# Includes ScaleFactor
def MakeRecoHistograms_CentralPDFReweight(xfx_pair_dict, tree):
    scalefactor = CalcScaleFactor(tree)
    for pdf_name in PDF_NAMES:
        pdf_suffix = pdf_name+"_PDFReweight"
        pdf_reweight = calcPDFReweight(xfx_pair_dict, ORIG_PDF_NAME, pdf_name)
        suffix = "ScaleFactor_" + pdf_suffix
        weight = scalefactor * pdf_reweight
        MakeHistogramsByChannelType(tree, suffix, weight)

# Makes the Histograms for the Eigenvector PDF Reweightings. Uses the stord pdf info to calculate
# the reweighting from a PDF set's central value to one of it's eigenvector values.
#Includes ScaleFactor
def MakeRecoHistograms_EigenvectorPDFReweight(xfx_pair_dict, tree):
    scalefactor = CalcScaleFactor(tree)
    # Loop Over each Eigenvector element in the xfx vector.
    for eigenvector_index in range(0, xfx_pair_dict[EIGENVECTOR_PDF_NAME][0].size()):
        pdf_eigenvector_suffix = EIGENVECTOR_PDF_NAME+"_"+str(eigenvector_index)+"_PDFReweight"
        pdf_eigenvector_reweight = calcPDFEigenvectorReweight(xfx_pair_dict, EIGENVECTOR_PDF_NAME, eigenvector_index)
        suffix = "ScaleFactor_" + pdf_eigenvector_suffix
        weight = scalefactor * pdf_eigenvector_reweight
        MakeHistogramsByChannelType(tree, suffix, weight)

# Distinguish between the different Leptonic Signal Channels, and make Histograms
def MakeHistogramsByChannelType(tree, suffix, weight):
    scalefactor =1;
    # Identify whether the event is from the electron or muon channel

    if(IsElectronChannel(tree)):
        channel="ElectronChannel_"+suffix
        MakeHistograms(tree, channel, weight)
    if(IsMuonChannel(tree)):
        channel="MuonChannel_"+suffix
        MakeHistograms(tree, channel, weight)
# if(not IsElectronChannel(tree) and not IsMuonChannel(tree)):

def MakeHistograms(tree, channel, weight):
    histogramBuilder.fillCountHistograms(channel, weight)
    histogramBuilder.fillPtHistograms(channel, tree.pt_leadph12, weight)
    histogramBuilder.fillPtCategoryHistograms(channel, tree.pt_leadph12, weight)
# histogramBuilder.fillPhotonLocationCategoryHistograms(channel+"_weighted", findPhotonLocations(tree),weight)
#   histogramBuilder.fillPtAndLocationCategoryHistograms(channel+"_weighted", findPhotonLocations(tree),tree.pt_leadph12, weight)


#Identify whether the event is in the electron channel
def IsElectronChannel(tree):
    return (tree.el_passtrig_n> 0 and tree.el_n==1 and tree.mu_n==0)

# Identrify whether the event is in the muon channel
def IsMuonChannel(tree):
    return (tree.mu_passtrig25_n>0 and tree.mu_n==1 and tree.el_n==0)

#Caculate Scale Factor Weight, different whether it is the muon of electron channel.
def CalcScaleFactor(tree):
    
    scalefactor = 1
    
    if(IsElectronChannel(tree)):
        scalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.PUWeight
    
    if(IsMuonChannel(tree)):
        scalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
        
    return scalefactor



# Calculate PDF reweighting
def calcPDFReweight(xfx_pair_dict, orig_pdf_name, pdf_name):
    reweight =1;
    
    # Central Value is the 0 index in the vector
    orig_xfx_first = xfx_pair_dict[ orig_pdf_name][0]
    orig_xfx_second = xfx_pair_dict[ orig_pdf_name][1]
    orig_central_xfx_first = orig_xfx_first[0]
    orig_central_xfx_second = orig_xfx_second[0]
    
    new_xfx_first = xfx_pair_dict[pdf_name][0]
    new_xfx_second = xfx_pair_dict[pdf_name][1]
    new_central_xfx_first = new_xfx_first[0]
    new_central_xfx_second = new_xfx_second[0]
    
    reweight = (new_central_xfx_first * new_central_xfx_second) / (orig_central_xfx_first*orig_central_xfx_second)
    return reweight

#Calculate Reweighting from central value of a set, to up-down eigenvector values of the set.  
def calcPDFEigenvectorReweight(xfx_pair_dict, EIGENVECTOR_PDF_NAME, eigenvector_index):
    eigenvector_reweight =1;
    
    # Central Value is the 0 index in the vector
    xfx_first = xfx_pair_dict[EIGENVECTOR_PDF_NAME][0]
    xfx_second = xfx_pair_dict[EIGENVECTOR_PDF_NAME][1]
    central_xfx_first = xfx_first[0]
    central_xfx_second = xfx_second[0]
    
    eigenvector_xfx_first = xfx_first[eigenvector_index]
    eigenvector_xfx_second = xfx_second[eigenvector_index]
    
    eigenvector_reweight = (eigenvector_xfx_first * eigenvector_xfx_second) / (central_xfx_first*central_xfx_second)
    return eigenvector_reweight


#Separate Lead and Sub Lead Photons between Barrel and EndCap.
# 0 is EBEB, 1 EBEE, 2 EEEB, 3 is all others
def findPhotonLocations(tree):
    #Both in Barrel
    if(tree.isEB_leadph12 and tree.isEB_sublph12):
        return 0
    #Lead in Barrel Sub in EndCap
    if(tree.isEB_leadph12 and tree.isEE_sublph12):
        return 1
    #Lead in EndCap Sub in Barrel
    if(tree.isEE_leadph12 and tree.isEB_sublph12):
        return 2
    #Both in EndCap
    if(tree.isEE_leadph12 and tree.isEE_sublph12):
        return 3
    

if __name__=="__main__":
        MakeRecoPDFReweightCategoryHistograms(sys.argv[1], sys.argv[2])
    
