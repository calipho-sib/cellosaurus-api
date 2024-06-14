from ApiCommon import log_it
from datetime import datetime
from ontologies import Term
from optparse import OptionParser
import sys
from lxml import etree


class Vterm:

    def __init__(self):
        self.id = None
        self.update_instructions = ""
        self.name = None
        self.isaList = list()
        self.obsolete = False

    def __str__(self):
        return f"Vterm({self.id} {self.name} - isa: {self.isaList} - obsolete: {self.obsolete} - update: {self.update_instructions} )"

class Vbo_Parser:

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
        if this_id in known_parent_set: return known_parent_set
        t = self.term_dict[this_id]
        #print("id:", this_id, "term: ", t)
        if t.obsolete: return known_parent_set
        known_parent_set.add(this_id)
        parent_set = set(t.isaList)
        # parent_set.update(t.isPartOfSet) # no part_of relationship so far for vbo
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
              "obo"  : "http://purl.obolibrary.org/obo/",
              "vbo"  : "http://purl.obolibrary.org/obo/vbo#"  
             }

        t0 = datetime.now()
        filename = self.term_dir + "vbo.owl"
        log_it("INFO:", "Loading", filename)
        root = etree.parse(filename)

        # get onto data version
        nodes = root.xpath("/rdf:RDF/owl:Ontology/owl:versionInfo", namespaces=ns)
        self.onto_version = nodes[0].text

        # get description of each orphanet class term
        classes = root.xpath("/rdf:RDF/owl:Class", namespaces=ns)
        for cl in classes:
            vterm = Vterm()

            # retrieve id from resource IRI in rdf:about attribute
            resource = cl.get('{%s}about' % ns["rdf"])
            if resource is not None and resource.startswith("http://purl.obolibrary.org/obo/VBO_"):
                vterm.id = resource[31:] # i.e. VBO_0000012
            if vterm.id is None: continue

            # retrieve name
            for node in cl.xpath("rdfs:label", namespaces=ns):
                vterm.name = node.text
            if vterm.name is None: continue

            # get absolescence status
            for node in cl.xpath("owl:deprecated", namespaces=ns):
                vterm.obsolete = (node.text == "true") 

            # get reason of term obsolescence
            for node in cl.xpath("obo:IAO_0000231", namespaces=ns):
                vterm.update_instructions += node.text + " "
            for node in cl.xpath("efo:reason_for_obsolescence", namespaces=ns): # not in vbo but present in ordo
                vterm.update_instructions += node.text + " "
            
            # get info about term to be used as a replacment for obsolete term
            for node in cl.xpath("obo:IAO_0100001", namespaces=ns):
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None:
                    if resource.startswith("http://purl.obolibrary.org/obo/VBO_"):
                        vterm.update_instructions += "replaced with " + resource[31:]
                    else:
                        vterm.update_instructions += "replaced with " + resource                

            # get parent classes
            for node in cl.xpath("rdfs:subClassOf", namespaces=ns):
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None and resource.startswith("http://purl.obolibrary.org/obo/VBO_"):
                    parent_id = resource[31:]
                    vterm.isaList.append(parent_id)
            
            self.term_dict[vterm.id] = vterm
        
        log_it("INFO:", "Loaded", filename, duration_since=t0)

    # - - - - - - - - - - - - - - - - - - 
    def to_cellostyle(self, id):
    # - - - - - - - - - - - - - - - - - - 
        # nothing special to do
        # in cellosaurus VBO accessions (id) have the form VBO_n...
        return id



# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()

    parser = Vbo_Parser("VBO")
    print("VBO version", parser.get_onto_version())

    ac = args[0]
    ac = parser.to_cellostyle(ac)
    print(parser.term_dict.get(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])
    sys.exit(0)

    
