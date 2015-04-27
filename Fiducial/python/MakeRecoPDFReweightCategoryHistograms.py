# Python Code for Histograming events based on their
# RECO values.  Splits signal events between the different
# channels and our different categories.
# 
# Example execution from command line:
# python MakeRecoPDFReweightCategoryHistograms.py /data/users/cranelli/WGamGam/Acceptances/AnalysisRECOCuts_Skim/LepGammaGammaFinalEl_2015_03_31_ScaleFactors_PDFReweights/job_summer12_WAA_ISR/tree.root test.root
#

import sys

from collections import namedtuple

from ROOT import TFile
from ROOT import TTree
from ROOT import vector

from ctypes import c_float


import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histogramBuilder


###################################

# Define Global Variables

TREELOC="EventTree"
OUTDIR="../test/Histograms/"

# Unweighted Histograms
DO_UNWEIGHTED=True

# With Scale Factor Weight
DO_SCALEFACTORS_UPDN = True
ELECTRON_CHANNEL_SCALEFACTORS=['el_trigSF', 'ph_idSF', 'ph_evetoSF']
MUON_CHANNEL_SCALEFACTORS=['mu_trigSF', 'mu_isoSF', 'mu_idSF', 'ph_idSF']
ScaleFactorOrigUpDnStruct = namedtuple ('ScaleFactorOrigUpDn', 'orig up down')


#Central PDF Reweighting
DO_CENTRAL_PDF_REWEIGHT=True
PDF_NAMES=['cteq6l1', 'MSTW2008lo68cl', 'cteq66'] #cteq6l1 is the original
ORIG_PDF_NAME = 'cteq6l1'
PDFPairStruct = namedtuple ('PDFPairStruct', 'first second')

#Eigenvector PDF Reweighting
DO_EIGENVECTOR_PDF_REWEIGHT=True
EIGENVECTOR_PDF_NAME= 'cteq66'


#####################################



#Make Reco Histograms
def MakeRecoPDFReweightCategoryHistograms(inFileLoc="", outFileName="test.root"):

    # In File, Out File, and Tree
    inFile = TFile(inFileLoc)
    tree = inFile.Get(TREELOC)
    # New File
    outFile = TFile(OUTDIR + outFileName, "RECREATE")
    
    #Holder for ScaleFactor UP DN Information
    if DO_SCALEFACTORS_UPDN:
        scalefactor_up_dn_dict = GetScaleFactorUPDNInfo(tree)
    
    # Holder for PDF Pair Information
    if DO_CENTRAL_PDF_REWEIGHT or DO_EIGENVECTOR_PDF_REWEIGHT :
        xfx_pair_dict = GetPDFPairInfo(tree)

    # Loop over Events
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)
        
        MakeBasicRecoHistograms(tree)
        
        #Unweighted
        if DO_UNWEIGHTED:
            MakeRecoHistograms_Unweighted(tree)
        
        # Caclulate UP DN Scale Factors
        if DO_SCALEFACTORS_UPDN:
            MakeRecoHistograms_ScaleFactorsUPDN(scalefactor_up_dn_dict, tree)
        
        #Calculate Central PDF Reweight (includes scale factor)
        if DO_CENTRAL_PDF_REWEIGHT:
            MakeRecoHistograms_CentralPDFReweight(xfx_pair_dict, tree)

        # Calculate Eigenvector PDF Reweights (includes scale factor)
        if DO_EIGENVECTOR_PDF_REWEIGHT:
            MakeRecoHistograms_EigenvectorPDFReweight(xfx_pair_dict, tree)
            

    outFile.Write()

# Returns a dictionary, for each scalefactor, with a link to it's original value,
# 1 sigma UP, and 1 sigma down.

def GetScaleFactorUPDNInfo(tree):
    scalefactor_up_dn_dict = {}
    scalefactor_names = set(ELECTRON_CHANNEL_SCALEFACTORS + MUON_CHANNEL_SCALEFACTORS) # Remove Duplicates
    for scalefactor_name in scalefactor_names:
        print scalefactor_name
        scalefactor_up_dn_dict[scalefactor_name]=ScaleFactorOrigUpDnStruct(c_float(),c_float(),c_float())
        tree.SetBranchAddress(scalefactor_name,scalefactor_up_dn_dict[scalefactor_name].orig)
        tree.SetBranchAddress(scalefactor_name+'UP',scalefactor_up_dn_dict[scalefactor_name].up)
        tree.SetBranchAddress(scalefactor_name+'DN',scalefactor_up_dn_dict[scalefactor_name].down)
    return scalefactor_up_dn_dict


