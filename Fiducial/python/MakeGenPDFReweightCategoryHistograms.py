# Python Code for making Histograms
# from the Common Fiducial Skim
# Example execution from command line:


import sys

from ROOT import TFile
from ROOT import TTree
from ROOT import vector

import CommonFiducialCutValues
import particleIdentification
import objectCuts
import parentCuts

import histogramBuilder

#origFileDir="/data/users/cranelli/WGamGam/Acceptances/CommonFiducial_Skim/ggNtuples_Skim/"
treeLoc="EventTree"

outFileDir="../test/"

#PDF Reweighting
pdf_names=['cteq6l1', 'MSTW2008lo68cl', 'cteq66'] #cteq6l1 is the original
orig_pdf_name = pdf_names[0]

# PdgIds
electronPdgId = 11
muonPdgId = 13
tauPdgId = 15
photonPdgId = 22
wPdgId = 24
# Statuses
finalStateStatus=1
hardScatterStatus=3
#Object Cut Values
minPhotonPt = CommonFiducialCutValues.PHOTON_CANDIDATE_MIN_PT
maxPhotonEta = CommonFiducialCutValues.PHOTON_CANDIDATE_MAX_ETA

def MakeGenPDFReweightCategoryHistograms(inFileLoc="job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root",
                                         outFileName="test.root"):
    # Original File
    origFile = TFile(inFileLoc)
    tree = origFile.Get(treeLoc)
    # New File
    outFile = TFile(outFileDir + outFileName, "RECREATE")
    
    nentries = tree.GetEntries()
    print "Number of Entries", nentries


    # Create a dictionairy (map) to store the addresses of the xfx pairs
    # for each PDF set.
    xfx_pair_dict = {}
    for pdf_name in pdf_names:
        print pdf_name
        xfx_pair_dict[pdf_name] = [vector('double')(), vector('double')()]
        tree.SetBranchAddress('xfx_first_'+pdf_name, xfx_pair_dict[pdf_name][0])
        tree.SetBranchAddress('xfx_second_'+pdf_name, xfx_pair_dict[pdf_name][1])
        
    # Loop Over Events
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)

        # Select Particles with a W Parent
        wChildren = []
        particleIdentification.assignParticleByParentID(tree, wChildren, wPdgId)
                                                        
        # Select and Make Object Cuts on Photons
        photons = []
        particleIdentification.assignParticleByID(tree, photons, photonPdgId)
        photons= objectCuts.selectOnStatus(photons, 1)
        photons=objectCuts.selectOnPtEta(photons, minPhotonPt, maxPhotonEta)
        photons=parentCuts.selectOnPhotonParentage(photons)

        #Calculate PDF Reweight
        for pdf_name in pdf_names:
            reweight = calcPDFReweight(xfx_pair_dict, orig_pdf_name, pdf_name)
        
            # Select Decay Type
            for wChild in wChildren: 
            
                # Electron Decay
                if(abs(wChild.PID()) == electronPdgId and wChild.Status() == finalStateStatus):
                    decay="ElectronDecay_" + pdf_name+"_PDFReweight"
                    MakeHistograms(tree, decay, photons, reweight)
                if(abs(wChild.PID()) == muonPdgId and wChild.Status() == finalStateStatus):
                    decay="MuonDecay_"+ pdf_name + "_PDFReweight"
                    MakeHistograms(tree, decay, photons, reweight)
                if(abs(wChild.PID()) == tauPdgId and wChild.Status() == hardScatterStatus):
                    decay="TauDecay_"+ pdf_name + "_PDFReweight"
                    MakeHistograms(tree, decay, photons, reweight)
           
    outFile.Write()

def MakeHistograms(tree, decay, photons, reweight):
    histogramBuilder.fillCountHistograms(decay)
    leadPhoton = selectLead(photons)
    histogramBuilder.fillPtHistograms(decay, leadPhoton.Pt(), reweight)
    histogramBuilder.fillPtCategoryHistograms(decay, leadPhoton.Pt(), reweight)
    #histogramBuilder.fillPhotonLocationCategoryHistograms(decay, findPhotonLocations(photons), reweight)
    #histogramBuilder.fillPtAndLocationCategoryHistograms(decay, findPhotonLocations(photons), leadPhoton.Pt(), reweight)

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

#Select Lead Particle by Pt
def selectLead(particles):
    #print "Start"
    maxPt = 0
    lead = None
    for particle in particles:
        #print particle.Pt()
        if particle.Pt() > maxPt :
            maxPt = particle.Pt()
            lead =  particle
    #print "Max:", lead.Pt()
    return lead

# Select Sub Lead Particle by Pt
def selectSubLead(particles):
    maxPt = 0
    subLeadPt = 0
    lead = None
    subLead = None
    for particle in particles:
        if particle.Pt() > maxPt:
            subLeadPt = maxPt
            subLead = lead
            maxPt = particle.Pt()
            lead = particle
        elif particle.Pt() > subLeadPt:
            subLeadPt = particle.Pt()
            subLead = particle
            
    return subLead

#Separate Lead and Sub Lead Photons between Barrel and EndCap.
def findPhotonLocations(photons):

    photonLead = selectLead(photons)
    photonSubLead = selectSubLead(photons)
    barrelMaxEta=1.44
    endCapMinEta=1.57
    
    #Both in Barrel
    if abs(photonLead.Eta()) < barrelMaxEta and abs(photonSubLead.Eta()) < barrelMaxEta:
        return 0
    #Lead in Barrel Sub in EndCap
    if abs(photonLead.Eta()) < barrelMaxEta and abs(photonSubLead.Eta()) > endCapMinEta:
        return 1
    #Lead in EndCap Sub in Barrel
    if abs(photonLead.Eta()) >endCapMinEta and abs(photonSubLead.Eta()) < barrelMaxEta:
        return 2
   
    #if(tree.isEE_leadph12 and tree.isEE_sublph12):
    return 3

if __name__=="__main__":
        MakeGenPDFReweightCategoryHistograms(sys.argv[1], sys.argv[2])
    
