from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
from optparse import OptionParser
import sys
import os
import http.client
import json


class IprTerm:
    def __init__(self):
        self.id = None
        self.name = None
        self.isaList = list()
        self.obsolete = False

    def __str__(self):
        return f"IprTerm({self.id} {self.name} - isa: {self.isaList} - obsolete: {self.obsolete} )"


# ----------------------------------------------------------------------
# UNUSED
# ----------------------------------------------------------------------
# We cancelled the idea of associating domain / family terms to
# UniProtKB xrefs: if we do we should dot it also for MGI xrefs, etc.
# Too complex, better use federated queries instead
# The download() method is functional, other methods are untested
# ----------------------------------------------------------------------

class Interpro_Parser:

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev):
    # - - - - - - - - - - - - - - - - - - 
        self.abbrev = abbrev
        self.TERM_DIR = "terminologies/" + self.abbrev + "/"
        self.CITED_TERMS_FILE = "cited_uniprot_ac.tsv"
        self.CITED_TERMS_TO_IPR_TERMS_FILE = "cited_uniprot_2_ipr.tsv"
        self.termi_version = "unknown version" # set by load()
        self.line_no = 0
        self.term_dict = dict()
        self.download()
        #self.load()


    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_termi_version(self):
    # - - - - - - - - - - - - - - - - - - 
        return self.termi_version
    

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_with_parent_list(self, some_id):
    # - - - - - - - - - - - - - - - - - - 
        some_set = self.get_parents(set(), some_id)
        return list(some_set)

    # - - - - - - - - - - - - - - - - - - 
    def get_parents(self, known_parent_set, this_id):
    # - - - - - - - - - - - - - - - - - - 
        if this_id in known_parent_set:
            return known_parent_set
        else:
            known_parent_set.add(this_id)
        t = self.term_dict[this_id]
        parent_set = set(t.isaList)
        for parent_id in parent_set:
            self.get_parents(known_parent_set, parent_id)
        return known_parent_set


    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_term(self, id):
    # - - - - - - - - - - - - - - - - - - 
        cterm = self.term_dict.get(id)
        if cterm is None: return None
        parent_set = set(cterm.isaList)
        parent_set.update(cterm.isPartOfSet)
        return Term(id, cterm.name, [], list(parent_set), self.abbrev)

    # - - - - - - - - - - - - - - - - - - 
    def read_next_term(self, f_in):
    # - - - - - - - - - - - - - - - - - - 
        term = None
        while True:
            line = f_in.readline()
            if line == "": break
            self.line_no += 1
            line = line.strip()
            if line == "": break
            if line == "[Typedef]": break            
            if line == "[Term]":
                term = IprTerm()
            elif line == "is_obsolete: true":
                term.obsolete = True
            elif line.startswith("id: "): 
                term.id = line[4:].rstrip()
            elif line.startswith("name: "):
                term.name = line[6:].rstrip()
            elif line.startswith("is_a: "):
                term.isaList.append(line[6:].strip())
        return term


    # - - - - - - - - - - - - - - - - - - 
    def find_data_version(self, f_in):
    # - - - - - - - - - - - - - - - - - - 
        self.termi_version = "version not found"
        while True:
            line = f_in.readline()
            if line == "": break
            self.line_no += 1
            line = line.strip()
            if line == "":
                break
            elif line.startswith("data-version: "): 
                self.termi_version = line
            elif line.startswith("[Term]"):
                log_it("ERROR:", "parser could not find InterPro version")
                break
    

    # - - - - - - - - - - - - - - - - - - 
    def load(self):
    # - - - - - - - - - - - - - - - - - - 
        if not os.path.exists(self.TERM_DIR + self.CITED_TERMS_FILE): 
            log_it("ERROR", self.CITED_TERMS_FILE, "not found. Please call download() method first")
            sys.exit(6)

        t0 = datetime.now()
        filename = self.TERM_DIR + self.CITED_TERMS_FILE
        
        log_it("INFO:", "Loading", filename)
        f_in = open(filename)
        self.find_data_version(f_in)
        term_cnt = 0
        while True:
            term = self.read_next_term(f_in)
            if term is None: break;
            term_cnt +=1
            #if term_cnt > 10: break
            if term.obsolete: continue
            self.term_dict[term.id] = term
            for alt_id in term.altIdList: self.term_dict[alt_id] = term
        f_in.close()

        # now store isPartOf relationships based on hasPart relationships
        for id in self.term_dict:
            term = self.term_dict[id]
            if term.id != id: continue # we don't want to have secondary (alt) ids in the isPartOf relationships
            for child_id in self.term_dict[id].hasPartList:
                self.term_dict[child_id].isPartOfSet.add(id)

        log_it("INFO:", "Loaded", filename, duration_since=t0)


    # - - - - - - - - - - - - - - - - - - - - - 
    def getUniProtKB_topic_ac_label(self, cc):
    # - - - - - - - - - - - - - - - - - - - - -
        # Examples of cc values:
        # CC   Monoclonal antibody target: UniProtKB; P04439; Human HLA-A (Note=Recognizes allele A*69).
        # CC   Sequence variation: Gene deletion; UniProtKB; Q8CFA6; Insig1; Zygosity=Heterozygous.
        if not cc.startswith("CC   "): return None
        pos = cc.find("UniProtKB; ")
        if pos == -1: return None
        topic = cc[5:].split(":")[0]
        parts = cc[pos:].split("; ")
        ac = parts[1]
        label = parts[2].strip()
        pos = label.find("(Note=")
        if pos > -1: label = label[:pos].strip()
        if label.endswith("."): label = label[:-1]
        return {"topic": topic, "ac": ac, "label": label}
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_fetch_from_interpro(self, uniprotkb_ac):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # https
        server = "www.ebi.ac.uk"
        path = "https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/uniprot/{ac}"
        params = "?format=json"
        url = path.format(ac=uniprotkb_ac) + params
        try:
            connection = http.client.HTTPSConnection(server)
            connection.request("GET", url)
            response = connection.getresponse()
        except Exception as e:
            print("ERROR", "on request to ebi", url , e)
            connection.close()
            return None
        
        if response.status == 200:
            data = response.read().decode('utf-8')
            json_data = json.loads(data)
            connection.close()
            return json_data
        else: 
            print("ERROR", "on request to ebi", url, "response status:", response.status, "reason:", response.reason)
            connection.close()
            return None

    # - - - - - - - - - - - - - - - - - - 
    def download(self):
    # - - - - - - - - - - - - - - - - - - 

        ac_dict = dict()

        # step 1 - extract UniProtKB references in cello

        t0 = datetime.now()
        filename = "data_in/cellosaurus.txt"
        log_it("INFO:", "Reading", filename, duration_since=t0)
        f_in = open(filename)
        while True:
            line = f_in.readline()
            if line == "": break
            line = line.strip()
            data = self.getUniProtKB_topic_ac_label(line)
            if data is None: continue
            ac_dict[data["ac"]] = data["label"]
        f_in.close()

        # step 2 - save list of ac - label pair in tsv file

        filename = self.TERM_DIR + self.CITED_TERMS_FILE
        f_out = open(filename, "w")
        for ac in ac_dict:
            line = "".join([ac, "\t", ac_dict[ac], "\n"])
            f_out.write(line)
        f_out.close()
        log_it("INFO:", "Saved", len(ac_dict), "UniProtKB ACs in", filename, duration_since=t0)

        # step 3 - query interpro to get domain / family info for each UniProtKB ac clloected above 
        
        t0 = datetime.now()
        filename = self.TERM_DIR + self.CITED_TERMS_TO_IPR_TERMS_FILE
        f_out = open(filename, "w")
        log_it("INFO:", "Creating", filename, duration_since=t0)
        count = 0
        for ac in ac_dict:
            #if count > 100: break
            count += 1
            if count % 20 == 0: log_it("INFO", f"Running request {count} / {len(ac_dict)} ...")
            obj = self.get_fetch_from_interpro(ac)
            if obj is None: continue 
            for result in obj.get("results") or []:
                metadata = result.get("metadata")
                #if metadata is None: continue
                ipr_ac = metadata["accession"]
                ipr_typ = metadata["type"]
                ipr_lbl = metadata["name"]
                line = "".join([ac, "\t", ac_dict[ac], "\t", ipr_typ, "\t", ipr_ac, "\t", ipr_lbl, "\n"])
                f_out.write(line)
        f_out.close()
        log_it("INFO:", "Saved", count, "UniProtKB / InterPro links in", filename, duration_since=t0)





# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()



    parser = Interpro_Parser("IPR")
    print(parser.get_termi_version())

    sys.exit()

    ac = args[0]

    print(parser.get_term(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    print("------")
    ids = parser.get_parents(set(), "CHEBI:78547")
    for id in ids:print(parser.term_dict[id])
    
    print("------")
    ids = parser.get_parents(set(), "CHEBI:36080")
    for id in ids:print(parser.term_dict[id])
    
    print("------")
    ids = parser.get_parents(set(), "CHEBI:87627")
    for id in ids:print(parser.term_dict[id])
    
