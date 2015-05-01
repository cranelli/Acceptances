#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
from collections import namedtuple
#from decimal import getcontext


HIST_DIR="../Histograms/LepGammaGammaFinalElandMuUnblindAll_2015_4_19_ScaleFactors_PDFReweights/"
fileLoc =HIST_DIR+"Acceptances_test.root"
FILE = TFile(fileLoc, 'READ')
channels=["MuonChannel", "ElectronChannel"]
Acceptances=["TauSig", "TauBkgd"]
histTypes=["Category_Pt", "Count"]


outFileLoc=HIST_DIR+"PDFSystematics_test.root"
OUT_FILE = TFile(outFileLoc, 'RECREATE')

PDF_SET_NAMES=['cteq6l1', 'MSTW2008lo68cl', 'cteq66']
ORIG_PDF_NAME='cteq6l1'

PDF_EIGENVECTOR_NAME="cteq66"
NUM_PDF_EIGENVECTORS=45

PDFEigenvectorSystematicStruct = namedtuple("PdfEigenvectorSystematicStruct", "UP DN")

def MakePDFSystematicHistograms():
    
    for channel in channels:
        for acceptance_type in Acceptances:
            for histType in histTypes:
                # Stores PDF Systematics for Each Bin
                #PDFSystematicAllBins=CalcPDFSystematicAllBins(channel, histType)
                MakePDFEigenvectorSystematicHistograms(channel, acceptance_type, histType)
                MakePDFSetSystematicHistograms(channel, acceptance_type, histType)
            
    FILE.Close()
    OUT_FILE.Close()


# Makes the Histograms Storing the PDF Eigenvector Systematics
def MakePDFEigenvectorSystematicHistograms(channel, acceptance_type, histType):
    
    # Select Histogram with the Central Value 0
    centralPDFHist=GetCentralPDFHist( channel, acceptance_type, histType)
    centralPDFHist.Print()

    # UP PDF Eigenvector Systematics
    pdfEigenvectorSystUPHistName=channel+"_"+acceptance_type+"_PDFEigenvectorSystematicUP_"+histType
    pdfEigenvectorSystUPHist=centralPDFHist.Clone(pdfEigenvectorSystUPHistName)
    pdfEigenvectorSystUPHist.Reset("ICE")
    
    pdfEigenvectorSystDNHistName=channel+"_"+acceptance_type+"_PDFEigenvectorSystematicDN_"+histType
    pdfEigenvectorSystDNHist=centralPDFHist.Clone(pdfEigenvectorSystDNHistName)
    pdfEigenvectorSystDNHist.Reset("ICE")
    
    # Loop over All bins in the Histogram, including the overflow bin.
    for bin_index in range(1, centralPDFHist.GetNbinsX()+2):
        PDFSystematic = CalcPDFEigenvectorSystematic(channel, acceptance_type, histType, bin_index)
        pdfEigenvectorSystUPHist.SetBinContent(bin_index, PDFSystematic.UP)
        #print str(bin_index)+": UP " + str(PDFSystematic.UP) ,
        pdfEigenvectorSystDNHist.SetBinContent(bin_index, PDFSystematic.DN)
        #print " DN " + str(PDFSystematic.DN) ,
    #print

    pdfEigenvectorSystUPHist.Print("all")
    pdfEigenvectorSystUPHist.Write()

    pdfEigenvectorSystDNHist.Print("all")
    pdfEigenvectorSystDNHist.Write()

# Makes the Histograms storing the PDF Set Systematic - the uncertainty depending on which
# PDF set was used.
def MakePDFSetSystematicHistograms(channel, acceptance_type, histType):
    origPDFHist = GetPDFSetHist(ORIG_PDF_NAME, channel, acceptance_type, histType)

    pdfSetSystHistName= channel+"_"+acceptance_type+"_PDFSetSystematic_"+histType
    pdfSetSystHist=origPDFHist.Clone(pdfSetSystHistName)
    pdfSetSystHist.Reset("ICE")

    # Loop over All bins in the Histogram, including the overflow bin.
    for bin_index in range(1, origPDFHist.GetNbinsX()+2):
        pdfSetSyst = CalcPDFSetSystematic(channel, acceptance_type, histType, bin_index)
        pdfSetSystHist.SetBinContent(bin_index, pdfSetSyst)

    pdfSetSystHist.Print("all")
    pdfSetSystHist.Write()

