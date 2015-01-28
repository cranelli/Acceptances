#!/bin/bash

STARTRANGE=`echo $1`
STOPRANGE=`echo $2`
INFILEPREFIX=`echo $3`
PART=`echo $4`

TEMPJDLFILE=Condor_CommonFiducialSkim_Condor_${INFILEPREFIX}_${PART}_.jdl

cat ./CommonFiducialSkim_Condor.jdl \
| sed -e s/STARTRANGE/${STARTRANGE}/ \
| sed -e s/STOPRANGE/${STOPRANGE}/ \
| sed -e s/INFILENAME/${INFILEPREFIX}.root/ \
| sed -e s/OUTFILENAME/${INFILEPREFIX}_CommonFiducialSkim_${PART}.root/ \
> $TEMPJDLFILE

condor_submit $TEMPJDLFILE
