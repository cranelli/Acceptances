"""
signalTruthSelection - Makes Histograms, Pre/Post Cuts on ROOT file 
                       for LNuAA Analysis
"""

# Python: main program for signal truth analysis
# Note: Run PyROOT in batch mode (-b) to suppress canvas output

# Created by Christopher Anelli, 8.4.2014
# Edits by Nicholas Zube, 9.30.2014
# Tested in Python 2.6.4

from ROOT import gSystem
from ROOT import TFile
from ROOT import TTree
from ROOT import TDirectory, gDirectory
from ROOT import TLorentzVector
from ROOT import TH1F, TH2F
from ROOT import TBranchElement
#Local Modules
import particleIdentification
import objectCuts
import eventCuts
import parentCuts
import histogramBuilder
import histPublish

import FiducialCutValues

# Define the following variables before running:
# Input file names

inRootFileDir = '/data/users/cranelli/WGamGam/Acceptances/CommonFiducial/'
inRootFileName = 'CommonFiducialEvents_ISR.root'
treeLoc = 'EventTree'
# Output file names
outRootFileName = 'FiducialISR_Selection_Full.root'
histDirLoc = 'histI/'
acceptanceTableFileName = "ISR"
ptBins = [15, 25, 40, 80]

def FiducialSelection():

    inRootFileLoc = inRootFileDir + inRootFileName
    inRootFile = TFile(inRootFileLoc, "READ")

    # Seth2M3M4 Histogram
    h2M3M4 = TH2F("h2M3M4", "M3 vs M4", 400, 0, 200, 400, 0 ,200)
 
    print "Running on file: ", inRootFileLoc
    analysis_tree = inRootFile.Get(treeLoc)
    print "Tree ", analysis_tree  
    num_entries = analysis_tree.GetEntries()
    print "Number of Entries: ", num_entries
    
    # Lists of events remaining after each cut step 
    # (e.g., event_Electron_count)
    numberOfCuts = 7    
    evEcount = [0] * numberOfCuts
    evMcount = [0] * numberOfCuts
    countByPT = {}

    # Uses a dictionary to store [Ecounts, Mcounts] by PT bin for each cut
    # countByPt[pt bin min][cut #][# e counts, # mu counts]
    for ptKey in ptBins:
        a = {}
        for cutNum in xrange(numberOfCuts):
            a[cutNum] = [0,0]
        countByPT[ptKey] = a
            
    # Loop Over Entries (Master Loop)
    for entry in xrange(num_entries):
        analysis_tree.GetEntry(entry)

        # Assign Particles
        photons = []
        electrons = []
        muons = []
        nu_es = []
        nu_ms = []
        ws = []

        # Particle Identification step
        particleIdentification.assignParticles(
                analysis_tree, photons, electrons, muons, nu_es, nu_ms, ws)

        # Common Fiducial Cuts
        
        #Status Cuts, Select Final State
        photons = objectCuts.selectOnStatus(photons)
        electrons = objectCuts.selectOnStatus(electrons)
        muons = objectCuts.selectOnStatus(muons)

        # Parent Cuts
        photons = parentCuts.selectOnPhotonParentage(photons)
        electrons= parentCuts.selectOnElectronParent(electrons)
        muons=parentCuts.selectOnMuonParent(muons)

        # Object Cuts: Make Kinematic Selection Cuts
        photons = objectCuts.selectOnPhotonKinematics(photons)
        electrons = objectCuts.selectOnElectronKinematics(electrons)
        muons = objectCuts.selectOnMuonKinematics(muons)
                
        # Event Cuts: beginning of split into electron and muon channels
        # Exact population requirement
        if not eventCuts.passReqNumParticles(photons, electrons, muons):
            continue
        
        #Photon Photon Delta R Cuts
        if not eventCuts.passPhotonPhotonDeltaR(photons): continue
                        
        # Electron Channel
        if len(electrons) == 1:
            if not eventCuts.passPhotonElectronDeltaR(photons, electrons): continue         

        # Muon Channel
        if len(muons) == 1:
            if not eventCuts.passPhotonMuonDeltaR(photons, muons): continue


        #
        # Make Fiducial Cuts
        #
        [countByPT, evEcount, evMcount] = fillCountAndHist(
            photons, electrons, muons, ptBins, 
            "1_CommonFiducialCuts_", 0,
            countByPT, evEcount, evMcount,"e")
        [countByPT, evEcount, evMcount] = fillCountAndHist(
            photons, electrons, muons, ptBins, 
            "0_CommonFiducialCuts_", 0,
            countByPT, evEcount, evMcount,"m")

        #photons = objectCuts.selectOnDetectorGap(photons)
        #[countByPT, evEcount, evMcount] = fillCountAndHist(
        #        photons, electrons, muons, ptBins, 
        #        "1_PhotonDetectorGapCuts_", 1,
        #        countByPT, evEcount, evMcount,"e")
        #[countByPT, evEcount, evMcount] = fillCountAndHist(
        #        photons, electrons, muons, ptBins, 
        #        "1_PhotonDetectorGapCuts_", 1,
        #        countByPT, evEcount, evMcount,"m")

        #if not eventCuts.passDiPhotonMass(photons): continue
        #[countByPT, evEcount, evMcount] = fillCountAndHist(
        #        photons, electrons, muons, ptBins, 
        #        "2_DiPhotonMass_", 2,
        #        countByPT, evEcount, evMcount,"e")
        #[countByPT, evEcount, evMcount] = fillCountAndHist(
        #        photons, electrons, muons, ptBins, 
        #        "2_DiPhotonMass_", 2,
        #        countByPT, evEcount, evMcount,"m")

        # Electron Channel
        if len(electrons) == 1:
            electrons = filter(lambda electron:
                               electron.Pt() > FiducialCutValues.ELECTRON_CANDIDATE_MIN_PT, electrons)
            [countByPT, evEcount, evMcount] = fillCountAndHist(
                photons, electrons, muons, ptBins,
                "4_ElectronFiducialPt_", 4,
                countByPT, evEcount, evMcount,"e")
         #   if not eventCuts.passZ2Mass(photons, electrons): continue
         #   [countByPT, evEcount, evMcount] = fillCountAndHist(
         #       photons, electrons, muons, ptBins, 
         #       "5_PostZ2MCut_", 5,
         #       countByPT, evEcount, evMcount,"e")         
            
         #   if not eventCuts.passZ3Mass(photons, electrons): continue
         #   [countByPT, evEcount, evMcount] = fillCountAndHist(
         #           photons, electrons, muons, ptBins, 
         #           "6_PostZ3MCut_", 6,
         #           countByPT, evEcount, evMcount,"e")    
            
        # Muon Channel
        if len(muons) == 1:
            muons = filter(lambda muon: abs(muon.Eta()) < FiducialCutValues.MUON_CANDIDATE_MAX_ETA, muons)
            [countByPT, evEcount, evMcount] = fillCountAndHist(
                photons, electrons, muons, ptBins,
                "3_PhotonMuonFiducialEta_", 3,
                countByPT, evEcount, evMcount,"m")

                    
        mAnalysis(photons, electrons, muons, nu_es, nu_ms, h2M3M4, 
                  "8_PostALL")

    outRootFile = TFile(outRootFileName, 'RECREATE')
    outRootFile.cd()
    h2M3M4.Write()
    
    # Iterate Over Selection Histograms
    for key, Histogram in histogramBuilder.Histograms.iteritems():
        Histogram.Write()

    inRootFile.Close()
    outRootFile.Close()
    
    print("E: ", evEcount, ", M: ", evMcount)
    for ptKey in countByPT:
        print "Bin", ptKey, "by cut:", countByPT[ptKey]

    # Make .png files for all histograms
    # Note: Run PyROOT in batch mode (-b) to suppress canvas output
    histPublish.histToPNG(outRootFileName, histDirLoc)
    # Make an HTML table of acceptance cut flow
    histPublish.makeAcceptanceTable(evEcount, evMcount, 
                                    acceptanceTableFileName + "_All")
    
    for ptKey in ptBins:
        for i in xrange(numberOfCuts):
            evEcount[i] = countByPT[ptKey][i][0]
            evMcount[i] = countByPT[ptKey][i][1]            
        histPublish.makeAcceptanceTable(evEcount, evMcount, 
                                        acceptanceTableFileName + 
                                        "_" + str(ptKey) + "PT")
        
    
    
