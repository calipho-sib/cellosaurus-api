from ApiCommon import log_it
from datetime import datetime
from terminologies import Term
from optparse import OptionParser
import sys
from lxml import etree


class RsTerm:

    def __init__(self):
        self.id = None
        self.update_instructions = ""
        self.name = None
        self.isaList = list()
        self.obsolete = False

    def __str__(self):
        return f"RsTerm({self.id} {self.name} - isa: {self.isaList} - obsolete: {self.obsolete} - update: {self.update_instructions} )"

class Rs_Parser:

    # - - - - - - - - - - - - - - - - - - 
    # INTERFACE
    # - - - - - - - - - - - - - - - - - - 
    def __init__(self, abbrev):
    # - - - - - - - - - - - - - - - - - - 

        self.abbrev = abbrev
        self.term_dir = "terminologies/" + self.abbrev + "/"
        self.termi_version = "" # set by load()
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
              "obo"  : "http://purl.obolibrary.org/obo/"
             }

        t0 = datetime.now()
        filename = self.term_dir + "owlapi.xrdf"
        log_it("INFO:", "Loading", filename)
        root = etree.parse(filename)

        # get termi data version
        nodes = root.xpath("/rdf:RDF/owl:Ontology/owl:versionInfo", namespaces=ns)
        if len(nodes) > 0: self.termi_version = nodes[0].text + " "
        nodes = root.xpath("/rdf:RDF/owl:Ontology/owl:versionIRI", namespaces=ns)
        if len(nodes) > 0:
            resource = nodes[0].get('{%s}resource' % ns["rdf"])
            if resource is not None: self.termi_version += resource



        # get description of each orphanet class term
        classes = root.xpath("/rdf:RDF/owl:Class", namespaces=ns)
        for cl in classes:
            rs_term = RsTerm()

            # retrieve id from resource IRI in rdf:about attribute
            resource = cl.get('{%s}about' % ns["rdf"])
            if resource is not None and resource.startswith("http://purl.obolibrary.org/obo/RS_"):
                rs_term.id = self.to_cellostyle(resource[31:]) # i.e. RS_0000012
            if rs_term.id is None: continue

            # retrieve name
            for node in cl.xpath("rdfs:label", namespaces=ns):
                rs_term.name = node.text

            # get absolescence status
            for node in cl.xpath("owl:deprecated", namespaces=ns):
                rs_term.obsolete = (node.text == "true") 

            if rs_term.name is None and not rs_term.obsolete:
                log_it("WARNING", f"term without name {rs_term.id}")

            # get reason of term obsolescence
            for node in cl.xpath("obo:IAO_0000231", namespaces=ns): # this IRI means 'reason for deprecation'
                if node.text is not None:
                    rs_term.update_instructions += node.text + " "
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None and resource == "http://purl.obolibrary.org/obo/IAO_0000227": # this IRI means 'merged terms'
                    rs_term.update_instructions += "merged terms "
            
            for node in cl.xpath("efo:reason_for_obsolescence", namespaces=ns): # not in vbo but present in ordo
                if node.text is not None:
                    rs_term.update_instructions += node.text + " "
                
            
            # get info about term to be used as a replacment for obsolete term
            for node in cl.xpath("obo:IAO_0100001", namespaces=ns):
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None:
                    if resource.startswith("http://purl.obolibrary.org/obo/RS_"):
                        rs_term.update_instructions += "replaced with " + self.to_cellostyle(resource[31:])
                    else:
                        rs_term.update_instructions += "replaced with " + resource                

            # get parent classes
            for node in cl.xpath("rdfs:subClassOf", namespaces=ns):
                resource = node.get('{%s}resource' % ns["rdf"])
                if resource is not None and resource.startswith("http://purl.obolibrary.org/obo/RS_"):
                    parent_id = self.to_cellostyle(resource[31:])
                    rs_term.isaList.append(parent_id)
            
            self.term_dict[rs_term.id] = rs_term
        
        log_it("INFO:", "Loaded", filename, duration_since=t0)

    # - - - - - - - - - - - - - - - - - - 
    def to_cellostyle(self, id):
    # - - - - - - - - - - - - - - - - - - 
        return id
        # Note: what's below is not true any more
        # in cellosaurus RS accessions are represented as 'RS:nnnnnnn' 
        #return id.replace("RS_", "RS:")



# =======================================================
if __name__ == '__main__':
# =======================================================

    (options, args) = OptionParser().parse_args()

    parser = Rs_Parser("RS")
    #for t in parser.term_dict: print(parser.term_dict[t])        
    print("Data version", parser.get_termi_version())
    print("Parsed terms", len(parser.term_dict))

    ac = args[0]
    ac = parser.to_cellostyle(ac)
    print(parser.term_dict.get(ac))
    print("with parents:")
    ids = parser.get_with_parent_list(ac)
    for id in ids:print(parser.term_dict[id])

    
