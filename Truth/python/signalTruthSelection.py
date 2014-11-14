from ROOT import gSystem
from ROOT import TFile
from ROOT import TTree
from ROOT import TDirectory, gDirectory
from ROOT import TLorentzVector
from ROOT import TH1F, TH2F
from ROOT import TBranchElement
from math import sqrt, cos
#import sys
#My Own Helper Modules
import particleIdentification
import objectCuts
import overlapCuts
import eventCuts
import histogramBuilder

#
# Define Root Files and Tree Locations and Names
#

workDirLoc = '/home/cranelli/WGamGam/Anomolous_QGC/CMSSW_5_3_12/src/Anomolous_QGC/Analysis/python/'
inRootFileDir = '../test/'
inRootFileName = 'signalTruth_WAA_ISR_Job0.root'
#inRootFileDir = '/data/users/cranelli/WGamGam/SignalTruth'
#inRootFileName = "/signaltruth_job_summer12_WAA_ISR.root"
treeLoc = "ggNtuplizer/EventTree"
outRootFileName = 'signalTruthISRSelection.root'
#print sys.path

#
# Begining of Analysis Code
#

def signalTruthSelection():

    inRootFileLoc = inRootFileDir + inRootFileName
    inRootFile = TFile(inRootFileLoc, "READ")
    # Set Histograms
    h1PhoLeadPt = TH1F("h1PhoLeadPt","Lead Photon Pt", 400, 0, 200)
    h1PhoLeadEta = TH1F("h1PhoLeadEta", "Lead Photon Eta", 100, -3, 3)
    h2M3M4 = TH2F("h2M4M4", "M3 vs M4", 400, 0, 200, 400, 0 ,200)
    # h1PhoLeadPtWeighted = TH1F("h1" + prefix + "PhoLeadPtWeighted", prefix +"Lead Photon Pt Weighted",
    #                           400, 0, 200)
    
    # h1Mt = TH1F("h1"+prefix+"Mt", prefix + "Transverse Mass LV", 20, 0, 100)


    analysis_tree = inRootFile.Get(treeLoc)
    print "Tree ", analysis_tree
    
    num_entries = analysis_tree.GetEntries()
    print "Number of Entries: ", num_entries
    
    #
    # Loop Over Entries
    #
    
    for entry in xrange(num_entries):
        analysis_tree.GetEntry(entry)
        # print analysis_tree.__dict__
            
        # Select Event, should be only one per entry.
        # event = analysis_tree.Event[0]
        # weight = event.Weight

        # Assign Particles
        # Will be filled with TLorentz Vector, for now.
        photons = []
        electrons = []
        muons = []
        nu_es = []
        nu_ms = []
        ws = []

        #
        # Particle Identification
        #

        particleIdentification.assignParticles(analysis_tree, photons, electrons, muons, nu_es, nu_ms, ws)
        histogramBuilder.fillStandardHistograms(photons, electrons, muons, "PreCut")

        #
        # Selection Cuts
        #

        # Object Cuts
        # Make Kinematic Selection Cuts
        photons = objectCuts.selectOnPhotonKinematics(photons)
        electrons = objectCuts.selectOnElectronKinematics(electrons)
        muons = objectCuts.selectOnMuonKinematics(muons)

        # Overlap Cuts

        # Event Cuts
        if not eventCuts.passReqNumParticles(photons, electrons, muons): continue
        if not eventCuts.passPhotonPhotonDeltaR(photons): continue
        # Electron Channel
        if len(electrons) == 1:
            if not eventCuts.passPhotonElectronDeltaR(photons, electrons): continue
            histogramBuilder.fillStandardHistograms(photons, electrons, muons, "PostEventCuts_ElectronChannel")
            
        # Muon Channel
        if len(muons) == 1:
            if not eventCuts.passPhotonMuonDeltaR(photons, muons): continue
            histogramBuilder.fillStandardHistograms(photons, electrons, muons, "PostEventCuts_MuonChannel")
        

        #
        # Analysis
        #
        leptons = electrons + muons
        nus = nu_es + nu_ms


        leadPhoton = selectLead(photons)
        #lepton = selectLead(leptons) # Have signal electron be the one with highest Pt 
        #nu = selectLead(nus)
        #subPhoton = selectSub(photons)

        if leadPhoton != None :
            h1PhoLeadPt.Fill(leadPhoton.Pt())
            h1PhoLeadEta.Fill(leadPhoton.Eta())
        
        """
        if leadPhoton != None and subPhoton != None and lepton != None and nu != None:
            m3 = (leadPhoton + lepton + nu).M() #Does not include sub leading lepton
            m4 = (leadPhoton + subPhoton + lepton +nu).M()
            h2M3M4.Fill(m3, m4)
        """
                         
    outRootFile = TFile(outRootFileName, 'RECREATE')
    outRootFile.cd()
    # outRootFile.Write #Does not seem to have anything in memmory.
    h1PhoLeadPt.Write()
    h1PhoLeadEta.Write()
    #Iterate Over Selection Histograms
    for key, Histogram in histogramBuilder.Histograms.iteritems():
        Histogram.Write()
    #h2M3M4.Write()
    # h1PhoLeadPtWeighted.Write(
    # h1Mt.Write()
    inRootFile.Close()
    outRootFile.Close()

def selectLead(particles):
    maxPt = 0
    lead = None
    for particle in particles:
        if particle.Pt() > maxPt :
            maxPt = particle.Pt()
            lead =  particle
    return lead

def selectSub(particles):
    maxPt = 0
    lead = None
    sub = None
    for particle in particles:
        if particle.Pt() > maxPt:
            maxPt = particle.Pt()
            sub = lead
            lead = particle
        
    return sub

if __name__=="__main__":
    signalTruthSelection()
    