# Returns a dictionary, for each pdf set, with a link to the first and second parton
# distribution function, xfx, information from the root tree.
def GetPDFPairInfo(tree):
    xfx_pair_dict = {}
    for pdf_name in PDF_NAMES:
        print pdf_name
        xfx_pair_dict[pdf_name] = PDFPairStruct(vector('double')(), vector('double')())
        tree.SetBranchAddress('xfx_first_'+pdf_name, xfx_pair_dict[pdf_name][0])
        tree.SetBranchAddress('xfx_second_'+pdf_name, xfx_pair_dict[pdf_name][1])
    return xfx_pair_dict


# Unweighted Histograms
def MakeRecoHistograms_Unweighted(tree):
    suffix = "unweighted"
    weight = 1
    MakeHistogramsByChannelType(tree, suffix, weight)


# Scale Factor Weighted Histograms
def MakeBasicRecoHistograms(tree):
    suffix = "ScaleFactor"
    scalefactor = CalcScaleFactor(tree)
    MakeHistogramsByChannelType(tree, suffix, scalefactor)


#  Scale Factor values varied 1 Sigma UP or 1 Sigma DN.
def MakeRecoHistograms_ScaleFactorsUPDN(scalefactor_up_dn_dict, tree):
    directions = ['UP', 'DN']
    
    for dir in directions:
        if IsElectronChannel(tree):
            for scalefactor_name in ELECTRON_CHANNEL_SCALEFACTORS:
                ReweightScaleFactorAndMakeHistograms(scalefactor_up_dn_dict, scalefactor_name, dir, tree)
        
        if IsMuonChannel(tree):
            for scalefactor_name in MUON_CHANNEL_SCALEFACTORS:
                ReweightScaleFactorAndMakeHistograms(scalefactor_up_dn_dict, scalefactor_name, dir, tree)

# Makes new
def ReweightScaleFactorAndMakeHistograms(scalefactor_up_dn_dict, scalefactor_name, dir, tree):
    scalefactor=CalcScaleFactor(tree)
    scalefactor_updn_suffix = "ScaleFactor_"+scalefactor_name+dir
    scalefactor_reweight = CalcScaleFactorReweight(scalefactor_up_dn_dict, scalefactor_name, dir, tree)
    weight = scalefactor*scalefactor_reweight
    MakeHistogramsByChannelType(tree, scalefactor_updn_suffix, weight)



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
        pdf_eigenvector_suffix = EIGENVECTOR_PDF_NAME+"_"+str(eigenvector_index)+"_PDFEigenvectorReweight"
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

# Given the scale factor name, returns a reweighting value to move it
# 1 sigma in the dir specified (UP DN).
# The scalefactor_up_dn dictionairy holds the original, up, and down value
# as c float types, so .value must be called to get/use their value.
def CalcScaleFactorReweight(scalefactor_up_dn_dict, scalefactor_name, dir, tree):
    orig_scalefactor = scalefactor_up_dn_dict[scalefactor_name].orig.value

    if dir == 'UP':
        new_scalefactor = scalefactor_up_dn_dict[scalefactor_name].up.value
    if dir == 'DN':
        new_scalefactor = scalefactor_up_dn_dict[scalefactor_name].down.value

    reweight =new_scalefactor/orig_scalefactor
    return reweight

# Calculate Central PDF reweighting
def calcPDFReweight(xfx_pair_dict, orig_pdf_name, pdf_name):
    reweight =1;
    
    # Central Value is the 0 index in the vector
    central_index = 0
    orig_xfx_first = xfx_pair_dict[ orig_pdf_name].first
    orig_xfx_second = xfx_pair_dict[ orig_pdf_name].second
    orig_central_xfx_first = orig_xfx_first[central_index]
    orig_central_xfx_second = orig_xfx_second[central_index]
    
    new_xfx_first = xfx_pair_dict[pdf_name].first
    new_xfx_second = xfx_pair_dict[pdf_name].second
    new_central_xfx_first = new_xfx_first[central_index]
    new_central_xfx_second = new_xfx_second[central_index]
    
    reweight = (new_central_xfx_first * new_central_xfx_second) / (orig_central_xfx_first*orig_central_xfx_second)
    return reweight

#Calculate Reweighting from central value of a set, to up-down eigenvector values of the set.  
def calcPDFEigenvectorReweight(xfx_pair_dict, EIGENVECTOR_PDF_NAME, eigenvector_index):
    eigenvector_reweight =1;
    central_index=0
    # Central Value is the 0 index in the vector
    xfx_first = xfx_pair_dict[EIGENVECTOR_PDF_NAME].first
    xfx_second = xfx_pair_dict[EIGENVECTOR_PDF_NAME].second
    central_xfx_first = xfx_first[central_index]
    central_xfx_second = xfx_second[central_index]
    
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
    
