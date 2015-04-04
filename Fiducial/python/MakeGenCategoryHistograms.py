# Python Code for making Histograms
# from the Common Fiducial Skim
# Example execution from command line:
# python MakeGenCategoryHistograms.py /data/users/cranelli/WGamGam/Acceptances/CommonFiducial_Skim/ggNtuples_Skim/job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root CommonFiducialSkim_WAA_ISR_CategoryHistograms.root

import sys

from ROOT import TFile
from ROOT import TTree

import CommonFiducialCutValues
import particleIdentification
import objectCuts
import parentCuts

import histogramBuilder

#origFileDir="/data/users/cranelli/WGamGam/Acceptances/CommonFiducial_Skim/ggNtuples_Skim/"
treeLoc="ggNtuplizer/EventTree"

outFileDir="../test/"
#newFileLoc="ggtree_ISR_Tau.root"

#histDirLoc = 'histOutput/'


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

def MakeGenCategoryHistograms(inFileLoc="job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root",
                               outFileName="test.root"):
    # Original File
    origFile = TFile(inFileLoc)
    tree = origFile.Get(treeLoc)
    # New File
    outFile = TFile(outFileDir + outFileName, "RECREATE")
    
    nentries = tree.GetEntries()
    print "Number of Entries", nentries
    
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

        # Select Decay Type
        for wChild in wChildren:

            # Electron Decay
            if(abs(wChild.PID()) == electronPdgId and wChild.Status() == finalStateStatus):
                decay="ElectronDecay"
                MakeHistograms(tree, decay, photons)
            if(abs(wChild.PID()) == muonPdgId and wChild.Status() == finalStateStatus):
                decay="MuonDecay"
                MakeHistograms(tree, decay, photons)
            if(abs(wChild.PID()) == tauPdgId and wChild.Status() == hardScatterStatus):
                decay="TauDecay"
                MakeHistograms(tree, decay, photons)
           
    outFile.Write()

def MakeHistograms(tree, decay, photons):
    histogramBuilder.fillCountHistograms(decay)
    leadPhoton = selectLead(photons)
    histogramBuilder.fillPtHistograms(decay, leadPhoton.Pt())
    histogramBuilder.fillPtCategoryHistograms(decay, leadPhoton.Pt())
    histogramBuilder.fillPhotonLocationCategoryHistograms(decay, findPhotonLocations(photons))
    histogramBuilder.fillPtAndLocationCategoryHistograms(decay, findPhotonLocations(photons), leadPhoton.Pt())
    

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

if __name__=="__main__":
        MakeGenCategoryHistograms(sys.argv[1], sys.argv[2])
    
