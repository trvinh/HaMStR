# HaMStR-OneSeq

Table of Contents
=================

   * [HaMStR-OneSeq](#hamstr-oneseq)
      * [How to install](#how-to-install)
         * [0. Basic system tools requirement](#0-basic-system-tools-requirement)
         * [1a. Install in Ubuntu/MacOS](#1a-install-in-ubuntumacos)
         * [1b. Install using Anaconda](#1b-install-using-anaconda)
      * [Usage](#usage)
      * [HaMStR and the utilisation of FAS](#hamstr-and-the-utilisation-of-fas)
      * [Output visualization using PhyloProfile](#output-visualization-using-phyloprofile)
      * [Pre-calculated data set](#pre-calculated-data-set)
      * [Dependencies](#dependencies)
         * [System tools/libraries](#system-toolslibraries)
         * [Bioinformatics tools](#bioinformatics-tools)
         * [Perl modules](#perl-modules)
      * [How to cite](#how-to-cite)
      * [Contact](#contact)

## How to install

### 0. Basic system tools requirement
You need to have `wget`, `grep` and `sed` (or `gsed` for **MacOS**) to install HaMStR. So please install them if they are missing. For MacOS users, we recommend using [Homebrew](https://brew.sh) to install those command line tools.

### 1a. Install in Ubuntu/MacOS

Get HaMStR source code from GitHub
```
git clone --depth=1 https://github.com/BIONF/HaMStR
```

Run `setup.sh` script in the HaMStR/bin folder to install HaMStR and its dependencies
```
cd HaMStR
bin/setup.sh
```
*Enter root password if required (some dependencies need root privileges to be installed. See [dependency list](#dependencies) for more info.)*

After the setup run successfully, you can start using HaMStR (in some cases you should restart the terminal).

### 1b. Install using Anaconda

Follow [this link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) to install conda (anaconda or miniconda) to your system.

Add additional channels [bioconda](https://bioconda.github.io/) and [conda-forge](https://conda-forge.org/):
```
conda config --add channels bioconda
conda config --add channels conda-forge
```

Create and activate a conda environment for HaMStR
```
conda create --name hamstr -y
conda activate hamstr
```

Install HaMStR
```
conda install -c trvinh hamstr
setup_hamstr
```

After the setup run successfully, you can start using HaMStR (in some cases you should restart the terminal).

*For debugging the installation, please create a log file by running the setup as e.g. `bin/setup.sh | tee log.txt` for Linux/MacOS or `setup_hamstr | tee log.txt` for Anaconda and send us that log file, so that we can trouble shoot the issues. Most of the problems can be solved by just re-running the setup.*

## Usage
HaMStR will run smoothly with the provided sample input file in 'HaMStR/data/infile.fa' if everything is set correctly.
```
perl oneSeq.pl -seqFile=infile.fa -seqid=P83876 -refspec=HUMAN@9606@1 -minDist=genus -maxDist=kingdom -coreOrth=5 -cleanup -global
```
You can have an overview about the available options with the command
```
perl oneSeq.pl -h
```
The output orthologous group for the query gene consist of these text files
1) `seqname.extended.fa`: a multiple FASTA file containing ortholog sequences and the query gene
2) `seqname.extended.profile`: a tab-delimited file containing list of orthologous sequences and their correspoding similarity scores by comparing their feature architectures with the one of the query gene (for more info about this score, please read [this document](https://bionf.github.io/FAS))
3) `seqname.phyloprofile`: an input file for visualisation the phylogenetic profile of the query gene using [PhyloProfile tool](https://github.com/BIONF/phyloprofile)
4) `seqname_1.domains` (and optional, `seqname_0.domains`): a protein domain annotation file for all the sequences present in the orthologous group. The `_0` or `_1` suffix indicates the direction of the feature architecture comparison, in which `_1` (forward) means that the query gene is used as *seed* and it orthologs as *target* for the comparison, while `_0` (backward) is vice versa.

## HaMStR and the utilisation of FAS
HaMStR integrates the prediction of orthologs and the calculation of the Feature Architecture Similarty (FAS) scores. FAS scores are computed pairwise between the query gene and it's predicted orthologous genes using [FAS tool](https://github.com/BIONF/FAS), which will be automatically installed during the setup of HaMStR.

## Output visualization using PhyloProfile
For a rich visualisation of the provided information from the HaMStR outputs, you can plug them into the [Phyloprofile tool](https://github.com/BIONF/phyloprofile).

The main input file for *PhyloProfile* is `seqname.phyloprofile`, which contains list of all orthologous gene names and the taxonomy IDs of their taxa together with the FAS scores (if available). For analysing more information such as the FASTA sequences or the domain annotations, you can optionally input `seqname.extended.fa` and `seqname_1.domains` (or `seqname_0.domains`) to *PhyloProfile*.

You can combine multiple HaMStR runs into a single phylogenetic profile input for data visualisation and data exploration. Each run is identified by the given seqname (opt -seqname=<>). This is either given by the user or randomly assigned. The following steps are necessary:

```
# concatenate all desired profile files into one combined profile

cat *.extended.profile > combined.extended.profile

# re-run the parsing script from your current data directory with the combined profile

perl /path/to/HaMStR/bin/visuals/parseOneSeq.pl -i combined.extended.profile -o combined.phyloprofile
```

To prepare the additional input file (*.domains) you just need to concatenate them with each other (please mind the distinction between forward (1) and backward (0) FAS comparisons and do not mix them up).

```
cat *_0.domains > combined_0.domains
cat *_1.domains > combined_1.domains
```

The resulting file `combined.phyloprofile`, `combined_0.matrix` and `combined_1.domains` can be then plugged into the *Phyloprofile tool* for further investigation.


## Pre-calculated data set

Within the data package (https://fasta.bioch.virginia.edu/fasta_www2/fasta_list2.shtml) we provide a set of 78 reference taxa (gene sets in genome_dir, annotations in weight_dir, blast databases in blast_dir). They can be automatically downloaded with the `setup.sh` script. This data comes "ready to use" with the HaMStR-OneSeq framework. Species data must be present in the three directories listed below. For each species/taxon there is a sub-directory named in accordance to the naming schema ([Species acronym]@[NCBI ID]@[Proteome version]).:

* genome_dir (Contains sub-directories for proteome fasta files for each species)
* blast_dir (Contains sub-directories for BLAST databases made with makeblastdb out of your proteomes)
* weight_dir (Contains sub-directories for feature annotation files for each proteome)


However, if needed the user can manually add further gene sets (multifasta format) and place them into the respective directories (genome_dir, weight_dir, blast_dir). Please note, that every taxon/species must be present in the NCBI taxonomy. The following steps need to be conducted:

1) Download the gene set of your taxon of interest as amino acid sequences from the NCBI database.

2) Rename the file in accordance to the naming schema of hamstr:     SPECIES@12345@1.fa ([Species acronym]@[NCBI ID]@[Proteome version])

3) Fasta header must be whitespace free and unique within the gene set (short header make your life easier for downstream analysis).
     - the following bash command uses sed to cut the header at the first whitespace: sed -i "s/ .*//" SPECIES@12345@1.fa
     - example:

before:

	>EXR66326.1 biofilm-associated domain protein, partial [Acinetobacter baumannii 339786]
	MTGEGPVAIHAEAVDAQGNVDVADADVTLTIDTTPQDLITAITVPEDLNGDGILNAAELGTDGSFNAQVALGPDAVDGTV
	VNVNGTNYTVTAADLANGYITATLDATAADPVTGQIVIHAEAVDAQGNVD
	>EXR66351.1 hypothetical protein J700_4015, partial [Acinetobacter baumannii 339786]
	NRRLLITTQPTATDSNYKTPIYINAPNGELYFANQDETSVSSVVFKRVIGATAANAPYVASDSWTKKIRKWNTYNHEVSK
	VGRFIAPMMLTYDVTFTTQQNNAGWSISKESTGVYRLQRDSGVTTELANPHIEVSGIFAGTGLGSGDVILPPTLQAIEAY
	>EXR66376.1 bacterial Ig-like domain family protein, partial [Acinetobacter baumannii 339786]
	DGVDYPAVNNGDGTWTLADNTLPTLADGPHTITVTATDAAGNVGNDTAVVTIDTVAPNAPVLDPINATDPVSGQAEPGST
	VTVTYPDGTTATVVAGTDGSWSVPNPGNLVDGDTVTATAT
	...
after (this is how your sequence data should look like):

	>EXR66326.1
	MTGEGPVAIHAEAVDAQGNVDVADADVTLTIDTTPQDLITAITVPEDLNGDGILNAAELGTDGSFNAQVALGPDAVDGTV
	VNVNGTNYTVTAADLANGYITATLDATAADPVTGQIVIHAEAVDAQGNVD
	>EXR66351.1
	NRRLLITTQPTATDSNYKTPIYINAPNGELYFANQDETSVSSVVFKRVIGATAANAPYVASDSWTKKIRKWNTYNHEVSK
	VGRFIAPMMLTYDVTFTTQQNNAGWSISKESTGVYRLQRDSGVTTELANPHIEVSGIFAGTGLGSGDVILPPTLQAIEAY
	>EXR66376.1
	DGVDYPAVNNGDGTWTLADNTLPTLADGPHTITVTATDAAGNVGNDTAVVTIDTVAPNAPVLDPINATDPVSGQAEPGST
	VTVTYPDGTTATVVAGTDGSWSVPNPGNLVDGDTVTATAT

4) After your gene set (proteomic data) is prepared and placed into the respective sub-directory in the genome_dir directory you can conduct the following instructions:

5.1) Create a Blast DB for the species within the blast_dir

	makeblastdb -dbtype prot -in genome_dir/SPECI@00001@1/SPECI@00001@1.fa -out blast_dir/SPECI@00001@1/SPECI@00001@1

5.2) Create a symbolic link with the blast_dir (change into the respective sub-directory in the blast_dir)

	cd blast_dir/SPECI@00001@1
	ln -s ../../genome_dir/SPECI@00001@1/SPECI@00001@1.fa SPECI@00001@1.fa

6) Create the annotation files for your taxon with the provided perl script

	perl /path/to/your/hamstr/bin/fas/annotation.pl -fasta=/path/to/your/hamstr/genome_dir/SPECI@00001@1/SPECI@00001@1.fa -path=/path/to/your/hamstr/weight_dir -name=SPECI@00001@1

Please take care that all parameter paths are provided as absolute paths. This action takes considerably longer than the BLAST database creation with makeblastdb (it takes about one hour to annotate a gene set with 5000 sequences).

To prove if your manually added species is integrated into the HaMStR framework your can run:

	perl bin/oneSeq.pl -showTaxa
This command simply prints a list of all available taxa.

## Dependencies
HaMStR has some dependencies, that either will be automatically installed via the setup script, or must be installed by your system admin if you don't have the root privileges. In the following you will find the full list of HaMStR's dependencies for Ubuntu system as well as the alternatives for MacOS. In Ubuntu, you can install those system and bioinformatics tools/libraries using `apt-get` tool
```
sudo apt-get update -y
sudo apt-get install tool_name -y
```
In MacOS, we suggest using [Homebrew](https://brew.sh) as a replacement for `apt-get`. After having Homebrew, you can install tools/libraries by using the command
```
brew install tool_name
```
In both operation systems, you can install Perl modules using `cpanm`.
```
# first, install cpanm
curl -L http://cpanmin.us | perl - --sudo App::cpanminus
# then, install perl module using cpanm
sudo cpanm perl_module_name
```

_**Note: After having all these dependencies installed, you still need to run the setup script to configure HaMStR!!!**_

### System tools/libraries
* grep (ggrep)
* sed (gsed)
* wget (wget)
* build-essential
* curl (curl)
* locales
* lib32ncurses5
* lib32z1

*(In parentheses are Mac's alternative tools)*

### Bioinformatics tools
* wise (brewsci/bio/genewise)
* hmmer (hmmer)
* ncbi-blast+ (blast)
* blast2
* clustalw (brewsci/bio/clustal-w)
* mafft (mafft)
* muscle (brewsci/bio/muscle)

*(In parentheses are Mac's alternative tools)*

### Perl modules
* libdbi-perl
* libipc-run-perl
* perl-doc
* DBI
* DB_File
* File::Copy
* File::Path
* File::Basename
* File::Which
* List::Util
* Parallel::ForkManager
* POSIX
* XML::SAX
* XML::NamespaceSupport
* XML::Parser
* Getopt::Long
* IO::Handle
* IPC::Run
* Statistics::R
* Term::Cap
* Time::HiRes
* Bio::AlignIO
* Bio::Align::ProteinStatistics
* Bio::DB::Taxonomy
* Bio::SearchIO
* Bio::SearchIO::blastxml
* Bio::Search::Hit::BlastHit
* Bio::Seq
* Bio::SeqIO
* Bio::SeqUtils
* Bio::Tree::Tree
* Bio::Tools::Run::StandAloneBlast

## How to cite
Ebersberger, I., Strauss, S. & von Haeseler, A. HaMStR: Profile hidden markov model based search for orthologs in ESTs. BMC Evol Biol 9, 157 (2009), [doi:10.1186/1471-2148-9-157](https://doi.org/10.1186/1471-2148-9-157)

## Contact
For further support or bug reports please contact: ebersberger@bio.uni-frankfurt.de