### Helper Functions

# Boolean: returns true if event has at least 1 lepton and 2 photons
def eventTest(leptons, photons):
    if len(leptons) > 0 and len(photons) > 1 : return True
    return False

# Returns leading photon from list of photons, 
# returns None if list is empty
def selectLead(particles):
    maxPt = 0
    lead = None
    for particle in particles:
        if particle.Pt() > maxPt :
            maxPt = particle.Pt()
            lead =  particle
    return lead

# Returns subleading photon from list of photons, 
# returns None if # number of photons <= 1
def selectSub(particles):
    maxPt, submaxPt = 0, 0
    lead, sub = None, None
    for particle in particles:
        if particle.Pt() > maxPt:
            sub = lead
            submaxPt = maxPt
            lead = particle
            maxPt = particle.Pt()
        elif particle.Pt() > submaxPt:
            sub = particle
            submaxPt = particle.Pt()   
    return sub

# Given particle lists and cut information, iterates event counters and
# stores data in the standard histograms
def fillCountAndHist(photons, electrons, muons, ptBins, histKey, cutNum,
                     countByPT, evEcount, evMcount, eORm = 0):
    if eORm == 0 or eORm == 'e' or eORm == 'E' or eORm == "electron": 
        eORm = 0
        leptons = electrons
        histKey += "E_"
    elif eORm == 1 or eORm == 'm' or eORm == 'M' or eORm == "muon": 
        eORm = 1
        leptons = muons
        histKey += "M_"
    else: 
        eORm = 2
        leptons = electrons + muons
    
    if eventTest(leptons, photons):
        photonPTBin = whichPTBin(selectLead(photons), ptBins)
        if eORm != 1: 
            evEcount[cutNum] += 1
            if photonPTBin > 0:
                countByPT[photonPTBin][cutNum][0] += 1
        if eORm != 0: 
            evMcount[cutNum] += 1
            if photonPTBin > 0:
                countByPT[photonPTBin][cutNum][1] += 1
              
        histogramBuilder.fillStandardHistograms(photons, electrons, 
                muons, histKey + str(photonPTBin) + "_PT")
    return [countByPT, evEcount, evMcount]          

