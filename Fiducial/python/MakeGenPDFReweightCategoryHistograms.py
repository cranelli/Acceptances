# Python Code for making Generator Info Histograms
# Includes options for PDF reweighting.
# Expected to run on root files, that have been through the Common Fiducial Skim
# Example execution from command line:
# python MakeGenPDFReweightCategoryHistograms.py /data/users/cranelli/WGamGam/Acceptances/CommonFiducial_wMT_Skim_PDFReweights/job_summer12_WAA_ISR/tree.root test.root

import sys

from ROOT import TFile
from ROOT import TTree
from ROOT import vector

import CommonFiducialCutValues
import particleIdentification
import objectCuts
import parentCuts
import histogramBuilder

# Define Global Variables

TREELOC="EventTree"
OUTDIR="../test/Histograms/"

# Standard Histograms (No Reweighting)
DO_NO_REWEIGHT=True

#Central PDF Reweighting
DO_CENTRAL_PDF_REWEIGHT=True
PDF_NAMES=['cteq6l1', 'MSTW2008lo68cl', 'cteq66'] #cteq6l1 is the original
ORIG_PDF_NAME = 'cteq6l1'

#Eigenvector PDF Reweighting
DO_EIGENVECTOR_PDF_REWEIGHT=True
EIGENVECTOR_PDF_NAME= 'cteq66'

# PdgIds
ELECTRON_PDGID = 11
MUON_PDGID = 13
TAU_PDGID = 15
PHOTON_PDGID = 22
W_PDGID = 24

# Statuses
FINAL_STATE_STATUS=1
HARD_SCATTER_STATUS=3

#Photon and Lepton Cut Values
MIN_PHOTON_PT = CommonFiducialCutValues.PHOTON_CANDIDATE_MIN_PT
MAX_PHOTON_ETA = CommonFiducialCutValues.PHOTON_CANDIDATE_MAX_ETA
MIN_LEPTON_PT = CommonFiducialCutValues.LEPTON_CANDIDATE_MIN_PT
MAX_LEPTON_ETA = CommonFiducialCutValues.LEPTON_CANDIDATE_MAX_ETA
REQ_NUM_LEPTONS = CommonFiducialCutValues.NUM_CANDIDATE_LEPTONS

# Makes Gen Histograms
def MakeGenPDFReweightCategoryHistograms(inFileLoc="job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root",
                                         outFileName="test.root"):
    # Original File
    origFile = TFile(inFileLoc)
    tree = origFile.Get(TREELOC)
    # New File
    outFile = TFile(OUTDIR + outFileName, "RECREATE")
    
    nentries = tree.GetEntries()
    print "Number of Entries", nentries

    # Holder for PDF Pair Information
    xfx_pair_dict = GetPDFPairInfo(tree)
        
    # Loop Over Events
    for i in range(0, nentries):
        if(i%1000==0): print i
        tree.GetEntry(i)
        
        # Select Particles
        photons = SelectPhotons(tree)
        electrons = SelectElectrons(tree)
        muons = SelectMuons(tree)
        taus = SelectTaus(tree)
        
        # W and Tau Parent Separation
        w_electrons= parentCuts.selectOnParentID(electrons, W_PDGID)
        w_muons=parentCuts.selectOnParentID(muons, W_PDGID)
        w_taus=parentCuts.selectOnParentID(taus, W_PDGID)
        
        tau_electrons= parentCuts.selectOnParentID(electrons, TAU_PDGID)
        tau_muons=parentCuts.selectOnParentID(muons, TAU_PDGID)
        
        #if len(taus)>0 :
        #    print len(taus),
        #    print len(w_taus),
        #    print len(tau_electrons),
        #    print len(tau_muons)
        
        # Identify the Decay Type
        decayType = SelectDecayType(w_electrons, w_muons, w_taus, tau_electrons, tau_muons)
        
        # Make Regular Histograms (No Reweighting)
        MakeBasicHistograms(decayType, photons)

        # Calculate Central PDF Reweight
        if DO_CENTRAL_PDF_REWEIGHT:
            MakeCentralPDFReweightHistograms(xfx_pair_dict, decayType, photons)
        
        # Calculate Eigenvector PDF Reweight, for all of the eigenvectors in "EIGENVECTOR_PDF_NAME"
        if DO_EIGENVECTOR_PDF_REWEIGHT:
            MakeEigenvectorPDFReweightHistograms(xfx_pair_dict, decayType, photons)
           
    outFile.Write()

