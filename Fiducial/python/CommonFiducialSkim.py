#This code skims the LNuAA ntuples, and leaves only events that pass
#our Common Fiducial Cuts.
#The values of these cuts are defined in CommonFiducialCutValues.
#Is passed arguments for startRange, stopRange, inFile, outFile
#Example Call
# python CommonFiducialSkim.py 0 10000 ggNtuples/ggtree_mc_ISR.root test.root

import sys

from ROOT import TFile
from ROOT import TTree

import CommonFiducialCutValues

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

#import histPublish
import histogramBuilder

origFileDir="/data/users/cranelli/WGamGam/"
origTreeLoc="ggNtuplizer/EventTree"
skimFileDir="../test/"

#Set Cut Values
minPhotonPt = CommonFiducialCutValues.PHOTON_CANDIDATE_MIN_PT
maxPhotonEta = CommonFiducialCutValues.PHOTON_CANDIDATE_MAX_ETA
minLeptonPt = CommonFiducialCutValues.LEPTON_CANDIDATE_MIN_PT
maxLeptonEta = CommonFiducialCutValues.LEPTON_CANDIDATE_MAX_ETA
reqNumPhotons = CommonFiducialCutValues.NUM_CANDIDATE_PHOTONS
reqNumLeptons = CommonFiducialCutValues.NUM_CANDIDATE_LEPTONS
minPhotonPhotonDeltaR = CommonFiducialCutValues.PHOTON_PHOTON_DR
minPhotonLeptonDeltaR = CommonFiducialCutValues.PHOTON_LEPTON_DR 


def CommonFiducialSkim(startRange=0, endRange=-1, inFileName="ggNtuples/job_summer12_LNuGG_FSR.root",
                       outFileName="test.root"):
    # Original File
    origFile = TFile(origFileDir+inFileName)
    origTree = origFile.Get(origTreeLoc)
    # New File
    skimFile = TFile(skimFileDir+outFileName, "RECREATE")
    skimTreeDirectory = skimFile.mkdir("ggNtuplizer")
    skimTreeDirectory.cd()
    skimTree = origTree.CloneTree(0)
    
    nentries = origTree.GetEntries()
    print "Number of Entries", nentries

    if endRange== -1: endRange=nentries
    for i in range(startRange, endRange):
        if(i%1000==0): print i
        origTree.GetEntry(i)
        
        keepEvent = False
        
        #Assign Particles
        photons = []
        electrons = []
        muons =[]
        taus =[]
        nu_es =[]
        nu_ms =[]
        nu_ts=[]
        ws = []

        # Particle Identification Step
        particleIdentification.assignParticles(origTree, photons, electrons, muons, taus,
                                               nu_es, nu_ms, nu_ts, ws)
        
        #Status Cuts
        #Select Final State Particles
        photons = objectCuts.selectOnStatus(photons, 1)
        electrons = objectCuts.selectOnStatus(electrons, 1)
        muons = objectCuts.selectOnStatus(muons,1)
        #For Taus Select on Hard Scatter:
        taus = objectCuts.selectOnStatus(taus,3)
        
        #Kinematic Selection Cuts
        photons = objectCuts.selectOnPtEta(photons, minPhotonPt, maxPhotonEta)
        electrons = objectCuts.selectOnPtEta(electrons, minLeptonPt, maxLeptonEta)
        muons = objectCuts.selectOnPtEta(muons, minLeptonPt, maxLeptonEta)
        #taus = objectCuts.selectOnPtEta(taus, minLeptonPt, maxLeptonEta)

        #Parent Cuts
        photons = parentCuts.selectOnPhotonParentage(photons)
        w_electrons= parentCuts.selectOnParentID(electrons, 24)
        w_muons=parentCuts.selectOnParentID(muons, 24)
        tau_electrons= parentCuts.selectOnParentID(electrons, 15)
        tau_muons=parentCuts.selectOnParentID(muons, 15)
        #if len(tau_muons) > 0: print "working"
        taus=parentCuts.selectOnParentID(taus, 24)
        electrons=w_electrons+tau_electrons
        muons=w_muons+tau_muons
        leptons=electrons+muons

        if not eventCuts.passReqNumParticles(photons, electrons, muons,
                                             reqNumPhotons, reqNumLeptons): continue

        #Photon Photon Delta R Cuts
        if not eventCuts.passPhotonPhotonDeltaR(photons, minPhotonPhotonDeltaR): continue
        if not eventCuts.passPhotonLeptonDeltaR(photons, leptons, minPhotonLeptonDeltaR): continue


        # You have reached the end of the Cuts, congratulations!
        keepEvent=True
        if(keepEvent): skimTree.Fill();

        
        # Make Histograms, Separated by Decay Type 

        # Electron Decay
        if len(w_electrons) == reqNumLeptons:
            # Electron Photon Delta R Cut
            prefix="CommonFiducial_WDecayToElectron"
            MakeCommonFiducialCheckHistograms(prefix, photons, electrons, muons)
            
        # Muon Decay
        if len(w_muons) == reqNumLeptons:
            prefix="CommonFiducial_WDecayToMuon"
            MakeCommonFiducialCheckHistograms(prefix, photons, electrons, muons)

        # Tau Decay
        if len(taus) == reqNumLeptons:
            # Tau to e
            if len(tau_electrons) == reqNumLeptons:
                prefix = "CommonFiducial_WDecayToTauToElectron"
                MakeCommonFiducialCheckHistograms(prefix, photons, electrons, muons)
            # Tau to mu
            if len(tau_muons) == reqNumLeptons:
                prefix = "CommonFiducial_WDecayToTauToMuon"
                MakeCommonFiducialCheckHistograms(prefix, photons, electrons, muons)
        

    #skimTree.Print()
    skimFile.Write()



