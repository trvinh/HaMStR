# -*- coding: utf-8 -*-

#######################################################################
# Copyright (C) 2020 Vinh Tran
#
#  This script is used to prepare data for HaMStR oneSeq.
#  It will create a folder within genome_dir with the naming scheme of
#  HaMStR ([Species acronym]@[NCBI ID]@[Proteome version], e.g
#  HUMAN@9606@3) and a annotation file in JSON format in weight_dir
#  (optional).
#  For a long header of original FASTA sequence, only the first word
#  will be taken as the ID of new fasta file, everything after the
#  first whitespace will be removed. If this first word is not unique,
#  an automatically increasing index will be added.
#
#  This script is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License <http://www.gnu.org/licenses/> for
#  more details
#
#  Contact: tran@bio.uni-frankfurt.de
#
#######################################################################

import sys
import os
import argparse
from pathlib import Path
from Bio import SeqIO
import subprocess
import multiprocessing as mp
from ete3 import NCBITaxa

def checkFileExist(file):
    if not os.path.exists(os.path.abspath(file)):
        sys.exit('%s not found' % file)

def checkTaxId(taxId):
    ncbi = NCBITaxa()
    tmp = ncbi.get_rank([taxId])
    try:
        tmp = ncbi.get_rank([taxId])
        rank = tmp[int(taxId)]
        if not rank == 'species':
            print('\033[92mWARNING: rank of %s is not SPECIES (%s)\033[0m' % (taxId, rank))
        else:
            print('\033[92mNCBI taxon info: %s %s\033[0m' % (taxId, ncbi.get_taxid_translator([taxId])[int(taxId)]))
    except:
        print('\033[92mWARNING: %s not found in NCBI taxonomy database!\033[0m' % taxId)

def runBlast(args):
    (specName, specFile, outPath) = args
    blastCmd = 'makeblastdb -dbtype prot -in %s -out %s/blast_dir/%s/%s' % (specFile, outPath, specName, specName)
    subprocess.call([blastCmd], shell = True)
    fileInGenome = "%s/genome_dir/%s/%s.fa" % (outPath, specName, specName)
    fileInBlast = "%s/blast_dir/%s/%s.fa" % (outPath, specName, specName)
    if not Path(fileInBlast).exists():
        lnCmd = 'ln -fs %s %s' % (fileInGenome, fileInBlast)
        subprocess.call([lnCmd], shell = True)


def main():
    version = '1.0.0'
    parser = argparse.ArgumentParser(description='You are running addTaxonHamstr version ' + str(version) + '.')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-f', '--fasta', help='FASTA file of input taxon', action='store', default='', required=True)
    required.add_argument('-n', '--name', help='Acronym name of input taxon', action='store', default='', required=True, type=str)
    required.add_argument('-i', '--taxid', help='Taxonomy ID of input taxon', action='store', default='', required=True, type=int)
    required.add_argument('-o', '--outPath', help='Path to output directory', action='store', default='', required=True)
    optional.add_argument('-c', '--coreTaxa', help='Include this taxon to core taxa (i.e. taxa in blast_dir folder)', action='store_true', default=False)
    optional.add_argument('-v', '--verProt', help='Proteome version', action='store', default=1, type=int)
    optional.add_argument('-a', '--noAnno', help='Do NOT annotate this taxon using annoFAS', action='store_true', default=False)
    optional.add_argument('--cpus', help='Number of CPUs used for annotation. Default = available cores - 1', action='store', default=0, type=int)

    args = parser.parse_args()

    checkFileExist(args.fasta)
    faIn = args.fasta
    name = args.name.upper()
    taxId = str(args.taxid)
    outPath = str(Path(args.outPath).resolve())
    doAnno = args.noAnno
    coreTaxa = args.coreTaxa
    ver = str(args.verProt)
    cpus = args.cpus
    if cpus == 0:
        cpus = mp.cpu_count()-2

    ### species name after hamstr naming scheme
    checkTaxId(taxId)
    specName = name+'@'+taxId+'@'+ver

    ### create file in genome_dir
    print('Parsing FASTA file...')
    Path(outPath + '/genome_dir').mkdir(parents = True, exist_ok = True)
    genomePath = outPath + '/genome_dir/' + specName
    Path(genomePath).mkdir(parents = True, exist_ok = True)
    # load fasta seq
    inSeq = SeqIO.to_dict((SeqIO.parse(open(faIn), 'fasta')))
    specFile = genomePath + '/' + specName + '.fa'
    if (not os.path.exists(os.path.abspath(specFile))) or (os.stat(specFile).st_size == 0):
        f = open(specFile, 'w')
        index = 0
        tmpDict = {}
        for id in inSeq:
            if not id in tmpDict:
                tmpDict[id] = 1
            else:
                index = index + 1
                id = str(id) + '|' + str(index)
                tmpDict[id] = 1
            f.write('>%s\n%s\n' % (id, inSeq[id].seq))
        f.close()
    else:
        print(genomePath + '/' + specName + '.fa already exists!')

    ### create blast db
    if coreTaxa:
        print('Creating Blast DB...')
        Path(outPath + '/blast_dir').mkdir(parents = True, exist_ok = True)
        if not os.path.exists(os.path.abspath(outPath + '/blast_dir/' + specName + '/' + specName + '.phr')):
            try:
                runBlast([specName, specFile, outPath])
            except:
                print('\033[91mProblem with creating BlastDB.\033[0m')
        else:
            print('Blast DB already exists!')

    ### create annotation
    if not doAnno:
        Path(outPath + '/weight_dir').mkdir(parents = True, exist_ok = True)
        annoCmd = 'annoFAS -i %s/%s.fa -o %s --cpus %s' % (genomePath, specName, outPath+'/weight_dir', cpus)
        try:
            subprocess.call([annoCmd], shell = True)
        except:
            print('\033[91mProblem with running annoFAS. You can check it with this command:\n%s\033[0m' % annoCmd)

    print('Output can be found in %s within genome_dir [and blast_dir, weight_dir] folder[s]' % outPath)

if __name__ == '__main__':
    main()