# Calculates the PDF systematic.  Takes the difference between the acceptance for the original
# PDF set and for the new PDF sets and sums them in quadrature.
def CalcPDFSetSystematic(channel, acceptance_type, hist_type, bin_index):
    differences=[]

    origPDFHist = GetPDFSetHist(ORIG_PDF_NAME, channel, acceptance_type, hist_type)

    for set_name in PDF_SET_NAMES:
        newPDFHist=GetPDFSetHist(set_name, channel, acceptance_type, hist_type)
        difference = newPDFHist.GetBinContent(bin_index)-origPDFHist.GetBinContent(bin_index)
        differences.append(difference)

    pdfSetSyst= sumInQuadrature(differences)
    return pdfSetSyst


# Calculates the PDF Systematic over all the Eigenvectors, using the Master Equation
def CalcPDFEigenvectorSystematic(channel, acceptance_type, histType, bin_index):

    masterDifferencesUpAllEigenvectors=[]
    masterDifferencesDnAllEigenvectors=[]

    centralPDFHist=GetCentralPDFHist(channel,acceptance_type, histType)
    central_value = centralPDFHist.GetBinContent(bin_index)

    num_eigenvector_pairs = NUM_PDF_EIGENVECTORS/2
    for eigenpair_index in range(1, num_eigenvector_pairs):
        histUP =GetEigenvectorHistUP(channel, acceptance_type, histType, eigenpair_index)
        up_value=histUP.GetBinContent(bin_index)

        histDN =GetEigenvectorHistDN(channel, acceptance_type, histType, eigenpair_index)
        dn_value=histDN.GetBinContent(bin_index)

        masterDifferencesUpAllEigenvectors.append(masterDifferenceUP(central_value, up_value, dn_value))
        masterDifferencesDnAllEigenvectors.append(masterDifferenceDN(central_value, up_value, dn_value))

    PDFEigenvectorSystematic_UP = sumInQuadrature(masterDifferencesUpAllEigenvectors)
    PDFEigenvectorSystematic_DN = sumInQuadrature(masterDifferencesDnAllEigenvectors)

    PDFEigenvectorSystematic = PDFEigenvectorSystematicStruct(PDFEigenvectorSystematic_UP,PDFEigenvectorSystematic_DN)
    return PDFEigenvectorSystematic
    

# up value comes from the "up eigenvector" and down from the "down eigenvector"
# But the master equation selects the one that actually causes the greatest difference
# up, unless both cause a downwards shift in which case 0 is taken.
def masterDifferenceUP(central, up, down):
    return max(up-central, down-central, 0)

# Same as masterDifferenceUp, but now selecting the largest downwards shift.
def masterDifferenceDN(central, up, down):
    return min(up - central, down - central, 0)


#Sum the differences in Quadrature
def sumInQuadrature(differences):
    sumdif2=0
    for difference in differences:
        sumdif2 += difference **2
    rootsumdif2= sumdif2 **0.5
    return rootsumdif2

# Gets the Histograms reweighted to a given PDF Set.
def GetPDFSetHist(pdf_set_name, channel, acceptance_type, histType):
    pdfHistName = channel+"_"+pdf_set_name+"_PDFReweight_Acceptance_"+acceptance_type+"_"+histType
    pdfHist = FILE.Get(pdfHistName)
    return pdfHist

#Selects the Central PDF Histogram 0
def GetCentralPDFHist(channel, acceptance_type, histType):
    histNameCentral= channel+"_"+PDF_EIGENVECTOR_NAME+"_0_PDFEigenvectorReweight_Acceptance_"+acceptance_type+"_"+histType
    print histNameCentral
    centralPDFHist = FILE.Get(histNameCentral)
    return centralPDFHist

# Selects the UP PDF Histogram, for the given eigenpair_index
def GetEigenvectorHistUP(channel, acceptance_type, histType, eigenpair_index):
    index_up = 2*eigenpair_index-1
    histNameUP = channel+"_"+PDF_EIGENVECTOR_NAME+"_"+ str(index_up)+"_PDFEigenvectorReweight_Acceptance_"+acceptance_type+"_"+histType

    print histNameUP
    histUP = FILE.Get(histNameUP)
    return histUP

# Selects the DN PDF Histogram, for the given eigenpair_index
def GetEigenvectorHistDN(channel, acceptance_type, histType, eigenpair_index):
    index_down = 2*eigenpair_index
    histNameDN = channel+"_"+PDF_EIGENVECTOR_NAME+"_"+ str(index_down)+"_PDFEigenvectorReweight_Acceptance_"+acceptance_type+"_"+histType
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
    MakePDFSystematicHistograms()
