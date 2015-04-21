#!/bin/bash
#Set up to take the ISR and FSR signal samples, make histograms for each, and make histograms
#for the weighted merger. 
#Example
# ./MakeRecoCategoryHistograms.sh /data/users/cranelli/WGamGam/Acceptances/AnalysisRECOCuts_Skim/LepGammaGammaNoPhID_2015_3_31_ScaleFactors/LepGammaGammaNoPhID_ISR_ScaleFactors.root /data/users/cranelli/WGamGam/Acceptances/AnalysisRECOCuts_Skim/LepGammaGammaNoPhID_2015_3_31_ScaleFactors/LepGammaGammaNoPhID_FSR_ScaleFactors.root
# 
FILE_ISR=$1
FILE_FSR=$2
echo $FILE_ISR
echo $FILE_FSR

FILENAME_ISR="${FILE_ISR##*/}"
FILENAME_FSR="${FILE_FSR##*/}"
#echo $FILENAME

PREFIX_ISR="${FILENAME_ISR%.*}"
PREFIX_FSR="${FILENAME_FSR%.*}"

SUFFIX=RecoCategoryHistograms.root

OUT_ISR=$PREFIX_ISR"_"$SUFFIX
OUT_FSR=$PREFIX_FSR"_"$SUFFIX

echo $PREFIX_ISR
echo $PREFIX_FSR

cd ../../python;

# Make Generator Level Histograms
echo python MakeRecoCategoryHistograms.py $FILE_ISR $OUT_ISR
python MakeRecoCategoryHistograms.py $FILE_ISR $OUT_ISR

echo python MakeRecoCategoryHistograms.py $FILE_FSR $OUT_FSR
python MakeRecoCategoryHistograms.py $FILE_FSR $OUT_FSR

cd ../test/scripts

# Merge the ISR and FSR samples together, using their respective weights

echo $OUT_FSR | sed 's/FSR/WeightedTotal/'
OUT_WEIGHTED=$(echo $OUT_FSR | sed 's/FSR/WeightedTotal/')
echo $OUT_WEIGHTED
echo python weightAndAddHistograms.py ../$OUT_ISR ../$OUT_FSR ../$OUT_WEIGHTED
python weightAndAddHistograms.py ../$OUT_ISR ../$OUT_FSR ../$OUT_WEIGHTED





