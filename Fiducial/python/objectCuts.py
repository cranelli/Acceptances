"""Selection Cuts - Makes Selection Cuts for LNuAA Analysis"""

# Python Module For Selection Cuts
# Created by Christopher Anelli, 8.4.2014
# Tested in Python 2.6.4

from ROOT import TLorentzVector
from ROOT import TH1F, TH2F

#import FiducialCutValues
import CommonFiducialCutValues
#import histogramBuilder

# Selection Cut Values
# Photons
#minPhotonPt = CommonFiducialCutValues.PHOTON_CANDIDATE_MIN_PT
#maxPhotonEta = CommonFiducialCutValues.PHOTON_CANDIDATE_MAX_ETA
#minPhotonEndCapEta = FiducialCutValues.PHOTONGAP_MIN_ETA
#maxPhotonEndCapEta = FiducialCutValues.PHOTONGAP_MAX_ETA
# Electrons
#minElectronPt = CommonFiducialCutValues.ELECTRON_CANDIDATE_MIN_PT
#maxElectronEta = CommonFiducialCutValues.ELECTRON_CANDIDATE_MAX_ETA
# Muons
#minMuonPt = CommonFiducialCutValues.MUON_CANDIDATE_MIN_PT
#maxMuonEta = CommonFiducialCutValues.MUON_CANDIDATE_MAX_ETA

# Require it to be final state

def selectOnStatus(particles, status=1):
    particles = filter(lambda particles: particles.Status()==status, particles)
    return particles

#Kinematic Cuts

def selectOnPtEta(particles, minPt, maxEta):
    particles = filter(lambda particle: particle.Pt() > minPt, particles)
    particles = filter(lambda particle: abs(particle.Eta()) < maxEta, particles)
    return particles

def selectOnDetectorGap(particles):
    particles = filter(lambda particle: abs(particle.Eta()) < minPhotonEndCapEta
                     or abs(particle.Eta()) > maxPhotonEndCapEta, particles)
    return particles

#def selectOnPhotonKinematics(photons):
    #if photons != None:
    # Post Cut Histograms
#    photons = filter(lambda photon: photon.Pt() > minPhotonPt, photons)
    #histogramBuilder.fillPtHistograms(photons, 'Photon_Pt_PostPhotonPtCut')
#    photons = filter(lambda photon: abs(photon.Eta()) < maxPhotonEta, photons)
    #histogramBuilder.fillEtaHistograms(photons, 'Photon_Eta_PostPhotonEtaCut')
#    return photons

#def selectOnElectronKinematics(electrons):
    #if electrons != None:
#    electrons = filter(lambda electron: electron.Pt() > minElectronPt, electrons)
    #histogramBuilder.fillPtHistograms(electrons, 'Electron_Pt_PostElectronPtCut')
#    electrons = filter(lambda electron: abs(electron.Eta()) < maxElectronEta, electrons)
    #histogramBuilder.fillEtaHistograms(electrons, 'Electron_Eta_PostElectronEtaCut')
#    return electrons

#def selectOnMuonKinematics(muons):
#    muons = filter(lambda muon: muon.Pt() > minMuonPt, muons)
    #histogramBuilder.fillPtHistograms(muons, 'Muon_Pt_PostMuonPtCut')
#    muons = filter(lambda muon: abs(muon.Eta()) < maxMuonEta, muons)
    #histogramBuilder.fillEtaHistograms(muons, 'Muon_Eta_PostMuonEtaCut')
#    return muons
