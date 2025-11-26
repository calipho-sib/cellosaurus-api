from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
from optparse import OptionParser
import sys


class ChebiTerm:
    def __init__(self):
        self.id = None
        self.altIdList = list()
        self.name = None
        self.isaList = list()
        self.hasPartList = list()
        self.isPartOfSet = set()
        self.obsolete = False

    def __str__(self):
        return f"ChebiTerm({self.id} {self.name} - isa: {self.isaList} - isPartOf: {self.isPartOfSet} - altIds: {self.altIdList} - obsolete: {self.obsolete} )"

class Chebi_Parser:

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev):
    # - - - - - - - - - - - - - - - - - - 
        self.abbrev = abbrev
        self.term_dir = "terminologies/" + self.abbrev + "/"
        self.termi_version = "unknown version" # set by load()
        self.line_no = 0
        self.term_dict = dict()
        self.load()


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
        parent_set.update(t.isPartOfSet)
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
        if id != cterm.id:
            log_it("WARNING", f"term {id} is a secondary ID of {cterm.id} in {self.abbrev} terminology")
            return None
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
                term = ChebiTerm()
            elif line == "is_obsolete: true":
                term.obsolete = True
            elif line.startswith("id: "): 
                term.id = line[4:].rstrip().replace(":", "_")
            elif line.startswith("alt_id: "): 
                term.altIdList.append(line[8:].rstrip().replace(":", "_"))
            elif line.startswith("name: "):
                term.name = line[6:].rstrip()
            elif line.startswith("is_a: "):
                # now is_a lines look like 'is_a: CHEBI:16114 ! medicarpin'
                term.isaList.append(line[6:].split(" ! ")[0].replace(":","_"))  
            elif line.startswith("relationship: has_part "):
                term.hasPartList.append(line[23:].strip().replace(":", "_"))
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
                log_it("ERROR:", "parser could not find ChEBI version")
                break
    

    # - - - - - - - - - - - - - - - - - - 
    def load(self):
    # - - - - - - - - - - - - - - - - - - 
        t0 = datetime.now()
        filename = self.term_dir + "chebi_lite.obo"
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









# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()

    parser = Chebi_Parser("ChEBI")
    print(parser.get_termi_version())

    ac = args[0]

    print(parser.get_term(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    print("------")
    #ids = parser.get_parents(set(), "CHEBI:78547")
    ids = parser.get_parents(set(), "CHEBI_78547")
    for id in ids:print(parser.term_dict[id])
    
    print("------")
    #ids = parser.get_parents(set(), "CHEBI:36080")
    ids = parser.get_parents(set(), "CHEBI_36080")
    for id in ids:print(parser.term_dict[id])
    
    print("------")
    #ids = parser.get_parents(set(), "CHEBI:36080")
    ids = parser.get_parents(set(), "CHEBI_36080")
    for id in ids:print(parser.term_dict[id])
    
