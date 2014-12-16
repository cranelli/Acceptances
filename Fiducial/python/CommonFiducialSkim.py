from ROOT import TFile
from ROOT import TTree

import particleIdentification
import objectCuts
import eventCuts
import parentCuts

import histPublish


origFileLoc="/data/users/cranelli/WGamGam/ggNtuples/job_summer12_LNuGG_FSR.root"
origTreeLoc="ggNtuplizer/EventTree"

newFileLoc="CommonFiducialEvents_FSR.root"

histDirLoc = 'histOutput/'
acceptanceTableFileName = "FSR"

def CommonFiducialSkim():
    # Original File
    origFile = TFile(origFileLoc)
    origTree = origFile.Get(origTreeLoc)
    # New File
    skimFile = TFile(newFileLoc, "RECREATE")
    skimTree = origTree.CloneTree(0)
    
    nentries = origTree.GetEntries()
    print "Number of Entries", nentries

    for i in range(0, nentries):
        if(i%1000==0): print i
        origTree.GetEntry(i)
        
        keepEvent = False
        
        #Assign Particles
        photons = []
        electrons = []
        muons =[]
        nu_es =[]
        nu_ms =[]
        ws = []

        # Particle Identification Step
        particleIdentification.assignParticles(
            origTree, photons, electrons, muons, nu_es, nu_ms, ws)
        
        #Status Cuts, Select Final State
        photons = objectCuts.selectOnStatus(photons)
        electrons = objectCuts.selectOnStatus(electrons)
        muons = objectCuts.selectOnStatus(muons)
        
        #Kinematic Selection Cuts
        photons = objectCuts.selectOnPhotonKinematics(photons)
        electrons = objectCuts.selectOnElectronKinematics(electrons)
        muons = objectCuts.selectOnMuonKinematics(muons)

        #Parent Cuts
        photons = parentCuts.selectOnPhotonParentage(photons)
        electrons= parentCuts.selectOnElectronParent(electrons)
        muons=parentCuts.selectOnMuonParent(muons)

        if not eventCuts.passReqNumParticles(photons, electrons, muons): continue

        #Photon Photon Delta R Cuts
        if not eventCuts.passPhotonPhotonDeltaR(photons): continue

        # Electron Channel
        if len(electrons) == 1:
            # Electron Photon Delta R Cut
            if not eventCuts.passPhotonElectronDeltaR(photons, electrons): continue

        if len(muons) == 1:
            if not eventCuts.passPhotonMuonDeltaR(photons, muons): continue

        # You have reached the end, congratulations!
        keepEvent=True
        if(keepEvent): skimTree.Fill();

    skimTree.Print()
    skimFile.Write()

        
if __name__=="__main__":
        CommonFiducialSkim()
    
