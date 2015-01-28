#!/bin/bash

inFilePrefix="ggtree_mc_ISR"

#Support Scripts are in TauSkim/ directory.
cd TauSkim/

# ISR Runs
./TauSkimTemp.sh 0 250000 ${inFilePrefix} part1
./TauSkimTemp.sh 250000 500000 ${inFilePrefix} part2
./TauSkimTemp.sh 500000 750000 ${inFilePrefix} part3
./TauSkimTemp.sh 750000 -1 ${inFilePrefix}  part4

inFilePrefix="job_summer12_LNuGG_FSR"
# FSR Runs
./TauSkimTemp.sh 0 250000 ${inFilePrefix} part1
./TauSkimTemp.sh 250000 500000 ${inFilePrefix} part2
./TauSkimTemp.sh 500000 750000 ${inFilePrefix} part3
./TauSkimTemp.sh 750000 -1 ${inFilePrefix}  part4
