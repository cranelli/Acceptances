#!/bin/bash

#Support Scripts are located in CommonFiducialSkim
cd CommonFiducialSkim/

inFilePrefix="ggtree_mc_ISR"

# ISR Runs
./CommonFiducialSkimTemp.sh 0 200000 ${inFilePrefix} part1
./CommonFiducialSkimTemp.sh 200000 400000 ${inFilePrefix} part2
./CommonFiducialSkimTemp.sh 400000 600000 ${inFilePrefix} part3
./CommonFiducialSkimTemp.sh 600000 800000 ${inFilePrefix}  part4
./CommonFiducialSkimTemp.sh 800000 -1 ${inFilePrefix}  part5

inFilePrefix="job_summer12_LNuGG_FSR"
# FSR Runs
./CommonFiducialSkimTemp.sh 0 200000 ${inFilePrefix} part1
./CommonFiducialSkimTemp.sh 200000 400000 ${inFilePrefix} part2
./CommonFiducialSkimTemp.sh 400000 600000 ${inFilePrefix} part3
./CommonFiducialSkimTemp.sh 600000 800000 ${inFilePrefix}  part4
./CommonFiducialSkimTemp.sh 800000 -1 ${inFilePrefix}  part5
