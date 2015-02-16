#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys

from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

#fileLoc ="../Acceptances.root"
#histName="Category_LeadPhotonPt_MuonChannel"
#histName="Category_PtAndLocation_Acceptances_ElectronChannel"
#histName="Acceptances"

fileLoc ="../AnalysisRecoCuts_ScaleFactors_WeightedTotal_CategoryHistograms.root"
histName="Category_PtAndLocation_ElectronChannel"
outFileLoc="/home/cranelli/WGamGam/Acceptances/CMSSW_5_3_12/src/Acceptances/Fiducial/test/Tables/PrintTest.html"
#histName="Category_PtAndLocation_ScaleFactorWeightMuonChannel"

htmlTableHeader=""" <table id="title" border="2" cellspacing="2" cellpadding="3" frame="border" rules="all" summary="summary of table"><tbody> """
htmlTableCloser="</tbody></table></tr>"

def printBinContent():
    file = TFile(fileLoc, 'READ')
    outfile =open(outFileLoc, 'w')
    #printh1BinContent(file, histName)
    printh2BinContent(file, histName, outfile)
    outfile.close()
    file.Close()
    

def printh1BinContent(file, h1Name):
    #hist = TH1F()
    print histName
    h1 = file.Get(h1Name)
    
    output=""
    for i in range(1, h1.GetNbinsX()+1):
        output = str(h1.GetBinLowEdge(i)) +" : " +str(h1.GetBinContent(i))
        print output
        #print h1.GetBinContent(i)

def printh2BinContent(file, h2Name, outfile):
    print h2Name
    print "Bins' Content:"
    h2 = file.Get(h2Name)
    outfile.write(htmlTableHeader)
    output=""
    htmlOutput=""
    #Loop Over Rows
    for i in range(1, h2.GetNbinsX()+1):
        outfile.write("""<tr align="center">""")
        #Loop Over Colums
        for j in range(1, h2.GetNbinsY()+1):
            output = str(h2.GetXaxis().GetBinLowEdge(i))+","+str(h2.GetYaxis().GetBinLowEdge(j))+" : "+ str(format(h2.GetBinContent(i,j),'.3f'))+" pm " + str(format(h2.GetBinError(i,j),'.3f'))
            # Bin Content and Errors in HTML format
            htmlOutput = """<td valign="middle">""" + str(format(h2.GetBinContent(i,j),'.3f'))+""" &plusmn """ + str(format(h2.GetBinError(i,j),'.3f'))+ """</td>""" 
            outfile.write(htmlOutput)
            print output
        outfile.write("""</tr>""")
            
    outfile.write(htmlTableCloser)

    
                                                                                                 
    
if __name__=="__main__":
    printBinContent()
