#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
from collections import namedtuple
#from decimal import getcontext

fileLoc ="../Histograms/Acceptances_PDFReweights_4_19_2015.root"
FILE = TFile(fileLoc, 'READ')
channels=["MuonChannel", "ElectronChannel"]
histTypes=["Category_Pt"]
#histTypes=["Category_PtAndLocation"]
outFileDir="../Tables/PDFSystematics/"

PDF_EIGENVECTOR_NAME="cteq66"
NUM_PDF_EIGENVECTORS=45

PDFSystematicStruct = namedtuple("PdfSystematicsStruct", "UP DN")

def printPDFSystematics():
    
    for channel in channels:
        for histType in histTypes:
            # Stores PDF Systematics for Each Bin
            PDFSystematicAllBins=CalcPDFSystematicAllBins(channel, histType)
        
        print "PDF Systematics for Entries in " + channel + " " + histType
        print "PDF Systematics Up: "
        #print PDFSystematicAllBins.UP
        print "PDF Systematics Dn: "
        #print PDFSystematicAllBins.DN
            
        """
        print "root sum of squares:"
        print "master differences up"
        print sumInQuadrature(masterDifferencesUpAllEigenvectors)
        print "master differences down"
        print sumInQuadrature(masterDifferencesDownAllEigenvectors)
        """
            
    FILE.Close()


def CalcPDFSystematicAllBins(channel, histType):
    # Select Histogram with the Central Value 0
    centralPDFHist=GetCentralPDFHist(channel, histType)
    # Loop over All bins in the Histogram, including the overflow bin.
    for bin_index in range(1, centralPDFHist.GetNbinsX()+2):
        PDFSystematic = CalcPDFSystematic(channel, histType, bin_index)
        PDFSystematicAllBins.append(PDFSYstematic)
    return PDFSystematicAllBins


# Calculates the PDF Systematic over all the Eigenvectors, using the Master Equation
def CalcPDFSystematic(channel, histType, bin_index):

    PDFSystematic = PDFSystematicStruct(0,0)
    masterDifferencesUpAllEigenvectors=[]
    masterDifferencesDnAllEigenvectors=[]

    centralPDFHist=GetCentralPDFHist(channel, histType)
    central_value = centralPDFHist.GetBinContent(bin_index)

    num_eigenvector_pairs = NUM_PDF_EIGENVECTORS/2
    for eigenpair_index in range(1, num_eigenvector_pairs):
        histUP =GetEigenvectorHistUP(channel, histType, eigenpair_index)
        up_value=histUP.GetBinContent(bin_index)
        histDN =GetEigenvectorHistDN(channel, histType, eigenpair_index)
        dn_value=histDN.GetBinContent(bin_index)
        masterDifferencesUpAllEigenvectors.append(masterDifferenceUP(central_value, up_value, dn_value))
        masterDifferencesDnAllEigenvectors.append(masterDifferenceDN(central_value, up_value, dn_value))
                                                  

    PDFSystematic.UP = sumInQuadrature(masterDifferencesUpAllEigenvectors)
    PDFSystematic.DN = sumInQuadrature(masterDifferencesDnAllEigenvectors)

    return PDFSystemtic
    

# up value comes from the "up eigenvector" and down from the "down eigenvector"
# But the master equation selects the one that actually causes the greatest difference
# up, unless both cause a downwards shift in which case 0 is taken.
def masterDifferenceUP(central, up, down):
    return max(up-central, down-central, 0)

# Same as masterDifferenceUp, but now selecting the largest downwards shift.
def masterDifferenceDN(central, up, down):
    return min(up - central, down - central, 0)


"""
    masterDifferencesUpAllEigenvectorsAllBins=[]
    masterDifferencesDownAllEigenvectorsAllBins=[]
    print centralPDFHist.GetName()
    # Loop Over Histograms for the PDF eigenvector UP DN pairs
    num_eigenvector_pairs = NUM_PDF_EIGENVECTORS/2
    for eigenpair_index in range(1, num_eigenvector_pairs):
        
        print histNameUP
        histNameDN = channel+"_"+PDF_EIGENVECTOR_NAME+"_"+ str(index_down)+"_PDFEigenvectorReweight_"+histType+"_Acceptances"
        print histNameDN
                
        
        histDN = file.Get(histNameDN)
                
        # Histogram Names
        printh1BinDifference(histUP, centralPDFHist)
        printh1BinDifference(histDN, centralPDFHist)
                
        # Master Euqation
        masterDifferenceUP=[]
        masterDifferenceDN=[]
        differenceUP=h1CalcDifferences(histUP, centralPDFHist)
        differenceDN=h1CalcDifferences(histDN, centralPDFHist)
        print differenceUP
        print differenceDN
        for bin_index in range(0, len(differenceUP)):
            masterDifferenceUP.append(max(differenceUP[bin_index], differenceDN[bin_index], 0))
            masterDifferenceDN.append(min(differenceUP[bin_index], differenceDN[bin_index], 0))
                
        print masterDifferenceUP
        print masterDifferenceDN
                
        masterDifferencesUpAllEigenvectors.append(masterDifferenceUP)
        masterDifferencesDownAllEigenvectors.append(masterDifferenceDN)

# elif hist.ClassName() == "TH2F":
#   printh2BinDifference(hist, centralPDFHist)
"""

