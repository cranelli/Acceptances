"""histPublish - Makes PNG files out of histograms in results file"""

# Python Module For making PNGs from histograms
# Created by Nicholas Zube
# 8.25.2014

from ROOT import TFile, TCanvas, TImage 
from ROOT import TH1F, TH2F
from ROOT import gDirectory
import htmlTable

def GetKeyNames(self, directory = "" ):
    self.cd(directory)
    return [key.GetName() for key in gDirectory.GetListOfKeys()]

def histToPNG(inRootFileLoc, dirLoc = ""):
    inRootFile = TFile(inRootFileLoc, "READ")
    internalPath = ""
    TFile.GetKeyNames = GetKeyNames
    keyList = inRootFile.GetKeyNames(internalPath)
    
    # Bind ROOT methods before loop to improve performance, so no lookup
    # is required during loop.
    getObj = inRootFile.Get
    img = TImage.Create()
    fromPad = img.FromPad
    writeImage = img.WriteImage
    
    for key in keyList:
        c = TCanvas();
        h = getObj(key)
        h.Draw()
        fromPad(c)
        writeImage(dirLoc + key + ".png")
        
    del getObj
    del fromPad
    del writeImage
    
def makeAcceptanceTable(evEcounts, evMcounts, 
                        outFileName = "acceptTable"):
    outFileName = outFileName + ".txt"
    f = open(outFileName, "w")
    f.write("#\tParticle\tCut\t" + 
            "Events passed\tEvents passed/total\tEfficiency/previous\t" +
            "Events passed\tEvents passed/total\tEfficiency/previous\n")
    part = ["Lep&gamma;&gamma;", 
            "&gamma;", 
            "&gamma;",
            "&mu;", 
            "e", 
            "e", 
            "e"]
    
    cut = ["Common Fiducial Events;", 
           "|&eta;| < 1.47 or > 1.57", 
           "M&gamma;&gamma; > 15",
           "|&eta;| < 2.4", 
           "PT > 30 GeV",
           "|Mass(Z) - Mass(Lep+&gamma;)| > 5 GeV", 
           "|Mass(Z) - Mass(Lep+&gamma;+&gamma;)| > 5 GeV"]
    for i in xrange(len(evEcounts)):
        if i == 0:
            f.write(" \t \t \t" + "Electron channel\t \t \t" +
                    "Muon channel\t \t\n")
        f.write(str(i) + "\t")
        f.write(part[i] + "\t")
        f.write(cut[i] + "\t")
        f.write(str(evEcounts[i]) + "\t")
        f.write(str(round(float(evEcounts[i])/evEcounts[0],5)) + "\t")
        if(i>0 and evEcounts[i-1] > 0): 
            f.write(str(round(float(evEcounts[i])/evEcounts[i-1],3))+"\t")
        else: f.write("-\t")
        if i >= 0 and i < 4:
            f.write(str(evMcounts[i]) + "\t")
            f.write(str(round(float(evMcounts[i])/evMcounts[0],5)) + "\t")
            if(i>0  and evMcounts[i-1] > 0): 
                f.write(str(round(float(evMcounts[i])/evMcounts[i-1],3)))
            else: f.write("-")
        else:
            f.write("-\t-\t-")
        f.write("\n")   
    f.close()              
    tab = htmlTable.HTMLTable(len(evEcounts)+2, 9)
    tab.BuildFromFile(outFileName)
    
