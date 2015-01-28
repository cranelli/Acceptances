#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F

#fileLoc ="../Acceptances.root"
#histName="Category_LeadPhotonPt_MuonChannel"
#histName="Category_PtAndLocation_Acceptances_ElectronChannel"
#histName="Acceptances"

fileLoc ="../AnalysisRecoCuts_ScaleFactors_WeightedTotal_CategoryHistograms.root"
#histName="Category_PtAndLocation_MuonChannel"
histName="Category_PtAndLocation_ScaleFactorWeightMuonChannel"

def printBinContent():
    file = TFile(fileLoc, 'READ')
    #printh1BinContent(file, histName)
    printh2BinContent(file, histName)
    #printh2BinError(file, histName)


def printh1BinContent(file, h1Name):
    #hist = TH1F()
    print histName
    h1 = file.Get(h1Name)
    #print h1.GetBinContent(0)
    
    for i in range(1, h1.GetNbinsX()+1):
        output = str(h1.GetBinLowEdge(i)) +" : " +str(h1.GetBinContent(i))
        print output
        #print h1.GetBinContent(i)

def printh2BinContent(file, h2Name):
    print h2Name
    print "Bins' Content:"
    h2 = file.Get(h2Name)
    for i in range(1, h2.GetNbinsX()+1):
        for j in range(1, h2.GetNbinsY()+1):
            output = str(h2.GetXaxis().GetBinLowEdge(i))+","+str(h2.GetYaxis().GetBinLowEdge(j))+" : "+ str(h2.GetBinContent(i,j))+" pm " + str(h2.GetBinError(i,j))
            print output
                                                                                                            
#def printh2BinError(file,h2Name):
#    print h2Name
#    print "Bins' Content:"
#    h2 = file.Get(h2Name)
#    for i in range(1, h2.GetNbinsX()+1):
#        for j in range(1, h2.GetNbinsY()+1):
#            error_output = str(h2.GetXaxis().GetBinLowEdge(i))+","+str(h2.GetYaxis().GetBinLowEdge(j))+" : "+ str(h2.GetBinError(i,j))
#            print error_output
                                                                                                 
    
if __name__=="__main__":
    printBinContent()
