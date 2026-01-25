# NPHL Mpox WGS Analysis
This script aims to help Cameroon NPHL's Bioinformatic Team in Mpox WGS data analysis in characterisation and tracking this outbreak.
## Usage 

### Launch nf-core/Viralrecon

If you want to identify circulating strains and build a consensus for downstream analyses.

```(bash)
bash run_nf_core_viralrecon.sh </path/to/datadir> </path/to/outdir> \
                                 <0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF (default=0)> \
                                </path/to/reference.fasta (only if the third parameter=1)> </path/to/reference.gff (only if the third parameter=1)>
```
**NOTE :**\
These two lines in `run_nf_core_viralrecon.sh` should be modified if your FASTQ files use different extensions 
```(bash)
R1_EXT='_R1_001.fastq.gz'
R2_EXT='_R2_001.fastq.gz'
```
## Launch Introduction Analysis (Phylodynamic)

To trace the origins of the strains circulating in your country.

```{bash}
bash run_phylogenetic_tree.sh </path/to/sequences.fasta> </path/to/reference_genome.fasta> \
                             </path/to/date_file.(csv|tsv)> </path/to/location_file.(csv|tsv)> \
                             <time of last sampled tip eg : 2025-05-03> </path/to/outdir>
```
