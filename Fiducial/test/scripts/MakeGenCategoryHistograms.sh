#!/bin/bash
#Set up to take the ISR and FSR signal samples, make histograms for each, and make histograms
#for the weighted merger. 
#Example
# ./MakeGenCategoryHistograms.sh /data/users/cranelli/WGamGam/Acceptances/CommonFiducial_Skim/ggNtuples_Skim/job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root /data/users/cranelli/WGamGam/Acceptances/CommonFiducial_Skim/ggNtuples_Skim/job_summer12_Wgg_FSR/job_summer12_LNuGG_FSR_CommonFiducialSkim.root
FILE_ISR=$1
FILE_FSR=$2
echo $FILE_ISR
echo $FILE_FSR

FILENAME_ISR="${FILE_ISR##*/}"
FILENAME_FSR="${FILE_FSR##*/}"
#echo $FILENAME

PREFIX_ISR="${FILENAME_ISR%.*}"
PREFIX_FSR="${FILENAME_FSR%.*}"

SUFFIX=GenCategoryHistograms.root

OUT_ISR=$PREFIX_ISR"_"$SUFFIX
OUT_FSR=$PREFIX_FSR"_"$SUFFIX

echo $PREFIX_ISR
echo $PREFIX_FSR

cd ../../python;

# Make Generator Level Histograms
echo python MakeGenCategoryHistograms.py $FILE_ISR $OUT_ISR
python MakeGenCategoryHistograms.py $FILE_ISR $OUT_ISR

echo python MakeGenCategoryHistograms.py $FILE_FSR $OUT_FSR
python MakeGenCategoryHistograms.py $FILE_FSR $OUT_FSR

cd ../test/scripts

# Merge the ISR and FSR samples together, using their respective weights
echo "python weightAndAddHistograms.py ../CommonFiducialSkim_WAA_ISR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_FSR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"

echo $OUT_FSR | sed 's/FSR/WeightedTotal/'
OUT_WEIGHTED=$(echo $OUT_FSR | sed 's/FSR/WeightedTotal/')
echo $OUT_WEIGHTED

python weightAndAddHistograms.py ../$OUT_ISR ../$OUT_FSR ../$OUT_WEIGHTED





