# NPHL Mpox WGS Analysis
This script aims to help Cameroon NPHL's Bioinformatic Team in Mpox WGS data analysis in characterisation and tracking this outbreak.

## Usage 

### Launch nf-core/Viralrecon

If you want to identify circulating strains and build a consensus for downstream analyses.

``` bash
#Move into the viralrecon_MPOX directory
cd viralrecon_MPOX

#Launch the script 
bash run_nf_core_viralrecon.sh </path/to/datadir> </path/to/outdir> \
                                 <0 = Use built-in REFSEQ_ID, 1 = Provide custom FASTA/GFF (default=0)> \
                                </path/to/reference.fasta (only if the third parameter=1)> </path/to/reference.gff (only if the third parameter=1)>
```

**NOTE :**\
These two lines in `run_nf_core_viralrecon.sh` should be modified if your FASTQ files use different extensions.

``` bash
R1_EXT='_R1_001.fastq.gz'
R2_EXT='_R2_001.fastq.gz'
```

### Phylogeography 

#### REQUIREMENTS

``` bash
cd phylogeography
conda env create -f environment.yml
```

#### Launch Introduction Analysis

To trace the origins of the strains circulating in your country.

``` bash
#Move into the phylogeography directory
cd phylogeography

#Activate the environment 
conda activate phylodynamic

#Launch the script
bash run_phylogenetic_tree.sh </path/to/sequences.fasta> </path/to/reference_genome.fasta> \
                             </path/to/date_file.(csv|tsv)> </path/to/location_file.(csv|tsv)> \
                             <time of last sampled tip eg : 2025-05-03> </path/to/outdir>
```

#### Plot Migrations on a Map 

``` bash
#Activate the environment 
conda activate phylodynamic

#final_DataViz.py Usage
python final_DataViz.py -h

usage: final_DataViz.py [-h] --migration MIGRATION --pointsGeoloc POINTSGEOLOC [--origins ORIGINS [ORIGINS ...]] [--destinations DESTINATIONS [DESTINATIONS ...]]

final_DataViz.py : This script allow user to vizualise the introductions found with AncestralChanges.py script.

options:
  -h, --help            show this help message and exit
  --migration MIGRATION, -m MIGRATION
                        Path to the AncestralChanges.py result csv file. Filewith columns : 'Origin', 'Destination','EventTime'
  --pointsGeoloc POINTSGEOLOC, -p POINTSGEOLOC
                        path to the csv file containing the geolication of each location in AncestralChanges.py result csv file. File with columns : 'location', 'long', and 'lat'.
  --origins ORIGINS [ORIGINS ...], -o ORIGINS [ORIGINS ...]
                        Optional list of origin locations separated by white space to filter the plot (e.g., --origins South Center).
  --destinations DESTINATIONS [DESTINATIONS ...], -d DESTINATIONS [DESTINATIONS ...]
                        Optional list of destination locations separated by white space to filter the plot (e.g., --destinations Center North-West).
```