# Returns a dictionary, for each pdf set, with a link to the first and second parton
# distribution function, xfx, information from the root tree.
def GetPDFPairInfo(tree):
    xfx_pair_dict = {}
    for pdf_name in PDF_NAMES:
        print pdf_name
        xfx_pair_dict[pdf_name] = [vector('double')(), vector('double')()]
        tree.SetBranchAddress('xfx_first_'+pdf_name, xfx_pair_dict[pdf_name][0])
        tree.SetBranchAddress('xfx_second_'+pdf_name, xfx_pair_dict[pdf_name][1])
    return xfx_pair_dict

# Standard Generator Histograms, weight is one.
def MakeBasicHistograms(decayType, photons):
    weight =1
    prefix = decayType + "_unweighted"
    MakeHistograms(prefix, photons, weight)


# Makes the Histograms for the Central PDF Reweightings
# Uses the parton distribution functions stored in xfx_pair_dict to calculate
# the reweighting from the central value of the original pdf to the new pdf.
def MakeCentralPDFReweightHistograms(xfx_pair_dict, decayType, photons):
    for pdf_name in PDF_NAMES:
        prefix = decayType+"_"+pdf_name+"_PDFReweight"
        reweight = calcPDFReweight(xfx_pair_dict, ORIG_PDF_NAME, pdf_name)
        MakeHistograms(prefix, photons, reweight)

# Makes the Histograms for the Eigenvector PDF Reweightings
# Uses the pdf info stored in xfx_pair_dict, to calculate
# the reweighting from a PDF sets central value to one of
# it's eigenvector values.
def MakeEigenvectorPDFReweightHistograms(xfx_pair_dict, decayType, photons):
    for pdf_eigenvector_index in range(0, xfx_pair_dict[EIGENVECTOR_PDF_NAME][0].size()):
        prefix=decayType + "_"+EIGENVECTOR_PDF_NAME+"_"+str(pdf_eigenvector_index)+"_PDFEigenvectorReweight"
        eigenvector_reweight = calcPDFEigenvectorReweight(xfx_pair_dict, EIGENVECTOR_PDF_NAME, pdf_eigenvector_index)
        MakeHistograms(prefix, photons, eigenvector_reweight)

# Distinguish between the different Leptonic Decay types of the W
# Also diferentiating between tau to e and tau to mu.
def SelectDecayType(w_electrons, w_muons, w_taus, tau_electrons, tau_muons):

    if len(w_electrons)==REQ_NUM_LEPTONS:
        return "ElectronDecay"

    if len(w_muons)==REQ_NUM_LEPTONS:
        return "MuonDecay"

    if len(tau_electrons) == REQ_NUM_LEPTONS:
        return "TauToElectronDecay"

    if len(tau_muons) == REQ_NUM_LEPTONS:
        return "TauToMuonDecay"


# Make Count, Lead Photon Pt, and other Histograms
def MakeHistograms(prefix, photons, reweight):
    histogramBuilder.fillCountHistograms(prefix, reweight)
    leadPhoton = selectLead(photons)
    histogramBuilder.fillPtHistograms(prefix, leadPhoton.Pt(), reweight)
    histogramBuilder.fillPtCategoryHistograms(prefix, leadPhoton.Pt(), reweight)
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

