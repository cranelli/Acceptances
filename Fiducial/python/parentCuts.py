"""Parent Cuts - Makes Parentage Selection Cuts for LNuAA Analysis"""

# Python Module For Parentage Cuts
# Created by Nicholas Zube, 8.22.2014
# Tested in Python 2.6.4

from ROOT import TLorentzVector
#from ROOT import TH1F, TH2F

#import histogramBuilder

#MC Parentage Masks
qcd_parent_mask = 2 #Binary Representation
non_prompt_mask = 4
boson_parent_mask = 8
lep_parent_mask = 16

# Uses mcParentage, chooses not Non-Prompt
def selectOnPhotonParentage(photons):
    filter_photons = filter(lambda photon:(photon.McParentage() & non_prompt_mask) != non_prompt_mask, photons)
    return filter_photons

def selectOnPhotonParent(photons):
    #if photons != None:
    filter_photons = filter(lambda photon: abs(photon.MomPID()) < 25, photons)
    #histogramBuilder.fillPtHistograms(filter_photons, 'Photon_Pt_PostParentCut')
    #histogramBuilder.fillEtaHistograms(filter_photons, 'Photon_Eta_PostParentCut')
    return filter_photons

def selectOnParentID(particles, parentID):
    #if particles != None:
    particles = filter(lambda particle: abs(particle.MomPID()) == parentID,
                       particles)
    return particles                  
    
#def selectOnElectronParent(electrons):
    #if electrons != None:
    #electrons = filter(lambda electron: abs(electron.MomPID()) == 24
                       #or abs(electron.MomPID()) ==15
    #                   , electrons)
    #histogramBuilder.fillPtHistograms(electrons, 'Electron_Pt_PostWParentCut')
    #histogramBuilder.fillEtaHistograms(electrons, 'Electron_Eta_PostWParentCut')
    #return electrons

#def selectOnMuonParent(muons):
    #if muons != None:
    #muons = filter(lambda muon: abs(muon.MomPID()) == 24
                   #or abs(muon.MomPID()==15)
    #               , muons)
    #histogramBuilder.fillPtHistograms(muons, 'Muon_Pt_PostWParentCut')
    #histogramBuilder.fillEtaHistograms(muons, 'Muon_Eta_PostWParentCut')
    #return muons
