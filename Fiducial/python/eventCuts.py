"""Event Cuts - Makes Event Cuts for LNuAA Analysis"""

# Python Module For Event Cuts
# Created by Christopher Anelli, 8.4.2014
# Tested in Python 2.6.4

from ROOT import TLorentzVector

import CommonFiducialCutValues
from math import sqrt, cos

zMass = 91.2

# Reject Event if it does not have a Single Lepton and Two Photons
def passReqNumParticles(photons, electrons, muons, reqNumPhotons, reqNumLeptons):
    if len(photons) == reqNumPhotons:
        if len(electrons) == reqNumLeptons and len(muons) == 0: return True
        if len(electrons) == 0 and len(muons) == reqNumLeptons: return True

        #if len(electrons) == reqNumLeptons and len(muons) == 0 and len(taus) == 0: return True
        #if len(electrons) == 0 and len(muons) == reqNumLeptons and len(taus) == 0: return True
        #if len(electrons) == 0 and len(muons) == 0 and len(taus) == reqNumLeptons: return True
    return False

# Reject Event if the Photons are Too Close
def passPhotonPhotonDeltaR(photons, minPhotonPhotonDeltaR):
    for photon1 in photons:
        for photon2 in photons:
            if photon1 == photon2: continue # Do Not Compare it to Itself
            if photon1.DeltaR(photon2) < minPhotonPhotonDeltaR: return False
    # Only if all pairings pass
    return True 

def passPhotonLeptonDeltaR(photons, leptons, minPhotonLeptonDeltaR):
    for photon in photons:
        for lepton in leptons:
            if photon.DeltaR(lepton) < minPhotonLeptonDeltaR: return False
    # Only if all pairings pass
    return True

def passMt(leptons, neutrinos, minMt):
    summed_nu=TLorentzVector()
    for nu in neutrinos:
        summed_nu += nu
        
    for lepton in leptons:
        Mt2 = 2*lepton.Et()*summed_nu.Et()*(1-cos(lepton.DeltaPhi(summed_nu)))
        Mt = sqrt(Mt2)
        if Mt < minMt: return False

    return True
    
# Reject Event if Photon and Electron are too close
#def passPhotonElectronDeltaR(photons, electrons):
#    for photon in photons:
#        for electron in electrons:
#            if photon.DeltaR(electron) < minPhotonElectronDeltaR: return False
    # Only if all pairings pass
#    return True

#def passPhotonMuonDeltaR(photons, muons):
#    for photon in photons:
#        for muon in muons:
#            if photon.DeltaR(muon) < minPhotonMuonDeltaR: return False
    # Only if all pairings pass
#    return True

def passZ2Mass(photons, electrons):
    for photon in photons:
        for electron in electrons:
            M = (electron + photon).M()
            if abs(M - zMass) < 5: return False
    # Only if all pairings pass
    return True

def passZ3Mass(photons, electrons):
    for photon1 in photons:
        for photon2 in photons:
            if photon1 == photon2: continue # Do Not Compare it to Itself
            for electron in electrons:
                M = (electron + photon1 + photon2).M()
                if abs(M - zMass) < 5: return False
    # Only if all pairings pass
    return True

# Checks that there are only 2 signal photons in the event.
def passDiPhotonMass(photons):
    if(len(photons)==2):
        M=(photons[0]+photons[1]).M()
        if M > 15: return True
    return False