#Calculate Reweighting from central value of a set, to up-down eigenvector values of the set.
def calcPDFEigenvectorReweight(xfx_pair_dict, eigenvector_pdf_name, pdf_eigenvector_index):
    eigenvector_reweight =1;
    
    # Central Value is the 0 index in the vector
    xfx_first = xfx_pair_dict[eigenvector_pdf_name][0]
    xfx_second = xfx_pair_dict[eigenvector_pdf_name][1]
    central_xfx_first = xfx_first[0]
    central_xfx_second = xfx_second[0]

    eigenvector_xfx_first = xfx_first[pdf_eigenvector_index]
    eigenvector_xfx_second = xfx_second[pdf_eigenvector_index]
            
    eigenvector_reweight = (eigenvector_xfx_first * eigenvector_xfx_second) / (central_xfx_first*central_xfx_second)
    return eigenvector_reweight

# Select Particles that have a W Parent
#def SelectWChildren(tree):
#    wChildren = []
#    particleIdentification.assignParticleByParentID(tree, wChildren, W_PDGID)
#    return wChildren

# Select Photons, Can assume they come from a fiducial event, but must make sure that they
# also pass the photon object cuts.
def SelectPhotons(tree):
    photons = []
    particleIdentification.assignParticleByID(tree, photons, PHOTON_PDGID)
    photons= objectCuts.selectOnStatus(photons, FINAL_STATE_STATUS)
    photons=objectCuts.selectOnPtEta(photons, MIN_PHOTON_PT, MAX_PHOTON_ETA)
    photons=parentCuts.selectOnPhotonParentage(photons)
    return photons

# Select Electrons, Can assume event cut, but must redo the object level cuts.
def SelectElectrons(tree):
    electrons=[]
    particleIdentification.assignParticleByID(tree, electrons, ELECTRON_PDGID)
    objectCuts.selectOnStatus(electrons, FINAL_STATE_STATUS)
    objectCuts.selectOnPtEta(electrons, MIN_LEPTON_PT, MAX_LEPTON_ETA)
    return electrons

# Select Muons, Can assume event cut, but must redo the object level cuts.
def SelectMuons(tree):
    muons=[]
    particleIdentification.assignParticleByID(tree, muons, MUON_PDGID)
    objectCuts.selectOnStatus(muons, FINAL_STATE_STATUS)
    muons = objectCuts.selectOnPtEta(muons, MIN_LEPTON_PT, MAX_LEPTON_ETA)
    return muons

# Select Taus, Can assume event cut, but must redo the object level cuts.
def SelectTaus(tree):
    taus=[]
    particleIdentification.assignParticleByID(tree, taus, TAU_PDGID)
    objectCuts.selectOnStatus(taus, HARD_SCATTER_STATUS)
    return taus

#Select Lead Particle by Pt
def selectLead(particles):
    maxPt = 0
    lead = None
    for particle in particles:
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
    #otherwise
    return 3

# Distinguish between the different Leptonic Decay types of the W, and Makes Histograms
#def MakeHistogramsByDecayType(wChildren, suffix, photons, reweight):
#    for wChild in wChildren:
        # Electron Decay
        #        if(abs(wChild.PID()) == ELECTRON_PDGID and wChild.Status() == FINAL_STATE_STATUS):
        #   decay="ElectronDecay_" + suffix
        #    MakeHistograms(decay, photons, reweight)
        #if(abs(wChild.PID()) == MUON_PDGID and wChild.Status() == FINAL_STATE_STATUS):
        #    decay="MuonDecay_"+ suffix
        #    MakeHistograms(decay, photons, reweight)
        #if(abs(wChild.PID()) == TAU_PDGID and wChild.Status() == HARD_SCATTER_STATUS):
        #    decay="TauDecay_"+ suffix
#    MakeHistograms(decay, photons, reweight)

if __name__=="__main__":
        MakeGenPDFReweightCategoryHistograms(sys.argv[1], sys.argv[2])
    
