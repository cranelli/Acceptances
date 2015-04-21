"""Histogram Builder - fills a dictionary of histograms"""

# Python Module For Histogram Filling
# Created by Christopher Anelli, 8.4.2014
# Tested in Python 2.6.4

from ROOT import TLorentzVector
from ROOT import TH1F, TH2F

from array import array

Histograms = {}
 
# Function to Create and Fill Count Histograms
#def fillParticleCountHistograms(particles, key, bins=2, xmin=0, xmax=2):
#    if not key in Histograms:
#        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
#    for particle in particles: Histograms[key].Fill(1)

def fillPtCategoryHistograms(prefix, pt, weight=1,bins=4):
    key=prefix + "_Category_Pt"
    binLowE = [15,25,40,70,200]
    if not key in Histograms:
        Histograms[key]=TH1F(key, key, bins,array('d',binLowE))
        Histograms[key].Sumw2()
    Histograms[key].Fill(pt, weight)

def fillPhotonLocationCategoryHistograms(prefix, locId, weight=1,bins=4, xmin=0, xmax=4):
    key=prefix + "_Category_PhotonLocations"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].Sumw2()
    Histograms[key].Fill(locId)

def fillPtAndLocationCategoryHistograms(prefix,locId, pt, weight=1, xbins=4, xmin=0, xmax=4, ybins=4):
    key=prefix + "_Category_PtAndLocation"
    binLowE = [15,25,40,70,200]
    if not key in Histograms:
        Histograms[key] = TH2F(key,key, xbins, xmin, xmax, ybins, array('d',binLowE))
        Histograms[key].Sumw2()
    Histograms[key].Fill(locId,pt,weight)

def fillCountHistograms(prefix, weight=1, bins=2, xmin=0, xmax=2):
    key = prefix + "_Count"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].GetYaxis().SetTitle("Counts")
        Histograms[key].Sumw2()
    Histograms[key].Fill(1,weight)

def fillScaleFactorHistograms(key, scaleFactor, weight=1, bins=200, xmin=0, xmax=2):
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
    Histograms[key].Fill(scaleFactor,weight)
    
#Function to Create and Fill Number of Particles Histograms
def fillMultiplicityHistograms(prefix, multiplicity, weight=1, bins=20, xmin=0, xmax=20):
    key = prefix+"_Multiplicity"
    if not key in Histograms:
        Histograms[key] = TH1F(key, key, bins, xmin, xmax)
        Histograms[key].GetYaxis().SetTitle("Multiplicity")
        Histograms[key].Sumw2()
    Histograms[key].Fill(multiplicity, weight)

# Function to Create and Fill Pt Histograms
def fillPtHistograms(prefix, pt, weight=1, bins=400, xmin=0, xmax=200):
    key = prefix+"_Pt"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].GetXaxis().SetTitle("Pt (GeV)")
        Histograms[key].Sumw2()
    Histograms[key].Fill(pt, weight)

#Function to create and Fill a 2D Pt Histograms
def fill2DPtHistograms(prefix, x_pt, y_pt, weight=1, xbins=400, xmin=0, xmax=200, ybins=400, ymin=0, ymax=200):
    key = prefix+"_2DPt"
    if not key in Histograms:
        Histograms[key] = TH2F(key, key, xbins, xmin, xmax, ybins, ymin, ymax)
        Histograms[key].GetXaxis().SetTitle("Pt (GeV)")
        Histograms[key].GetYaxis().SetTitle("Pt (GeV)")
        Histograms[key].Sumw2()
    Histograms[key].Fill(x_pt, y_pt, weight)                  

# Function To Create and Fill Eta Histograms
def fillEtaHistograms(prefix, eta, bins=120, xmin=-3, xmax=3):
    key = prefix+"_Eta"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].Sumw2()
    Histograms[key].Fill(eta)

# Watch out for double counting when particles1 = particles2
def fillDeltaRHistograms(prefix, deltaR, bins=200, xmin=0, xmax=8):
    key = prefix + "_dR"
    if not key in Histograms:
        Histograms[key] = TH1F(key, key, bins, xmin, xmax)
        Histograms[key].Sumw2()
    Histograms[key].Fill(deltaR)

def fillStatusHistograms(prefix, status, bins=4, xmin=0, xmax=4):
    key = prefix+ "_Status"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].Sumw2()
    Histograms[key].Fill(status)

def fillPDGIDHistograms(prefix, pdgId, bins=100, xmin=-50, xmax=50):
    key = prefix +"_PDGID"
    if not key in Histograms:
        Histograms[key] = TH1F(key,key, bins, xmin, xmax)
        Histograms[key].Sumw2()
    Histograms[key].Fill(pdgId)

def fillMHistograms(m, key, bins=300, xmin=0, xmax=300):
    if not key in Histograms:
        Histograms[key] = TH1F(key, key, bins, xmin, xmax)
        Histogrmas[key].Sumw2()
    Histograms[key].Fill(m)

def fillMtHistograms(prefix, Mt, weight=1, bins=200, xmin=0, xmax =400):
    key = prefix+"_Mt"
    if not key in Histograms:
        Histograms[key] = TH1F(key, key, bins, xmin, xmax)
        Histograms[key].GetXaxis().SetTitle("Mt (GeV)")
        Histograms[key].Sumw2()
    Histograms[key].Fill(Mt, weight)
    
#def fillStandardHistograms(photons, electrons, muons, suffix):
    # Photons
#    fillCountHistograms(photons, 'Photon_'+suffix)
#    fillPtHistograms(photons, 'Photon_Pt_' + suffix)
#    fillEtaHistograms(photons, 'Photon_Eta_' + suffix)
#    fillNumParticleHistograms(photons, 'Photon_Num_' + suffix)
#    fillStatusHistograms(photons, "Photon_Status_" + suffix)
    # Electrons
#    fillCountHistograms(electrons, 'Electron_' + suffix)
#    fillPtHistograms(electrons, 'Electron_Pt_' + suffix)
#    fillEtaHistograms(electrons, 'Electron_Eta_' + suffix)
#    fillNumParticleHistograms(electrons, 'Electron_Num_' + suffix)
#    fillStatusHistograms(electrons, "Photon_Status_" + suffix)
    # Muons
#    fillCountHistograms(muons, 'Muon_' + suffix)
#    fillPtHistograms(muons, 'Muon_Pt_' + suffix)
#    fillEtaHistograms(muons, 'Muon_Eta_' + suffix)
#    fillNumParticleHistograms(muons, 'Muon_Num_' + suffix)
#    fillStatusHistograms(muons, "Photon_Status_" + suffix)
    # Delta R
#    fillDeltaRHistograms(photons, electrons, 'DeltaR(Ae)_' + suffix)
#    fillDeltaRHistograms(photons, muons, 'DeltaR(AMu)_' + suffix)
#    fillDeltaRHistograms(photons, photons, 'DeltaR(AA)_' + suffix)
    

