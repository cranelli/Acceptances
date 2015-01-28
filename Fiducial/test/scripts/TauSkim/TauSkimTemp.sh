#!/bin/bash

STARTRANGE=`echo $1`
STOPRANGE=`echo $2`
INFILEPREFIX=`echo $3`
PART=`echo $4`

cat ./TauSkim_Condor.jdl \
| sed -e s/STARTRANGE/${STARTRANGE}/ \
| sed -e s/STOPRANGE/${STOPRANGE}/ \
| sed -e s/INFILENAME/${INFILEPREFIX}.root/ \
| sed -e s/OUTFILENAME/${INFILEPREFIX}_TauSkim_${PART}.root/ \
> TauSkim_Condor_${FILENAME}.jdl

condor_submit TauSkim_Condor_${FILENAME}.jdl
