from namespace import NamespaceRegistry as ns_reg
from sparql_client import EndpointClient
import sys
from ApiCommon import log_it


#-------------------------------------------------
class OntologyBuilder:
#-------------------------------------------------


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for ns in ns_reg.namespaces: lines.append(ns.getSparqlPrefixDeclaration())
        prefixes = "\n".join(lines)

        self.client = EndpointClient("http://localhost:8890/sparql")

        self.domain_query_template = prefixes + """
            \nselect ?prop ?value (count(distinct ?s) as ?count) where {
            \n    values ?prop { $prop }
            \n    ?s ?prop ?o .
            \n    ?s rdf:type ?value .
            \n}
            \ngroup by ?prop ?value
            """
        
        self.range_query_template = prefixes + """
            \nselect  ?prop ?value (count(*) as ?count) where {
            \n    values ?prop { $prop }
            \n    ?s ?prop ?o .
            \n    optional { ?o rdf:type ?cl . }
            \n    BIND( IF (isIRI(?o), 'rdfs:Resource', IF (isLiteral(?o), datatype(?o), ?cl)) AS ?value)
            \n}
            \ngroup by ?prop ?value
            """

        self.rdfs_subClassOf = dict()

        # publication classes
        self.rdfs_subClassOf[ns_reg.onto.Thesis()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.BachelorThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.MasterThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.DoctoralThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.MedicalDegreeMasterThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.MedicalDegreeThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.PrivaDocentThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.VeterinaryMedicalDegreeThesis()] = ns_reg.onto.Thesis()
        self.rdfs_subClassOf[ns_reg.onto.Patent()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.JournalArticle()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.Book()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.BookChapter()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.TechnicalDocument()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.MiscellaneousDocument()] = ns_reg.onto.Publication()
        self.rdfs_subClassOf[ns_reg.onto.ConferencePublication()] = ns_reg.onto.Publication()

        # antigen classes
        self.rdfs_subClassOf[ns_reg.onto.Protein()] = ns_reg.onto.Antigen()
        self.rdfs_subClassOf[ns_reg.onto.ChemicalAgent()] = ns_reg.onto.Antigen()

        # sequence variation classes
        self.rdfs_subClassOf[ns_reg.onto.GeneMutation()] = ns_reg.onto.SequenceVariation()
        self.rdfs_subClassOf[ns_reg.onto.RepeatExpansion()] = ns_reg.onto.GeneMutation()
        self.rdfs_subClassOf[ns_reg.onto.SimpleMutation()] = ns_reg.onto.GeneMutation()
        self.rdfs_subClassOf[ns_reg.onto.UnexplicitMutation()] = ns_reg.onto.GeneMutation()
        self.rdfs_subClassOf[ns_reg.onto.GeneFusion()] = ns_reg.onto.SequenceVariation()
        self.rdfs_subClassOf[ns_reg.onto.GeneAmplification()] = ns_reg.onto.SequenceVariation()
        self.rdfs_subClassOf[ns_reg.onto.GeneDuplication()] = ns_reg.onto.GeneAmplification()
        self.rdfs_subClassOf[ns_reg.onto.GeneTriplication()] = ns_reg.onto.GeneAmplification()
        self.rdfs_subClassOf[ns_reg.onto.GeneQuarduplication()] = ns_reg.onto.GeneAmplification()
        self.rdfs_subClassOf[ns_reg.onto.GeneExtensiveAmplification()] = ns_reg.onto.GeneAmplification()
        self.rdfs_subClassOf[ns_reg.onto.GeneDeletion()] = ns_reg.onto.SequenceVariation()

        self.rdfs_comment = dict()
        # comments for classes
        self.rdfs_comment[ns_reg.onto.CellLine()] = "Cell line as defined in the Cellosaurus"
        # comments for props
        self.rdfs_comment[ns_reg.onto.recommendedName()] = "Most frequently the name of the cell line as provided in the original publication"
        self.rdfs_comment[ns_reg.onto.alternativeName()] = "Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_label(self, class_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        chars = list()
        for ch in class_name:
            if ch.isupper() and len(chars)>0:
                chars.append(" ")
                chars.append(ch.lower())
            else:
                chars.append(ch)
        return "".join(chars)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_url(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        onto_url = ns_reg.onto.baseurl()
        if onto_url.endswith("#"): onto_url = onto_url[:-1]
        return onto_url


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_header(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for ns in ns_reg.namespaces: lines.append(ns.getTtlPrefixDeclaration())

        lines.append("")
        onto_url = "<" + self.get_onto_url() + ">"
        descr = """The Cellosaurus ontology describes the concepts used to build the Cellosaurus knowledge resource on cell lines. 
        The Cellosaurus attempts to describe all cell lines used in biomedical research."""
        lines.append(onto_url)
        lines.append("    a owl:Ontology ;")
        lines.append("    dcterms:created " + ns_reg.xsd.date("2022-11-21") + " ;")
        lines.append("    dcterms:modified " + ns_reg.xsd.date("2024-07-11") + " ;")
        lines.append("    dcterms:description " + ns_reg.xsd.string3(descr) + " ;")
        lines.append("    dcterms:license <http://creativecommons.org/licenses/by/4.0> ;")
        lines.append("    dcterms:title " + ns_reg.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    dcterms:versionInfo " + ns_reg.xsd.string("1.0") + " ;")
        lines.append("    .")
        lines.append("")
        return lines


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_classes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology Classes", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        for method in dir(ns_reg.onto):
            if callable(getattr(ns_reg.onto, method)):
                if method[0].isupper():
                    class_name = method
                    lines.append(":" + class_name)
                    lines.append(f"    rdf:type owl:Class ;")
                    class_label =  ns_reg.xsd.string(self.build_label(class_name))
                    lines.append(f"    rdfs:label {class_label} ;")
                    parent_class = self.rdfs_subClassOf.get(":" + class_name)
                    if parent_class is not None:
                        lines.append(f"    rdfs:subClassOf " + parent_class + " ;")
                    class_comment = self.rdfs_comment.get(":" + class_name)
                    if class_comment is not None:
                        class_comment =  ns_reg.xsd.string(class_comment)
                        lines.append(f"    rdfs:comment {class_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")
                    lines.append("    .")
                    lines.append("")
        return lines
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_root_ancestor(self, some_class):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ancestor = self.rdfs_subClassOf.get(some_class)
        if ancestor is None:
            return some_class
        else: 
            return self.get_root_ancestor(ancestor)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_simplified_classes(self, class_dict):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        simplified_classes = dict()
        for name in class_dict:
            count = class_dict[name]
            root_name = self.get_root_ancestor(name)
            if root_name not in simplified_classes: simplified_classes[root_name] = 0
            simplified_classes[root_name] += count
        return simplified_classes


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_props(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology properties", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        prop_count = 0
        for method in dir(ns_reg.onto):
            if callable(getattr(ns_reg.onto, method)):
                if method[0].islower():
                    # skip those below are not ontology terms but helper functions of the super class
                    if method in ["prefix", "baseurl", "getTtlPrefixDeclaration", "getSparqlPrefixDeclaration"]: continue 
                    prop_name = ":" + method
                    prop_label =  ns_reg.xsd.string(self.build_label(method))
                    prop_comment = self.rdfs_comment.get(prop_name)

                    #if prop_count > 10: break
                    prop_count += 1

                    log_it("DEBUG", "querying prop_name", prop_name, "domains")
                    domains = dict()
                    domain_query = self.domain_query_template.replace("$prop", prop_name)
                    response = self.client.run_query(domain_query)
                    if not response.get("success"):
                        log_it("ERROR", response.get("error_type"))
                        log_it(response.get("error_msg"))
                        sys.exit(2)
                    rows = response.get("results").get("bindings")
                    for row in rows:
                        value = self.client.apply_prefixes(row.get("value").get("value"))
                        count = int(row.get("count").get("value"))
                        domains[value]=count

                    log_it("DEBUG", "querying prop_name", prop_name, "ranges")
                    ranges = dict()
                    range_query = self.range_query_template.replace("$prop", prop_name)
                    response = self.client.run_query(range_query)
                    if not response.get("success"):
                        log_it("ERROR", response.get("error_type"))
                        log_it(response.get("error_msg"))
                        sys.exit(2)
                    rows = response.get("results").get("bindings")
                    for row in rows:
                        value = self.client.apply_prefixes(row.get("value").get("value"))
                        count = int(row.get("count").get("value"))
                        ranges[value]=count

                    prop_types = set()
                    for r in ranges:
                        if r.startswith("xsd:"): 
                            prop_types.add("owl:DatatypeProperty") 
                        else:
                            prop_types.add("owl:ObjectProperty") 

                    # now build the prop definition

                    lines.append(prop_name)
                    lines.append("    a rdf:Property ;")
                    for typ in prop_types:
                        lines.append("    a " + typ + " ;")

                    lines.append(f"    rdfs:label {prop_label} ;")

                    if prop_comment is not None:
                        prop_comment =  ns_reg.xsd.string(prop_comment)
                        lines.append(f"    rdfs:comment {prop_comment} ;")

                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")

                    if len(domains)>1: 
                        sd = self.get_simplified_classes(domains)
                        if sd != domains:
                            #lines.append("# SIMPLIFIED domains")
                            domains = sd

                    if len(domains)==1:
                        name = list(domains.keys())[0]
                        tmp = "    rdfs:domain " + name + " ;"
                        line = tmp.ljust(60) + "# " + str(domains[name]) + " instances"
                        lines.append(line)
                    elif len(domains)>1:
                        lines.append("    rdfs:domain [ a owl:Class ; owl:unionOf (")
                        for name in domains:
                            tmp = "        " + name
                            line = tmp.ljust(60) + "# " + str(domains[name]) + " instances"
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    if len(ranges)==1:
                        sr = self.get_simplified_classes(ranges)
                        if sr != ranges:
                            #lines.append("# SIMPLIFIED ranges")
                            ranges = sr

                    if len(ranges)==1:
                        name = list(ranges.keys())[0]
                        tmp = "    rdfs:range " + name + " ;"
                        line = tmp.ljust(60) + "# " + str(ranges[name]) + " instances"
                        lines.append(line)

                    elif len(ranges)>1:
                        lines.append("    rdfs:range [ a owl:Class ; owl:unionOf (")
                        for name in ranges:
                            tmp = "        " + name
                            line = tmp.ljust(60) + "# " + str(ranges[name]) + " instances"
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    lines.append("    .")
                    lines.append("")

        return lines


# --------------------------------------------
if __name__ == '__main__':
# --------------------------------------------

    builder = OntologyBuilder()
    lines = list()
    lines.extend(builder.get_onto_header())
    lines.extend(builder.get_classes())
    lines.extend(builder.get_props())
    for line in lines: print(line)