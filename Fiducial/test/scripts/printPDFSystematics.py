#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

fileLoc ="../Acceptances_PDFReweights_4_19_2015.root"
channels=["MuonChannel", "ElectronChannel"]
histTypes=["weighted_Category_Pt"]
#histTypes=["Category_PtAndLocation"]
outFileDir="../Tables/PDFSystematics/"

pdf_eigenvector_name="cteq66"
num_pdf_eigenvectors=45

def printPDFSystematics():
    file = TFile(fileLoc, 'READ')
    #list = file.GetListOfKeys()
    
    for channel in channels:
        for histType in histTypes:
            # Select Histogram with Expected Values
            # 0 is the Central Value
            print channel+"_"+pdf_eigenvector_name+"_0_PDFEigenvectorReweight_"+histType+"_Acceptances"
            expectedHist = file.Get(channel+"_"+pdf_eigenvector_name+"_0_PDFEigenvectorReweight_"+histType+"_Acceptances")
            print expectedHist.GetName()

            masterDifferencesUpAllEigenvectors=[]
            masterDifferencesDownAllEigenvectors=[]
            # Loop Over Histograms with modified Scale Factor Values
            num_eigenvector_pairs = num_pdf_eigenvectors/2
            print num_eigenvector_pairs
            for eigenpair_index in range(1, num_eigenvector_pairs):
                index_up = 2*eigenpair_index-1
                index_down = 2*eigenpair_index
                histNameUP = channel+"_"+pdf_eigenvector_name+"_"+ str(index_up)+"_PDFEigenvectorReweight_"+histType+"_Acceptances"
                print histNameUP
                histNameDN = channel+"_"+pdf_eigenvector_name+"_"+ str(index_down)+"_PDFEigenvectorReweight_"+histType+"_Acceptances"
                print histNameDN
                
                histUP = file.Get(histNameUP)
                histDN = file.Get(histNameDN)
                
                # Histogram Names
                printh1BinDifference(histUP, expectedHist)
                printh1BinDifference(histDN, expectedHist)

                # Master Euqation
                masterDifferenceUP=[]
                masterDifferenceDN=[]
                differenceUP=h1CalcDifferences(histUP, expectedHist)
                differenceDN=h1CalcDifferences(histDN, expectedHist)
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
                #   printh2BinDifference(hist, expectedHist)
            
            
            print "root sum of squares:"
            print "master differences up"
            print sumInQuadrature(masterDifferencesUpAllEigenvectors)
            print "master differences down"
            print sumInQuadrature(masterDifferencesDownAllEigenvectors)
            
            
    file.Close()


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
        
def printh2BinDifference(h2, h2Expected):
    outfile =open(outFileDir+"BinDifferences_"+h2.GetName()+".html", 'w')
    print "Bins Content:"
    outfile.write(htmlTableHeader)
    output=""
    htmlOutput=""
    
    # Loop Over Rows (Pt)
    for j in range(1, h2.GetNbinsY()+1):
        outfile.write("""<tr align="center">""")
        # Loop Over Columns (Photons' Location)
        for i in range(1, h2.GetNbinsX()+1):
            output = str(h2.GetXaxis().GetBinLowEdge(i))+","+str(h2.GetYaxis().GetBinLowEdge(j))+" : "+ str(format(h2.GetBinContent(i,j),'.3f'))+" pm " + str(format(h2.GetBinError(i,j),'.3f'))
            #print output
            # Bin Content and Errors in HTML format
            htmlOutput = """<td valign="middle">""" + str(format(h2.GetBinContent(i,j)-h2Expected.GetBinContent(i,j),'.4f'))+ """</td>""" 
            outfile.write(htmlOutput)
        outfile.write("""</tr>""")
            
    outfile.write(htmlTableCloser)
    outfile.close()
    
                                                                                                 
    
if __name__=="__main__":
    printPDFSystematics()
