from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
from optparse import OptionParser
import sys
from lxml import etree


class Oterm:

    def new(id, name, isaList): # for test purpose only
        t = Oterm()
        t.id = id
        t.name = name
        t.isaList = isaList
        return t

    def __init__(self):
        self.id = None
        self.update_instructions = ""
        self.name = None
        self.isaList = list()
        self.obsolete = False

    def __str__(self):
        return f"Oterm({self.id} {self.name} - isa: {self.isaList} - obsolete: {self.obsolete} - update: {self.update_instructions} )"

class Ordo_Parser:

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
        if this_id in known_parent_set: return known_parent_set
        t = self.term_dict[this_id]
        #print("id:", this_id, "term: ", t)
        if t.obsolete: return known_parent_set
        known_parent_set.add(this_id)
        parent_set = set(t.isaList)
        # parent_set.update(t.isPartOfSet) # no part_of relationship so far for ordo
        for parent_id in parent_set:
            self.get_parents(known_parent_set, parent_id)
        return known_parent_set

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def get_term(self, id):
    # - - - - - - - - - - - - - - - - - - 
        o_term = self.term_dict.get(id)
        if o_term is None: return None
        if o_term.obsolete:
            log_it("WARNING", f"term {id} is obsolete in {self.abbrev} {o_term.update_instructions}")
            return None
        parent_set = set(o_term.isaList)
        return Term(id, o_term.name, [], list(parent_set), self.abbrev)



    # - - - - - - - - - - - - - - - - - - 
    def load(self):
    # - - - - - - - - - - - - - - - - - - 

        ns = {"rdf"  : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
              "skos" : "http://www.w3.org/2004/02/skos/core#",
              "efo"  : "http://www.ebi.ac.uk/efo/",
              "owl"  : "http://www.w3.org/2002/07/owl#",
              "ORDO" : "http://www.orpha.net/ORDO/"  
             }

        t0 = datetime.now()
        filename = self.term_dir + "ordo.owl"
        log_it("INFO:", "Loading", filename)
        root = etree.parse(filename)

        # get terminology data version
        nodes = root.xpath("/rdf:RDF/owl:Ontology/owl:versionInfo", namespaces=ns)
        self.termi_version = nodes[0].text

        # get description of each orphanet class term
        classes = root.xpath("/rdf:RDF/owl:Class", namespaces=ns)
        for cl in classes:
            oterm = Oterm()

            # retrieve id from resource IRI in rdf:about attribute
            resource = cl.get('{%s}about' % ns["rdf"])
            if resource is not None and resource.startswith("http://www.orpha.net/ORDO/Orphanet_"):
                oterm.id = resource[26:] # i.e. Orphanet_234
            if oterm.id is None: continue

            # retrieve name
            for node in cl.xpath("rdfs:label", namespaces=ns):
                oterm.name = node.text
                break
            if oterm.name is None: continue

            # infer obsolete flag from name
            oterm.obsolete = oterm.name.lower().startswith("obsolete")
                        
            # get parent classes
            for node in cl.xpath("rdfs:subClassOf", namespaces=ns):
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None and resource.startswith("http://www.orpha.net/ORDO/Orphanet_"):
                    parent_id = resource[26:]
                    oterm.isaList.append(parent_id)
            
            # capture reason for obsolescence
            for node in cl.xpath("efo:reason_for_obsolescence", namespaces=ns):
                oterm.update_instructions = node.text

            self.term_dict[oterm.id] = oterm
        
        log_it("INFO:", "Loaded", filename, duration_since=t0)

    # - - - - - - - - - - - - - - - - - - 
    def to_cellostyle(self, id):
    # - - - - - - - - - - - - - - - - - - 
        return id.replace("ORPHA:", "Orphanet_")



# =======================================================

# - - - - - - - - - - - - - - - - - - 
def test_get_parents():
# - - - - - - - - - - - - - - - - - - 
    parser = Ordo_Parser("ORDO")
    parser.term_dict = dict()
    parser.term_dict[1] = Oterm.new(1, "root", [])
    parser.term_dict[11] = Oterm.new(11, "b11", [1])
    parser.term_dict[12] = Oterm.new(12, "b12", [1])
    parser.term_dict[111] = Oterm.new(111, "b111", [11])
    parser.term_dict[15] = Oterm.new(15, "b15", [1])
    parser.term_dict[125] = Oterm.new(125, "b12-b15", [12,15])
    parser.term_dict[1251] = Oterm.new(1251, "b12-b15.1", [125])
    parser.term_dict[115] = Oterm.new(115, "b11-b15", [11,15])
    parser.term_dict[1151] = Oterm.new(1151, "b11-b15.1", [115])
    parser.term_dict[1154] = Oterm.new(1154, "b11-b15.4", [115])
    
    for k in parser.term_dict:
        print("-----")
        print(parser.term_dict[k])
        for p in parser.get_with_parent_list(k):
           if p != k: print("has parents", parser.term_dict[p])
    

# =======================================================
if __name__ == '__main__':
# =======================================================

    #test_get_parents()
    #sys.exit()

    (options, args) = OptionParser().parse_args()

    parser = Ordo_Parser("ORDO")
    print("ORDO version", parser.get_termi_version())

    ac = args[0]
    ac = parser.to_cellostyle(ac)
    print(parser.get_term(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    
