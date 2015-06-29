#!/bin/bash

HIST_DIR=/Users/Chris/CMS/WGamGam/Acceptances/Fiducial/test/Histograms/NLO_LepGammaGammaFinalElandMu_2015_6_26_ScaleFactors_PDFReweights/

echo python MakeScaleFactorSystematicHistograms.py $HIST_DIR
python MakeScaleFactorSystematicHistograms.py $HIST_DIR

echo python MakePileUpSystematicHistograms.py $HIST_DIR
python MakePileUpSystematicHistograms.py $HIST_DIR

echo python MakePDFSystematicHistograms.py $HIST_DIR
python MakePDFSystematicHistograms.py $HIST_DIR

echo python MakeFactorizationRenormalizationSystematicHistograms.py $HIST_DIR
python MakeFactorizationRenormalizationSystematicHistograms.py $HIST_DIR



