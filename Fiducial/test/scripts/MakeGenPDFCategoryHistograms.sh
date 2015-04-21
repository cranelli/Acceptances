#!/bin/bash
#Set up to take the ISR and FSR signal samples, make reco histograms for each, and make histograms
#for the weighted merger. 
#Example (should end in /)
# ./MakeGenPDFCategoryHistograms.sh /data/users/cranelli/WGamGam/Acceptances/CommonFiducial_wMT_Skim_PDFReweights/

SKIM_PATH=$1
SKIM_NAME=${SKIM_PATH%?} #Removes Last Character, should be a '/'

SKIM_NAME="${SKIM_NAME##*/}" 


SUFFIX="GenCategoryHistograms.root"

ISR_DIR="job_summer12_WAA_ISR/"
FSR_DIR="job_summer12_Wgg_FSR/"

ROOT_NAME="tree.root"

FILE_ISR=$SKIM_PATH$ISR_DIR$ROOT_NAME
FILE_FSR=$SKIM_PATH$FSR_DIR$ROOT_NAME


OUT_ISR=$SKIM_NAME"_ISR_"$SUFFIX
OUT_FSR=$SKIM_NAME"_FSR_"$SUFFIX


cd ../../python;

# Make Generator Level Histograms
echo python MakeGenPDFReweightCategoryHistograms.py $FILE_ISR $OUT_ISR
python MakeGenPDFReweightCategoryHistograms.py $FILE_ISR $OUT_ISR

echo python MakeGenPDFReweightCategoryHistograms.py $FILE_FSR $OUT_FSR
python MakeGenPDFReweightCategoryHistograms.py $FILE_FSR $OUT_FSR

cd ../test/scripts

# Merge the ISR and FSR samples together, using their respective weights

#echo $OUT_FSR | sed 's/FSR/WeightedTotal/'
OUT_WEIGHTED=$(echo $OUT_FSR | sed 's/FSR/WeightedTotal/')
#echo $OUT_WEIGHTED
echo python weightAndAddHistograms.py ../$OUT_ISR ../$OUT_FSR ../$OUT_WEIGHTED
python weightAndAddHistograms.py ../$OUT_ISR ../$OUT_FSR ../$OUT_WEIGHTED





