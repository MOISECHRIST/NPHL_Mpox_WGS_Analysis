#!/bin/bash 

##----------------------------------------------------------------------------
##  DQ011155.1,  Clade I,        Zaire (Democratic Republic of the Congo) 1979
##  NC_063383.1, Clade IIb,      Nigeria 08-2018
##  ON563414.3,  Clade IIb,      USA 05-2022
##  MT903344.1,  Clade IIb,      United Kingdom 
##  NC_063383.1 (with B.1 SNPs), lineage-b.1
##-----------------------------------------------------------------------------

# USAGE :
## bash run_nf_core_viralrecon.sh </path/to/datadir> </path/to/outdir> \
#                                 <0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF (default=0)> \
##                                </path/to/reference.fasta (only if the third parameter=1)> </path/to/reference.gff (only if the third parameter=1)>

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "ERROR : Missing parameter(s)"
    echo "USAGE : bash $0 </path/to/datadir> </path/to/outdir> \\"
    echo "                <0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF (default=0)> \\"
    echo "                </path/to/reference.fasta (only if the third parameter=1)> </path/to/reference.gff (only if the third parameter=1)>"
    exit 1
fi

# Input Arguments
DATADIR=$1
OUTDIR=$2
if [ -z "$3" ]; then 
    INPUT_REFSEQ=0
else 
    INPUT_REFSEQ=$3 # 0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF
fi

REFSEQ_FASTA=$4 # Full path to Fasta file containing reference genome for the viral species
REFSEQ_GFF=$5 # Full path to viral GFF annotation file (default: false)

# Constants
REFSEQ_ID='NC_063383.1'
SAMPLE_SHEET="samplesheet.csv"
R1_EXT='_R1_001.fastq.gz'
R2_EXT='_R2_001.fastq.gz'

# Create outdir 
mkdir -p "$OUTDIR"

if [ $INPUT_REFSEQ == "0" ]; then 
    echo "Using pre-configured genome: $REFSEQ_ID"
    PARAMETERS="--genome  $REFSEQ_ID"
elif [ $INPUT_REFSEQ == "1" ]; then
    echo "Using custom reference files."
    if [ -f "$REFSEQ_FASTA" ] && [ -f "$REFSEQ_GFF" ]; then
        PARAMETERS="--fasta $REFSEQ_FASTA --gff $REFSEQ_GFF"
    else 
        echo "reference fasta/gff file not found. Please make sure the file exists..."
        exit 1
    fi
else
    echo "The third parameter can only take 2 values : 0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF"
    exit 1
fi

SCRIPTDIR_PATH=$(cd "$(dirname "$0")"; echo "$PWD")

#Build a sample sheet with : https://raw.githubusercontent.com/nf-core/viralrecon/master/bin/fastq_dir_to_samplesheet.py 
"./$SCRIPTDIR_PATH/fastq_dir_to_samplesheet.py" \
    --read1_extension $R1_EXT \
    --read2_extension $R2_EXT \
    "$DATADIR" "${OUTDIR}/${SAMPLE_SHEET}"

#Launch nf-core/viralrecon on samples
nextflow run nf-core/viralrecon -r 2.6.0 -profile docker \
    --input "${OUTDIR}/${SAMPLE_SHEET}" \
    --outdir $OUTDIR \
    --platform illumina \
    --protocol metagenomic \
    --max_memory '64.GB' --max_cpus 10 \
    --kraken2_variants_host_filter \
    $PARAMETERS

## NOTE : Pour plus d'information sur le genome de reference : https://github.com/nf-core/configs/blob/master/conf/pipeline/viralrecon/genomes.config
