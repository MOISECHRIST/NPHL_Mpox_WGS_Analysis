#!/bin/bash

if [ -z "$1" ]; then
    echo "ERROR : Missing parameter"
    echo "USAGE : $0 YYYY-MM-DD"
    exit 1
fi

INPUT_DATE=$1

OS_NAME=$(uname -s)
if [ $OS_NAME == "Linux" ]; then
    YEAR=$(date -d "$INPUT_DATE" "+%Y")
    DAY_OF_YEAR=$(date -d "$INPUT_DATE" "+%j")
elif [ $OS_NAME == "Darwin" ]; then 
    YEAR=$(date -j -f "%Y-%m-%d" "$INPUT_DATE" "+%Y")
    DAY_OF_YEAR=$(date -j -f "%Y-%m-%d" "$INPUT_DATE" "+%j")
fi

# Déterminer si l'année est bissextile (365 ou 366 jours)
if (( ($YEAR % 4 == 0 && $YEAR % 100 != 0) || ($YEAR % 400 == 0) )); then
    DAY_IN_YEAR=366
else
    DAY_IN_YEAR=365
fi

# Calcul de la version décimale avec 10 chiffres de précision
# Formule : Année + (Jour_de_l_année / Nombre_total_de_jours)
DECIMAL=$(echo "scale=10; $YEAR + ($DAY_OF_YEAR / $DAY_IN_YEAR)" | bc -l)

echo $DECIMAL