# Make Histograms to check that the passing events are with the Common Fiducial Region.
def MakeCommonFiducialCheckHistograms(prefix, photons, electrons, muons):
    # Counts
    histogramBuilder.fillCountHistograms(prefix)

    # Particle Type Histograms
    MakeParticleTypeHistograms(prefix, photons, "Photons")
    MakeParticleTypeHistograms(prefix, electrons, "Electrons")
    MakeParticleTypeHistograms(prefix, muons, "Muons")

    #dR Histograms
    MakeDeltaRHistograms(prefix, photons, photons, "Photons", "Photons")
    MakeDeltaRHistograms(prefix, photons, electrons, "Photons", "Electrons")
    MakeDeltaRHistograms(prefix, photons, muons, "Photons", "Muons")    
    
# Make histograms of the Multiplicity, Pt, Eta ...
# of all particles of a given type.
def MakeParticleTypeHistograms(prefix, particles, particleType):
    histogramBuilder.fillMultiplicityHistograms(prefix+"_"+particleType, len(particles))

    for particle in particles:
        histogramBuilder.fillPtHistograms(prefix+"_"+particleType,particle.Pt())
        histogramBuilder.fillEtaHistograms(prefix+"_"+particleType, particle.Eta())
        histogramBuilder.fillStatusHistograms(prefix+"_" + particleType, particle.Status())
        histogramBuilder.fillPDGIDHistograms(prefix+"_"+particleType, particle.PID())
        histogramBuilder.fillPDGIDHistograms(prefix+"_"+particleType+"Mother", particle.MomPID())

def MakeDeltaRHistograms(prefix, particles1, particles2, particleType1, particleType2):
    prefix+="_"+particleType1 +"_"+ particleType2
    for particle1 in particles1:
        for particle2 in particles2:
            if particle1 != particle2:
                histogramBuilder.fillDeltaRHistograms(prefix, particle1.DeltaR(particle2))
                

    
        
if __name__=="__main__":
        CommonFiducialSkim(int(sys.argv[1]),int(sys.argv[2]), sys.argv[3], sys.argv[4])
    
