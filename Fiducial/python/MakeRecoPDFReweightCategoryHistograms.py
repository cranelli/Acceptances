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

#inFileDir="../test/"
treeLoc="EventTree"

outFileDir="../test/"

#PDF Reweighting
pdf_names=['cteq6l1', 'MSTW2008lo68cl', 'cteq66'] #cteq6l1 is the original
orig_pdf_name = pdf_names[0]

#Eigenvector PDF Reweighting
eigenvector_pdf_name=pdf_names[2]

def MakeRecoPDFReweightCategoryHistograms(inFileLoc="", outFileName="test.root"):

    # In File, Out File, and Tree
    inFile = TFile(inFileLoc)
    tree = inFile.Get(treeLoc)
    outFile = TFile(outFileDir + outFileName, "RECREATE")

    # Create a dictionairy (map) to store the addresses of the xfx pairs
    # for each PDF set.
    xfx_pair_dict = {}
    for pdf_name in pdf_names:
        print pdf_name
        xfx_pair_dict[pdf_name] = [vector('double')(), vector('double')()]
        tree.SetBranchAddress('xfx_first_'+pdf_name, xfx_pair_dict[pdf_name][0])
        tree.SetBranchAddress('xfx_second_'+pdf_name, xfx_pair_dict[pdf_name][1])

    # Loop over Events
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)


        
        #Calculate Weight Using Scale Factors and PDF Reweighting
        weight=1

        #Calculate PDF Reweight
        for pdf_name in pdf_names:
            pdf_reweight = calcPDFReweight(xfx_pair_dict, orig_pdf_name, pdf_name)

            scalefactor =1;
            
            isElectronChannel=(tree.el_passtrig_n> 0 and tree.el_n==1 and tree.mu_n==0)
            isMuonChannel=(tree.mu_passtrig25_n>0 and tree.mu_n==1 and tree.el_n==0)

            if(isElectronChannel):
                channel="ElectronChannel_"+pdf_name+"_PDFReweight"
                scalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.PUWeight
                weight = pdf_reweight*scalefactor
                MakeHistograms(tree, channel, weight)
            if(isMuonChannel):
                channel="MuonChannel_"+pdf_name+"_PDFReweight"
                scalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
                weight =pdf_reweight*scalefactor
                MakeHistograms(tree, channel, weight)
            # if(not isElectronChannel and not isMuonChannel):

        # Calculate Eigenvector PDF Reweight
        # Loop Over each Eigenvector element in the xfx vector.
        for eigenvector_index in range(0, xfx_pair_dict[eigenvector_pdf_name][0].size()):
            eigenvector_reweight = calcPDFEigenvectorReweight(xfx_pair_dict, eigenvector_pdf_name, eigenvector_index)
            if(isElectronChannel):
                channel="ElectronChannel_"+eigenvector_pdf_name+"_"+str(eigenvector_index)+"_PDFReweight"
                scalefactor = tree.el_trigSF*tree.ph_idSF*tree.ph_evetoSF*tree.PUWeight
                weight = eigenvector_reweight*scalefactor
                MakeHistograms(tree, channel, weight)
            if(isMuonChannel):
                channel="MuonChannel_"+eigenvector_pdf_name+"_"+str(eigenvector_index)+"_PDFReweight"
                scalefactor = tree.mu_trigSF*tree.mu_isoSF*tree.mu_idSF*tree.ph_idSF*tree.PUWeight
                weight =eigenvector_reweight*scalefactor
                MakeHistograms(tree, channel, weight)
            
    outFile.Write()

def MakeHistograms(tree, channel, weight):
    
    histogramBuilder.fillCountHistograms(channel+"_unweighted")
    histogramBuilder.fillCountHistograms(channel+"_weighted", weight)
    #histogramBuilder.fillScaleFactorHistograms("ScaleFactors_"+channel, weight)
    histogramBuilder.fillPtHistograms(channel+"_weighted", tree.pt_leadph12, weight)
    histogramBuilder.fillPtCategoryHistograms(channel+"_weighted", tree.pt_leadph12, weight)
    #histogramBuilder.fillPhotonLocationCategoryHistograms(channel+"_ScaleFactorWeight", findPhotonLocations(tree),weight)
    #histogramBuilder.fillPtAndLocationCategoryHistograms(channel+"_ScaleFactorWeight", findPhotonLocations(tree),
    #                                                     tree.pt_leadph12, weight)
    #histogramBuilder.fillPtAndLocationCategoryHistograms(channel, findPhotonLocations(tree),
     #                                                    tree.pt_leadph12)


# Calculate PDF reweighting
def calcPDFReweight(xfx_pair_dict, orig_pdf_name, pdf_name):
    reweight =1;
    
    # Central Value is the 0 index in the vector
    orig_xfx_first = xfx_pair_dict[orig_pdf_name][0]
    orig_xfx_second = xfx_pair_dict[orig_pdf_name][1]
    orig_central_xfx_first = orig_xfx_first[0]
    orig_central_xfx_second = orig_xfx_second[0]
    
    new_xfx_first = xfx_pair_dict[pdf_name][0]
    new_xfx_second = xfx_pair_dict[pdf_name][1]
    new_central_xfx_first = new_xfx_first[0]
    new_central_xfx_second = new_xfx_second[0]
    
    reweight = (new_central_xfx_first * new_central_xfx_second) / (orig_central_xfx_first*orig_central_xfx_second)
    return reweight

#Calculate Reweighting from central value of a set, to up-down eigenvector values of the set.  
def calcPDFEigenvectorReweight(xfx_pair_dict, eigenvector_pdf_name, eigenvector_index):
    eigenvector_reweight =1;
    
    # Central Value is the 0 index in the vector
    xfx_first = xfx_pair_dict[eigenvector_pdf_name][0]
    xfx_second = xfx_pair_dict[eigenvector_pdf_name][1]
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
    
