import random
from dnasearch.dnasearch_app.models import DnaSearch
from datetime import datetime
from Bio import SeqIO
from Bio import Seq
from Bio import SeqRecord

PROTEIN_LIST: list = [
    'NC_000852',
    'NC_007346',
    'NC_008724',
    'NC_009899',
    'NC_014637',
    'NC_020104',
    'NC_023423',
    'NC_023640',
    'NC_023719',
    'NC_027867',
]

PROTEIN_DATA_FILE_TEMPLATE = "./protein_data/{}.gb"


def dna_search_task(dna_search: DnaSearch):
    # generate a random ordering of proteins to search through
    protein_search_order = PROTEIN_LIST[:]
    random.shuffle(protein_search_order)

    # for each of those proteins perform a search
    for protein in protein_search_order:
        # load protein data
        seq_record: SeqRecord = SeqIO.read(PROTEIN_DATA_FILE_TEMPLATE.format(protein), "genbank")
        seq: Seq = seq_record.seq.upper()

        # search for matching substring
        idx: int = seq.find(dna_search.search_string)

        # if we found a match record it in our database and stop searching
        if idx > -1:
            dna_search_to_update: DnaSearch = DnaSearch.objects.get(pk=dna_search.pk)
            dna_search_to_update.search_state = 'FOUND'
            dna_search_to_update.completed_at = datetime.now()
            dna_search_to_update.result_protein = protein
            dna_search_to_update.result_start_location = idx
            dna_search_to_update.result_end_location = idx + len(dna_search.search_string)
            dna_search_to_update.save()
            return

    # finally if no results were found, update the database accordingly
    not_found_dna_search_to_update: DnaSearch = DnaSearch.objects.get(pk=dna_search.pk)
    not_found_dna_search_to_update.search_state = 'NOT_FOUND'
    not_found_dna_search_to_update.completed_at = datetime.now()
    not_found_dna_search_to_update.save()

    return