#Sum the differences in Quadrature
def sumInQuadrature(differences):
    sumdif2=0
    for difference in differences:
        sumdif2 += difference **2
    rootsumdif2= sumdif2 **0.5
    return rootsumdif2



"""
# Sum the differences, for each list of differences in the Dictionairy.
def sumInQuadrature(differencesAllEigenvectors):
    sumdif2=[]
    for differences in differencesAllEigenvectors:
        for i in range(0, len(differences)):
            if len(sumdif2) != len(differences) :
                sumdif2.insert(i, differences[i] **2)
            else:
                sumdif2[i] += differences[i] **2

    #Than take the square root of each element
    rootsumdif2=[]
    for i in range(len(sumdif2)):
        rootsumdif2.insert(i, sumdif2[i] **0.5)
    return rootsumdif2
"""
#Selects the Central PDF Histogram 0
def GetCentralPDFHist(channel, histType):
    print channel+"_"+PDF_EIGENVECTOR_NAME+"_0_PDFEigenvectorReweight_"+histType+"_Acceptances"
    centralPDFHist = FILE.Get(channel+"_"+PDF_EIGENVECTOR_NAME+"_0_PDFEigenvectorReweight_"+histType+"_Acceptances")
    return centralPDFHist

# Selects the UP PDF Histogram, for the given eigenpair_index
def GetEigenvectorHistUP(channel, histType, eigenpair_index):
    index_up = 2*eigenpair_index-1
    histNameUP = channel+"_"+PDF_EIGENVECTOR_NAME+"_"+ str(index_up)+"_PDFEigenvectorReweight_"+histType+"_Acceptances"
    print histNameUP
    histUP = FILE.Get(histNameUP)
    return histUP

# Selects the DN PDF Histogram, for the given eigenpair_index
def GetEigenvectorHistDN(channel, histType, eigenpair_index):
    index_down = 2*eigenpair_index
    histNameDN = channel+"_"+PDF_EIGENVECTOR_NAME+"_"+ str(index_down)+"_PDFEigenvectorReweight_"+histType+"_Acceptances"
    print histNameDN
    histDN = FILE.Get(histNameDN)
    return histDN

"""
def h1CalcDifferences(h1, h1Expected):
    differences=[]
    for x in range(1, h1.GetNbinsX()+1):
        differences.append(h1.GetBinContent(x)-h1Expected.GetBinContent(x))
    return differences

# For a two 1D Histograms, prints the differences of the bin contents
def printh1BinDifference(h1, h1Expected):
    #hist = TH1F()
    output=""
    for i in range(1, h1.GetNbinsX()+1):
        output = str(h1.GetBinLowEdge(i)) +" : " +str(h1.GetBinContent(i)-h1Expected.GetBinContent(i))
        print output
        #print h1.GetBinContent(i)

def h2CalcDifferences(h2, h2Expected):
    differences=[]
    for y in range(1, h2.GetNbinsY()+1):
        # Loop Over Columns (Photons' Location)
        for x in range(1, h2.GetNbinsX()+1):
            differences.append(h2.GetBinContent(x,y)-h2Expected.GetBinContent(x,y))
    return differences
"""
        
# def printh2BinDifference(h2, h2Expected):
#    outfile =open(outFileDir+"BinDifferences_"+h2.GetName()+".html", 'w')
#    print "Bins Content:"
#    outfile.write(htmlTableHeader)
#    output=""
#    htmlOutput=""
    
    # Loop Over Rows (Pt)
    #    for j in range(1, h2.GetNbinsY()+1):
    #    outfile.write("""<tr align="center">""")
        # Loop Over Columns (Photons' Location)
        #   for i in range(1, h2.GetNbinsX()+1):
        #    output = str(h2.GetXaxis().GetBinLowEdge(i))+","+str(h2.GetYaxis().GetBinLowEdge(j))+" : "+ str(format(h2.GetBinContent(i,j),'.3f'))+" pm " + str(format(h2.GetBinError(i,j),'.3f'))
            #print output
            # Bin Content and Errors in HTML format
            #            htmlOutput = """<td valign="middle">""" + str(format(h2.GetBinContent(i,j)-h2Expected.GetBinContent(i,j),'.4f'))+ """</td>"""
            #outfile.write(htmlOutput)
            #outfile.write("""</tr>""")
            
            #outfile.write(htmlTableCloser)
#outfile.close()

                                                                                                 
    
if __name__=="__main__":
    printPDFSystematics()