# Creates a histogram comparing Mass(L-Nu-g) to Mass (L-L-Nu-g)
def mAnalysis(photons, electrons, muons, nu_es, nu_ms, h2M3M4, suffix):
    # Leading/Sub-leading Photon Analysis        
    leptons = electrons + muons
    nus = nu_es + nu_ms
    
    leadPhoton = selectLead(photons)
    subPhoton = selectSub(photons)
    lepton = selectLead(leptons) # Let signal lepton be the one w/ highest PT 
    nu = selectLead(nus)
    
    if leadPhoton != None :
        histogramBuilder.fillPtHistograms([leadPhoton], 
                                          'Photon(Leading)_Pt_' + suffix)
        histogramBuilder.fillEtaHistograms([leadPhoton], 
                                          'Photon(Leading)_Eta_' + suffix)
    # Near-Z-Mass checks
    if(leadPhoton != None and subPhoton != None and lepton != None):
        m2_L = (leadPhoton + lepton).M()
        m2_S = (subPhoton + lepton).M()
        m3 = (leadPhoton + subPhoton + lepton).M()
        histogramBuilder.fillMHistograms(m2_L, 'Z2M(A_Lead+L)_' + suffix)
        histogramBuilder.fillMHistograms(m2_S, 'Z2M(A_Sub+L)_' + suffix)
        histogramBuilder.fillMHistograms(m3, 'Z3M(A+A+L)_' + suffix)               
    
    # Near-W-Mass checks
    if(leadPhoton != None and subPhoton != None and lepton != None 
       and nu != None):
        m3 = (leadPhoton + lepton + nu).M() # no sub leading lepton
        m4 = (leadPhoton + subPhoton + lepton + nu).M()
        histogramBuilder.fillMHistograms(m3, '3M(A+L+Nu)_' + suffix)
        histogramBuilder.fillMHistograms(m4, '4M(A+A+L+Nu)_' + suffix)                
        h2M3M4.Fill(m3, m4)

# Given a photon and a set of bin minimums, returns an integer for which
# bin it belongs in        
def whichPTBin(leadPhoton, ptBins):
    if leadPhoton != None:
        for i in xrange(len(ptBins)-1):
            min = ptBins[i]
            max = ptBins[i+1]
            if leadPhoton.Pt() >= min and leadPhoton.Pt()< max:
                return min
        finalMin = ptBins[len(ptBins)-1]
        if leadPhoton.Pt() >= finalMin:
            return finalMin
    return 0

if __name__=="__main__":
    FiducialSelection()
    
