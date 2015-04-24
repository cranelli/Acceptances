#Python Code for looking at the Histograms in a root
#file, and printing the content of each bin.

import sys
from ROOT import TFile
from ROOT import TH1F
#from decimal import getcontext


fileLoc ="../Histograms/CommonFiducial_wMT_Skim/CommonFiducial_wMT_Skim_PDFReweights_WeightedTotal_GenCategoryHistograms.root"

outFileDir="../Histograms/CommonFiducial_wMT_Skim/BinContent/"

Header= " \n"

#Loops over histograms in a file, and writes out the bin contents in table formatted txt files.
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
    file.Close()
    

# Writing out a 1D Histogram.  X axis is rows.
def printh1BinContent(h1):
    outfile =open(outFileDir+"BinContent_"+h1.GetName()+".dat", 'w')
    #outfile.write(Header)
    output=''
    for x in range(1, h1.GetNbinsX()+1):
        
        output += str(h1.GetBinLowEdge(x))+ '-' + str(h1.GetBinLowEdge(x+1)) +':'
        output += str(format(h1.GetBinContent(x), '.6f')).rjust(10)
        output += '\n'
    outfile.write(output)
    outfile.close()


# Writing out a 2D Histogram. Y Axis is row X axis is Columns
def printh2BinContent(h2):
    outfile =open(outFileDir+"BinContent_"+h2.GetName()+".dat", 'w')
    print "Bins Content of " + h2.GetName()
    
    outfile.write(Header)
    
    # Write Row with Column Values
    colVals="".ljust(12)
    for x in range(1, h2.GetNbinsX()+1):
        colVals += (str(h2.GetXaxis().GetBinLowEdge(x))+ "-" + str(h2.GetXaxis().GetBinLowEdge(x+1))).rjust(10)
    colVals += "\n"
    outfile.write(colVals)
    
    # Loop Over Rows (Pt)
    output =""
    for y in range(1, h2.GetNbinsY()+1):
        output += (str(h2.GetYaxis().GetBinLowEdge(y))+ '-' + str(h2.GetYaxis().GetBinLowEdge(y+1)) +':').ljust(12)
        # Loop Over Columns (Photons' Location)
        for x in range(1, h2.GetNbinsX()+1):
            output += str(format(h2.GetBinContent(x,y), '.4f').rjust(10))
        
        output += '\n'

    outfile.write(output)
    outfile.close()
    
                                                                                                 
    
if __name__=="__main__":
    printBinContent()
