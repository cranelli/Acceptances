#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

fileLoc ="../Acceptances.root"
channels=["MuonChannel_ScaleFactorWeight", "ElectronChannel_ScaleFactorWeight"]
histTypes=["Category_PtAndLocation"]

outFileDir="../Tables/Acceptances_SystErrors/"

Header= " \n"

def printSystematics():
    file = TFile(fileLoc, 'READ')
    list = file.GetListOfKeys()
    
    for channel in channels:
        for histType in histTypes:
            # Select Histogram with Expected Values
            expectedHist = file.Get(channel+"_"+histType+"_Acceptances")
            print expectedHist.GetName()
            outfileUP =open(outFileDir+"SystErrorsUP_"+expectedHist.GetName()+".dat", 'w')
            outfileDN =open(outFileDir+"SystErrorsDN_"+expectedHist.GetName()+".dat", 'w')
            # Store the Difference Systematics Together in a Dictionairy
            differencesUP=dict()
            differencesDN=dict()
            # Loop Over Histograms with modified Scale Factor Values
            for key in list:
                histName = key.GetName()
                if channel+"_"+histType in histName:
                    print histName
                    hist = file.Get(histName)
                    if hist.ClassName() == "TH1F":
                        # Histogram Names
                        printh1BinDifference(hist, expectedHist)
                    elif hist.ClassName() == "TH2F":
                        #printh2BinDifference(hist, expectedHist)
                        if "UP" in histName:
                            differencesUP[histName]=h2CalcDifferences(hist, expectedHist)
                        elif "DN" in histName:
                            differencesDN[histName]=h2CalcDifferences(hist, expectedHist)
                    else:
                        print "This type of Class Not Supported for Printing Bin Content"
            #Differences Up
            outputUP=""
            for key in differencesUP:
                print key
            # print differencesUP[key]
            systematicsUP= sumInQuadrature(differencesUP)
            for systematicUP in systematicsUP:
                outputUP+=str(format(systematicUP, '.6f')).rjust(10)
            outfileUP.write(outputUP)
            # print sumInQuadrature(differencesUP)
            
            # Differences Down
            outputDN=""
            for key in differencesDN:
                print key
            #    print differencesDN[key]
            systematicsDN= sumInQuadrature(differencesDN)
            for systematicDN in systematicsDN:
                outputDN+=str(format(systematicDN, '.6f')).rjust(10)
            outfileDN.write(outputDN)
            # print sumInQuadrature(differencesDN)
            outfileUP.close()
            outfileDN.close()
    file.Close()

# Sum the differences, for each list of differences in the Dictionairy. 
def sumInQuadrature(differencesDict):
    sumdif2=[]
    for key in differencesDict:
        differences = differencesDict[key]
        for i in range(len(differences)):
            if len(sumdif2) != len(differences) :
                sumdif2.insert(i, differences[i] **2)
            else:
                sumdif2[i] += differences[i] **2
    #Than take the square root of each element
    rootsumdif2=[]
    for i in range(len(sumdif2)):
        rootsumdif2.insert(i, sumdif2[i] **0.5)
    return rootsumdif2
    

# For a two 1D Histograms, prints the differences of the bin contents
def printh1BinDifference(h1, h1Expected):
    #hist = TH1F()
    output=""
    for i in range(1, h1.GetNbinsX()+1):
        output = str(h1.GetBinLowEdge(i)) +" : " +str(h1.GetBinContent(i)-h1Expected.GetBinContent(i))
        #print output
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
    printSystematics()
