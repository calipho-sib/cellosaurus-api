from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
from optparse import OptionParser
import sys


class NciTerm:
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
        return f"NciTerm({self.id} {self.name} - isa: {self.isaList} - isPartOf: {self.isPartOfSet} - obsolete: {self.obsolete} - update: {self.update_instructions} - )"

class Ncit_Parser:

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
        nci_term = self.term_dict.get(id)
        if nci_term is None: return None
        if nci_term.obsolete:
            log_it("WARNING", f"term {id} is obsolete in {self.abbrev} {nci_term.update_instructions}")
            return None
        if nci_term.id != id:
            log_it("WARNING", f"term {id} is a secondary ID of {nci_term.id} in {self.abbrev} terminology")
            return None
        parent_set = set(nci_term.isaList)
        parent_set.update(nci_term.isPartOfSet)
        return Term(id, nci_term.name, [], list(parent_set), self.abbrev)


    # - - - - - - - - - - - - - - - - - - 
    def to_cellostyle(self, id):
    # - - - - - - - - - - - - - - - - - - 
        # remove "NCIT:" prefix
        # or since 2025:
        # remove "Thesaurus:" prefix
        if id.startswith("Thesaurus:"): return id[10:]
        if id.startswith("NCIT:"): return id[5:]
        return id


    # - - - - - - - - - - - - - - - - - - 
    def filter_out_braces(self, str):
    # - - - - - - - - - - - - - - - - - - 
        p1 = str.find("{")
        if p1 == -1: return str
        p2 = str.find("}")
        if p2 == -1: return str
        left_part = str[:p1].strip()
        rght_part = str[p2+1:].strip()
        all = left_part + " " + rght_part
        return all.strip()

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
                term = NciTerm()
            elif line == "is_obsolete: true":
                term.obsolete = True
            elif line.startswith("id: "): 
                term.id = self.to_cellostyle(line[4:].rstrip())
            elif line.startswith("name: "):
                term.name = line[6:].rstrip()
            elif line.startswith("is_a: "):
                parentId = line[6:].split("!")[0].strip()       
                parentId = self.filter_out_braces(parentId)
                parentId = self.to_cellostyle(parentId)
                term.isaList.append(parentId)
            elif line.startswith("alt_id: "):               # not found in data
                altId = line[8:].strip()
                altId = self.to_cellostyle(altId)
                term.altIdList.append(altId)
            elif line.startswith("replaced_by: "):          # not found in data
                term.update_instructions += self.to_cellostyle(line) + " "
            elif line.startswith("consider: "):             # not found in data
                term.update_instructions += self.to_cellostyle(line) + " "
            elif line.startswith("relationship: has_part "):  # not found in data
                childId = line[23:].split("!")[0].strip()      
                childId = self.filter_out_braces(childId)
                childId = self.to_cellostyle(childId)
                term.hasPartList.append(childId)
            elif line.startswith("relationship: part_of "):    # not found in data
                childId = line[22:].split("!")[0].strip()       
                childId = self.filter_out_braces(childId)
                childId = self.to_cellostyle(childId)
                term.isPartOfSet.add(childId)
        return term


    # - - - - - - - - - - - - - - - - - - 
    def find_data_version(self, f_in):
    # - - - - - - - - - - - - - - - - - - 
        # example of line containing verion:
        # data-version: releases/2024-05-07
        # since 2025: 
        # property_value: owl:versionInfo "25.02d" xsd:string        
        self.termi_version = "version not found"
        while True:
            line = f_in.readline()
            if line == "": break
            self.line_no += 1
            line = line.strip()
            if line == "":
                break
            elif line.startswith("property_value: owl:versionInfo"): # new format
                self.termi_version = line.split("\"")[1]
            elif line.startswith("data-version: "):                  # old format
                self.termi_version = line
            elif line.startswith("[Term]"):
                log_it("ERROR:", "parser could not find ChEBI version")
                break
    

    # - - - - - - - - - - - - - - - - - - 
    def load(self):
    # - - - - - - - - - - - - - - - - - - 
        t0 = datetime.now()
        filename = self.term_dir + "ncit.obo"
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
        # now add isPartOf relationships based on hasPart relationships
        # INFO: part_of is not found in data, so not useful so far
        for id in self.term_dict:
            term = self.term_dict[id]
            if term.id != id : continue  # we don't want to have a secondary ID in the isPartOf relationships
            if term.obsolete:  continue  # we don't want to have obsolete ids in the isPartOf relationships
            for child_id in self.term_dict[id].hasPartList:
                self.term_dict[child_id].isPartOfSet.add(id)

        log_it(f"INFO: found {term_cnt} terms")
        log_it("INFO:", "Loaded", filename, duration_since=t0)









# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()

    parser = Ncit_Parser("NCIt")
    print("data version:", parser.get_termi_version())
    obsolete_or_secondary_count = 0
    for k in parser.term_dict:
        if parser.get_term(k) == None:
            obsolete_or_secondary_count += 1
    print("obsolete or secondary count:", obsolete_or_secondary_count)
    ac = args[0]
    ac = parser.to_cellostyle(ac)
    print(parser.get_term(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    
