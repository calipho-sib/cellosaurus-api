from ApiCommon import log_it
from datetime import datetime
from ontologies import Term
from optparse import OptionParser
import sys


class ClTerm:
    def __init__(self):
        self.id = None
        self.update_instructions = ""
        self.altIdList = list()
        self.name = None
        self.isaList = list()
        self.hasPartList = list()
        self.isPartOfSet = set()
        self.obsolete = False

    def __str__(self):
        return f"ClTerm({self.id} {self.name} - isa: {self.isaList} - isPartOf: {self.isPartOfSet} - obsolete: {self.obsolete} - update: {self.update_instructions} - )"

class Cl_Parser:

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev):
    # - - - - - - - - - - - - - - - - - - 
        self.abbrev = abbrev
        self.term_dir = "terminologies/" + self.abbrev + "/"
        self.onto_version = "unknown version" # set by load()
        self.line_no = 0
        self.term_dict = dict()
        self.load()


    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_onto_version(self):
    # - - - - - - - - - - - - - - - - - - 
        return self.onto_version
    

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
        if cterm.obsolete:
            log_it("WARNING", f"term {id} is obsolete in {self.abbrev} {cterm.update_instructions}")
            return None
        if cterm.id != id:
            log_it("WARNING", f"term {id} is a secondary ID of {cterm.id} in {self.abbrev} ontology")
            return None
        parent_set = set(cterm.isaList)
        parent_set.update(cterm.isPartOfSet)
        return Term(id, cterm.name, [], list(parent_set), self.abbrev)


    # - - - - - - - - - - - - - - - - - - 
    def to_cellostyle(self, id):
    # - - - - - - - - - - - - - - - - - - 
        return id.replace("CL:", "CL_")

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
                term = ClTerm()
            elif line == "is_obsolete: true":
                term.obsolete = True
            elif line.startswith("id: "): 
                term.id = self.to_cellostyle(line[4:].rstrip())
            elif line.startswith("alt_id: "):
                altId = line[8:].strip()
                altId = self.to_cellostyle(altId)
                term.altIdList.append(altId)
            elif line.startswith("replaced_by: "): 
                term.update_instructions += self.to_cellostyle(line) + " "
            elif line.startswith("consider: "): 
                term.update_instructions += self.to_cellostyle(line) + " "
            elif line.startswith("name: "):
                term.name = line[6:].rstrip()
            elif line.startswith("is_a: "):
                parentId = line[6:].split("!")[0].strip()       # i.e. "is_a: CL:0000422 ! mitogenic signaling cell"
                parentId = parentId.replace("{is_inferred=\"true\"}", "").strip() # we also take inferred is_a relationship
                parentId = self.to_cellostyle(parentId)
                term.isaList.append(parentId)
            elif line.startswith("relationship: has_part "):
                childId = line[23:].split("!")[0].strip()       # i.e. "relationship: has_part CL:0017503 ! basophilic cytoplasm "
                childId = self.to_cellostyle(childId)
                term.hasPartList.append(childId)
        return term


    # - - - - - - - - - - - - - - - - - - 
    def find_data_version(self, f_in):
    # - - - - - - - - - - - - - - - - - - 
        self.onto_version = "version not found"
        while True:
            line = f_in.readline()
            if line == "": break
            self.line_no += 1
            line = line.strip()
            if line == "":
                break
            elif line.startswith("data-version: "): 
                self.onto_version = line
            elif line.startswith("[Term]"):
                log_it("ERROR:", "parser could not find ChEBI version")
                break
    

    # - - - - - - - - - - - - - - - - - - 
    def load(self):
    # - - - - - - - - - - - - - - - - - - 
        t0 = datetime.now()
        filename = self.term_dir + "cl-simple.obo"
        log_it("INFO:", "Loading", filename)
        f_in = open(filename)
        self.find_data_version(f_in)
        term_cnt = 0
        while True:
            term = self.read_next_term(f_in)
            if term is None: break;
            term_cnt +=1
            #if term_cnt > 10: break
            #if term.obsolete: continue
            self.term_dict[term.id] = term
            for alt_id in term.altIdList:
                self.term_dict[alt_id] = term
        f_in.close()

        # now store isPartOf relationships based on hasPart relationships
        for id in self.term_dict:
            term = self.term_dict[id]
            if term.id != id : continue  # we don't want to have a secondary ID in the isPartOf relationships
            if term.obsolete:  continue  # we don't want to have obsolete ids in the isPartOf relationships
            for child_id in self.term_dict[id].hasPartList:
                self.term_dict[child_id].isPartOfSet.add(id)

        log_it("INFO:", "Loaded", filename, duration_since=t0)









# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()

    parser = Cl_Parser("CL")
    print(parser.get_onto_version())

    ac = args[0]
    ac = parser.to_cellostyle(ac)
    print(parser.get_term(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    
