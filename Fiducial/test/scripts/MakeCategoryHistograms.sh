#!/bin/bash

cd ../../python;

# Make Generator Level Histograms
python MakeGenCategoryHistograms.py job_summer12_WAA_ISR/ggtree_mc_ISR_CommonFiducialSkim.root CommonFiducialSkim_WAA_ISR_CategoryHistograms.root
python MakeGenCategoryHistograms.py job_summer12_Wgg_FSR/job_summer12_LNuGG_FSR_CommonFiducialSkim.root CommonFiducialSkim_Wgg_FSR_CategoryHistograms.root

cd ../test/scripts

# Merge the ISR and FSR samples together, using their respective weights
echo "python weightAndAddHistograms.py ../CommonFiducialSkim_WAA_ISR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_FSR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root"

python weightAndAddHistograms.py ../CommonFiducialSkim_WAA_ISR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_FSR_CategoryHistograms.root ../CommonFiducialSkim_Wgg_WeightedTotal_CategoryHistograms.root

# Make RECO Level Histograms - Loop Over the Root Files with the Different Skimming Cuts

for skim_name in AnalysisRecoCuts_LepGammaGammaNoPHID_ScaleFactors
#AnalysisRecoCuts_ScaleFactors  AnalysisRecoCuts_NoPixelVetoFilter_ScaleFactors AnalysisRecoCuts_NoMggFilter_ScaleFactors
do
  cd ../../python
  python MakeRecoCategoryHistograms.py $skim_name"_WAA_ISR.root" $skim_name"_WAA_ISR_CategoryHistograms.root"
  python MakeRecoCategoryHistograms.py $skim_name"_Wgg_FSR.root" $skim_name"_Wgg_FSR_CategoryHistograms.root"
  cd ../test/scripts

  # Merge the ISR and FSR samples together, using their respective weights
  echo "python weightAndAddHistograms.py ../"$skim_name"_WAA_ISR_CategoryHistograms.root" "../"$skim_name"_Wgg_FSR_CategoryHistograms.root" "../"$skim_name"_WeightedTotal_CategoryHistograms.root" 
  python weightAndAddHistograms.py "../"$skim_name"_WAA_ISR_CategoryHistograms.root" "../"$skim_name"_Wgg_FSR_CategoryHistograms.root" "../"$skim_name"_WeightedTotal_CategoryHistograms.root" 

done




