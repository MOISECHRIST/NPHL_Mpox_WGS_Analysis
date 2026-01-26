#!/bin/bash

set -e

if [ -z "$1" ] && [ -z "$2" ]; then
    echo "ERROR : Missing parameter"
    echo "USAGE : $0 </path/to/sequences_file.fasta> </path/to/outdir>"
    exit 1
fi

#Parameters
INPUT_SEQ="$1"
OUTDIR="$2"
CURRENT_DATE=$(date "+%Y-%M-%d")

#Constants 
NEXTSTRAIN_DB='nextstrain/mpox/all-clades'
NEXTSTRAIN_DB_PATH='data/nextstrain/mpox/all-clades'

if [ ! -d "${NEXTSTRAIN_DB_PATH}_${CURRENT_DATE}" ]; then 
    #Download/Update nexclade data base for mpox/all-clades
    nextclade dataset get \
    --name  "$NEXTSTRAIN_DB"\
    --output-dir "${NEXTSTRAIN_DB_PATH}_${CURRENT_DATE}"
else
    echo "The Database available on : $PWD/${NEXTSTRAIN_DB_PATH}_${CURRENT_DATE}"
fi

#And then run nexclade on Cameroon's hcov sequences 
nextclade run --verbose \
    --input-dataset "${NEXTSTRAIN_DB_PATH}_${CURRENT_DATE}" \
    --output-csv "$OUTDIR/mpox_nextclade_results.csv" \
    "$INPUT_SEQ"