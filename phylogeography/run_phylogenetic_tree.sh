#!/bin/bash 

set -e

# USAGE :
## bash run_phylogenetic_tree.sh </path/to/sequences.fasta> </path/to/reference_genome.fasta> \
##                              </path/to/date_file.(csv|tsv)> </path/to/location_file.(csv|tsv)> \
##                              <time of last sampled tip eg : 2025-05-03> </path/to/outdir>

# REQUIREMENTS 
## conda create -n phylodynamic python=3.7 -y
## conda activate phylodynamic
## conda install -y -c bioconda mafft iqtree 
## conda install -y -c bioconda seqkit
## pip install phylo-treetime

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ]; then
    echo "ERROR : Missing parameter(s)"
    echo "USAGE : bash $0 </path/to/sequences.fasta> </path/to/reference_genome.fasta> \\"
    echo "         </path/to/date_file.(csv|tsv) : with two columns: 'name' and 'date'> \\"
    echo "         </path/to/location_file.(csv|tsv) : with two columns: 'name' and 'country'> \\"
    echo "         <time of last sampled tip eg : 2025-05-03> </path/to/outdir>"
    exit 1
fi

# Input Arguments
INPUT_FASTA="$1"
REFERENCE="$2"
# This requires a date file (tsv or csv) with two columns: 'name' and 'date'
# 'date' format should be YYYY-MM-DD
METADATA="$3"
# This requires a location file (tsv or csv) with two columns: 'name' and 'country'
LOCATION="$4"
OUTDIR="$6"

mkdir -p "$OUTDIR"

echo "#----------------------------#"
echo "#--- Alignment with MAFFT ---#"
echo "#----------------------------#"

mkdir -p "$OUTDIR/mafft"

# Using --auto to choose the best strategy and --add to align to reference
mafft --auto --thread 8 --add "$INPUT_FASTA" "$REFERENCE" > "$OUTDIR/mafft/sequences_aligned.fasta" \
     2> "$OUTDIR/mafft/mafft_alignement.err"

echo "#--------------------------------#"
echo "#---- Phylogeny with IQ-TREE ----#"
echo "#--------------------------------#"

mkdir -p "$OUTDIR/iqtree"

# -m MFP: Best-fit model selection
# -bb 1000: Ultrafast bootstrap for branch support
iqtree -s "$OUTDIR/mafft/sequences_aligned.fasta" \
         -m MFP -bb 1000 -nt AUTO -pre "$OUTDIR/iqtree/MLE_phylogeny"


echo "#---------------------------------------#"
echo "#---- Temporal Dating with TreeTime ----#"
echo "#---------------------------------------#"

if [ -f "$METADATA" ] && [ -f "$LOCATION" ]; then
    treetime clock --tree "$OUTDIR/iqtree/MLE_phylogeny.treefile" \
             --aln "$OUTDIR/mafft/sequences_aligned.fasta" \
             --reroot least-squares \
             --dates "$METADATA" --outdir "$OUTDIR/clock_test" 
    
    OUTLIER_PATH="$OUTDIR/clock_test"
    nb_outlier=$(awk 'END {print NR-1}' "$OUTLIER_PATH/outliers.tsv")

    iteration=0

    while [ "$nb_outlier" -ge 1 ] ; do

        iteration=$(echo "$iteration+1" | bc)
        mkdir -p "$OUTDIR/outliers_cleaning_$iteration/mafft" \
            "$OUTDIR/outliers_cleaning_$iteration/iqtree" \
            "$OUTDIR/outliers_cleaning_$iteration/clock_test"
        
        echo "Outliers detected. Cleaning dataset..."
        
        tail -n+2 "$OUTLIER_PATH/outliers.tsv" | awk '{print $1}' > "$OUTLIER_PATH/outliers.txt"

        seqkit grep -v -f "$OUTLIER_PATH/outliers.txt" "$INPUT_FASTA" \
            > "$OUTDIR/outliers_cleaning_$iteration/sequences_clean.fasta"
        
        grep -v -f "$OUTLIER_PATH/outliers.txt" "$METADATA" \
            > "$OUTDIR/outliers_cleaning_$iteration/metadata_clean.csv"

        INPUT_FASTA="$OUTDIR/outliers_cleaning_$iteration/sequences_clean.fasta"
        METADATA="$OUTDIR/outliers_cleaning_$iteration/metadata_clean.csv"
        
        echo "Re-aligning cleaned sequences for the iteration ($iteration)..."
        mafft --auto --thread 8 --add "$INPUT_FASTA" "$REFERENCE" \
            > "$OUTDIR/outliers_cleaning_$iteration/mafft/sequences_aligned.fasta" \
            2> "$OUTDIR/outliers_cleaning_$iteration/mafft/mafft_alignment.err"
        
        echo "Re-building phylogeny with cleaned data..."
        iqtree -s "$OUTDIR/outliers_cleaning_$iteration/mafft/sequences_aligned.fasta" \
               -m MFP -bb 1000 -nt AUTO \
               -pre "$OUTDIR/outliers_cleaning_$iteration/iqtree/MLE_phylogeny"
        
        treetime clock --tree "${OUTDIR}/outliers_cleaning_${iteration}/iqtree/MLE_phylogeny.treefile" \
             --aln "$OUTDIR/outliers_cleaning_$iteration/mafft/sequences_aligned.fasta" \
             --reroot least-squares \
             --dates "$METADATA" --outdir "$OUTDIR/outliers_cleaning_$iteration/clock_test" 

        OUTLIER_PATH="$OUTDIR/outliers_cleaning_$iteration/clock_test"
        nb_outlier=$(awk 'END {print NR-1}' "$OUTLIER_PATH/outliers.tsv")

    done
    echo "No outliers detected. Using original tree."
    CLEANING_FINAL_PATH=$(dirname "$OUTLIER_PATH")
    
    treetime \
        --tree "$CLEANING_FINAL_PATH/iqtree/MLE_phylogeny.treefile" \
        --aln "$CLEANING_FINAL_PATH/mafft/sequences_aligned.fasta" \
        --dates "$METADATA" \
        --outdir "$OUTDIR/treetime_final"

    treetime mugration \
        --tree "$OUTDIR/treetime_final/timetree.nexus" \
        --states "$LOCATION" --attribute country \
        --outdir "$OUTDIR/mugration"
    
    SCRIPTDIR_PATH=$(cd "$(dirname "$0")"; echo "$PWD")
    LAST_TIP_TIME=$(bash "$SCRIPTDIR_PATH/compute_float_date.sh" "$5")
    python3 "$(dirname "$0")/AncestralChanges.py" --treeFile "$OUTDIR/mugration/annotated_tree.nexus" \
                                --outFile "$OUTDIR/mugration/mugration_results.csv" \
                                --lastDate "$LAST_TIP_TIME"
else
    echo "Metadata file not found. Skipping TreeTime. Create metadata.csv to date your tree."
fi

echo "#---------------------------------------#"
echo "#-------- Analysis Completee -----------#"
echo "#---------------------------------------#"
echo "Results are in $OUTDIR/"
tree -d "$OUTDIR/"