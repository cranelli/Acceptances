#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext

fileLoc ="../Acceptances.root"
histName="MuonChannel_Acceptances_ScaleFactorWeight_Category_PtAndLocation"
#histName="Category_PtAndLocation_Acceptances_ElectronChannel"
#histName="Acceptances"

#fileLoc ="../AnalysisRecoCuts_ScaleFactors_WeightedTotal_CategoryHistograms.root"
#histName="ElectronChannel_Category_PtAndLocation"

outFileDir="../Tables/Acceptances"

htmlTableHeader=""" <table id="title" border="2" cellspacing="2" cellpadding="3" frame="border" rules="all" summary="summary of table"><tbody> """
htmlTableCloser="</tbody></table></tr>"

def printBinContent():
    file = TFile(fileLoc, 'READ')
    list = file.GetListOfKeys()
    for key in list:
        histName = key.GetName()
        print histName
        hist = file.Get(histName)
        if hist.ClassName() == "TH1F":
            printh1BinContent(hist)
        elif hist.ClassName() == "TH2F":
            printh2BinContent(hist)
        else:
            print "This type of Class Not Supported for Printing Bin Content"
        
    #printh1BinContent(file, histName)
    #printh2BinContent(file, histName, outfile)
    file.Close()
    

def printh1BinContent(h1):
    #hist = TH1F()
    output=""
    for i in range(1, h1.GetNbinsX()+1):
        output = str(h1.GetBinLowEdge(i)) +" : " +str(h1.GetBinContent(i))
        print output
        #print h1.GetBinContent(i)

def printh2BinContent(h2):
    outfile =open(outFileDir+"BinContent_"+h2.GetName()+".html", 'w')
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
            print output
            # Bin Content and Errors in HTML format
            htmlOutput = """<td valign="middle">""" + str(format(h2.GetBinContent(i,j),'.3f'))+""" &plusmn """ + str(format(h2.GetBinError(i,j),'.3f'))+ """</td>""" 
            outfile.write(htmlOutput)
            
        outfile.write("""</tr>""")
            
    outfile.write(htmlTableCloser)
    outfile.close()
    
                                                                                                 
    
if __name__=="__main__":
    printBinContent()
