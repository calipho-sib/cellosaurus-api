from namespace import NamespaceRegistry as ns_reg
from ApiCommon import log_it
from sparql_client import EndpointClient
import sys
from datetime import datetime


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
            select ?prop ?value (count(distinct ?s) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                ?s rdf:type ?value .
            }
            group by ?prop ?value
            """
        
        self.range_query_template = prefixes + """
            select  ?prop ?value (count(*) as ?count) where {
                values ?prop { $prop }
                ?s ?prop ?o .
                optional { ?o rdf:type ?cl . }
                BIND(
                IF (bound(?cl) , ?cl,  IF ( isIRI(?o), 'rdfs:Resource', datatype(?o))
                ) as ?value)
            }
            group by ?prop ?value
            """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # sub class relationships
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

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

        self.rdfs_subClassOf[ns_reg.onto.CelloTerminology()] = ns_reg.skos.ConceptScheme()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # additional sub class relationships
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.more_rdfs_subClassOf = dict()
        self.more_rdfs_subClassOf[ns_reg.onto.Publication()] = ns_reg.fabio.Expression()
        self.more_rdfs_subClassOf[ns_reg.onto.Thesis()] = ns_reg.fabio.Thesis() 
        self.more_rdfs_subClassOf[ns_reg.onto.BachelorThesis()] = ns_reg.fabio.BachelorsThesis() 
        self.more_rdfs_subClassOf[ns_reg.onto.MasterThesis()] = ns_reg.fabio.MastersThesis() 
        self.more_rdfs_subClassOf[ns_reg.onto.DoctoralThesis()] = ns_reg.fabio.DoctoralThesis() 
        self.more_rdfs_subClassOf[ns_reg.onto.MedicalDegreeMasterThesis()] = ns_reg.fabio.Thesis()  
        self.more_rdfs_subClassOf[ns_reg.onto.MedicalDegreeThesis()] = ns_reg.fabio.Thesis()  
        self.more_rdfs_subClassOf[ns_reg.onto.PrivaDocentThesis()] = ns_reg.fabio.Thesis()  
        self.more_rdfs_subClassOf[ns_reg.onto.VeterinaryMedicalDegreeThesis()] = ns_reg.fabio.Thesis() 
        self.more_rdfs_subClassOf[ns_reg.onto.Patent()] = ns_reg.fabio.Patent()
        self.more_rdfs_subClassOf[ns_reg.onto.JournalArticle()] = ns_reg.fabio.JournalArticle() 
        self.more_rdfs_subClassOf[ns_reg.onto.Book()] = ns_reg.fabio.Book() 
        self.more_rdfs_subClassOf[ns_reg.onto.BookChapter()] = ns_reg.fabio.BookChapter() 
        self.more_rdfs_subClassOf[ns_reg.onto.TechnicalDocument()] = ns_reg.fabio.TechnicalReport() 
        self.more_rdfs_subClassOf[ns_reg.onto.ConferencePublication()] = ns_reg.fabio.ConferencePaper() 

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # sub property relationships
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_subPropertyOf = dict()
        self.rdfs_subPropertyOf[ns_reg.onto.creator()] = ns_reg.dcterms.creator()

        self.rdfs_subPropertyOf[ns_reg.onto.title()] = ns_reg.dcterms.title()        
        self.rdfs_subPropertyOf[ns_reg.onto.bookTitle()] = ns_reg.dcterms.title()
        self.rdfs_subPropertyOf[ns_reg.onto.documentTitle()] = ns_reg.dcterms.title()
        self.rdfs_subPropertyOf[ns_reg.onto.conferenceTitle()] = ns_reg.dcterms.title()
        self.rdfs_subPropertyOf[ns_reg.onto.documentSerieTitle()] = ns_reg.dcterms.title()
        
        self.rdfs_subPropertyOf[ns_reg.onto.more_specific_than()] = ns_reg.skos.broader()

        self.rdfs_subPropertyOf[ns_reg.onto.productId()] = ns_reg.dcterms.identifier()
        self.rdfs_subPropertyOf[ns_reg.onto.issn13()] = ns_reg.dcterms.identifier()
        self.rdfs_subPropertyOf[ns_reg.onto.hasDOI()] = ns_reg.dcterms.identifier()
        self.rdfs_subPropertyOf[ns_reg.onto.hasInternalId()] = ns_reg.dcterms.identifier()
        self.rdfs_subPropertyOf[ns_reg.onto.hasPMCId()] = ns_reg.fabio.hasPubMedCentralId()
        self.rdfs_subPropertyOf[ns_reg.onto.hasPubMedId()] = ns_reg.fabio.hasPubMedId()
        self.rdfs_subPropertyOf[ns_reg.onto.volume()] = ns_reg.up.volume()
        
        self.rdfs_subPropertyOf[ns_reg.onto.primaryAccession()] = ns_reg.onto.accession()
        self.rdfs_subPropertyOf[ns_reg.onto.secondaryAccession()] = ns_reg.onto.accession()
        self.rdfs_subPropertyOf[ns_reg.onto.accession()] = ns_reg.dcterms.identifier()
        
        self.rdfs_subPropertyOf[ns_reg.onto.name()] = ns_reg.rdfs.label()
        self.rdfs_subPropertyOf[ns_reg.onto.populationName()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.recommendedName()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.alternativeName()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.shortname()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.misspellingName()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.registeredName()] = ns_reg.onto.name()
        self.rdfs_subPropertyOf[ns_reg.onto.CellLineName()] = ns_reg.onto.name()
        
        
        
        

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # domain / ranges to remove
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_domain_to_remove = dict()
        self.rdfs_domain_to_remove[ns_reg.onto.accession()] = ns_reg.skos.Concept() 
        self.rdfs_domain_to_remove[ns_reg.onto.category()] = ns_reg.skos.Concept() 
        self.rdfs_domain_to_remove[ns_reg.onto.database()] = ns_reg.skos.Concept() 
        self.rdfs_domain_to_remove[ns_reg.onto.version()] = ns_reg.owl.NamedIndividual()
        self.rdfs_domain_to_remove[ns_reg.onto.more_specific_than()] = ns_reg.onto.Xref() 

        self.rdfs_range_to_remove = dict()
        self.rdfs_range_to_remove[ns_reg.onto.xref()] = ns_reg.skos.Concept() 
        self.rdfs_range_to_remove[ns_reg.onto.more_specific_than()] = ns_reg.onto.Xref() 



        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # non default labels for classes and properties
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_label = dict()
        self.rdfs_label[ns_reg.onto.HLATyping()] = "HLA typing"
        self.rdfs_label[ns_reg.onto.hlaTyping()] = "has HLA typing"
        self.rdfs_label[ns_reg.onto.MabIsotype()] = "Monoclonal antibody isotype"
        self.rdfs_label[ns_reg.onto.mabIsotype()] = "has monoclonal antibody isotype"
        self.rdfs_label[ns_reg.onto.mabTarget()] = "has monoclonal antibody target"
        self.rdfs_label[ns_reg.onto.cvclEntryCreated()] = "cellosaurus cell line record creation date"
        self.rdfs_label[ns_reg.onto.cvclEntryLastUpdated()] = "cellosaurus cell line record last update"
        self.rdfs_label[ns_reg.onto.cvclEntryVersion()] = "cellosaurus cell line record version"
        self.rdfs_label[ns_reg.onto.hasPMCId()] = "has PMC identifier"
        self.rdfs_label[ns_reg.onto.hasPubMedId()] = "has PubMed identifier"
        self.rdfs_label[ns_reg.onto.hasDOI()] = "has DOI identifier"
        self.rdfs_label[ns_reg.onto.msiValue()] = "has microsatellite instability value"
        self.rdfs_label[ns_reg.onto.productId()] = "product identifier"
        self.rdfs_label[ns_reg.onto.xref()] = "has cross-reference"
        self.rdfs_label[ns_reg.onto.Xref()] = "Cross-reference"
        self.rdfs_label[ns_reg.onto.CelloTerminology()] = "Cellosaurus terminology"


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # comments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.rdfs_comment = dict()
        # comments for classes
        self.rdfs_comment[ns_reg.onto.CellLine()] = "Cell line as defined in the Cellosaurus"
        # comments for props
        self.rdfs_comment[ns_reg.onto.recommendedName()] = "Most frequently the name of the cell line as provided in the original publication"
        self.rdfs_comment[ns_reg.onto.alternativeName()] = "Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"
        self.rdfs_comment[ns_reg.onto.more_specific_than()] = "Links two concepts. The subject concept is more specific than the object concept. The semantics is the similar to the skos:broader property but its label less ambiguous."


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_label(self, str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if str in self.rdfs_label:
            return self.rdfs_label[str]
        else:
            return self.build_default_label(str)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_default_label(self, prefixed_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if ":" in prefixed_name:
            str = prefixed_name.split(":")[1]
        else:
            str = prefixed_name

        # 1) insert space instead of "_" and on case change  
        chars = list()
        wasupper = False
        for ch in str:
            if ch.isupper() and not wasupper and len(chars)>0:
                chars.append(" ")
                chars.append(ch)
            elif ch == "_":
                chars.append(" ")
            else:
                chars.append(ch)
            wasupper = ch.isupper()
        sentence = "".join(chars).replace("  ", " ")
        words = sentence.split(" ")

        # 2) lower all words except first and those having all chars uppercase
        first = True
        new_words = list()
        for w in words:
            if first:
                first = False
                new_words.append(w)
            else:
                allUpper = True
                for ch in w:
                    if ch.islower(): allUpper = False
                if allUpper:
                    new_words.append(w)
                else:
                    new_words.append(w.lower())

        return " ".join(new_words)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_url(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        onto_url = ns_reg.onto.baseurl()
        if onto_url.endswith("#"): onto_url = onto_url[:-1]
        return onto_url


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_header(self, version="alpha"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()

        # append prefixes fefined in our namespace
        for ns in ns_reg.namespaces: lines.append(ns.getTtlPrefixDeclaration())
        lines.append("")

        # set last modification date for ontology
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        
        # set ontology URL
        onto_url = "<" + self.get_onto_url() + ">"
        
        # set ontology description
        onto_descr = """The Cellosaurus ontology describes the concepts used to build the Cellosaurus knowledge resource on cell lines. 
        The Cellosaurus attempts to describe all cell lines used in biomedical research."""
        
        # set ontology abstract
        onto_abstract = onto_descr

        # set preferred prefix for ontology
        onto_prefix = "cls" 

        # set ontology introduction
        onto_intro = onto_descr

        # Note: all the prefixes are declared in namespace.py but not necessarily all the properties because used only once...
        lines.append(onto_url)
        lines.append("    a owl:Ontology ;")
        lines.append("    " + ns_reg.rdfs.label() + " " + ns_reg.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    dcterms:created " + ns_reg.xsd.date("2024-07-30") + " ;")
        lines.append("    dcterms:modified " + ns_reg.xsd.date(date_string) + " ;")
        lines.append("    dcterms:description " + ns_reg.xsd.string3(onto_descr) + " ;")
        lines.append("    dcterms:license <http://creativecommons.org/licenses/by/4.0> ;")
        lines.append("    dcterms:title " + ns_reg.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    dcterms:versionInfo " + ns_reg.xsd.string(version) + " ;")
        lines.append("    dcterms:abstract " + ns_reg.xsd.string3(onto_abstract) + " ;")
        lines.append("    vann:preferredNamespacePrefix " + ns_reg.xsd.string(onto_prefix) + " ;")
        lines.append("    bibo:status <http://purl.org/ontology/bibo/status/published> ;")
        lines.append("    widoco:introduction " + ns_reg.xsd.string3(onto_intro) + " ;")
        lines.append("    .")
        lines.append("")
        return lines


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_classes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology Classes", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        for method_name in dir(ns_reg.onto):
            if callable(getattr(ns_reg.onto, method_name)):
                if method_name[0].isupper():
                    #print("method name", method_name)
                    method = getattr(ns_reg.onto, method_name)
                    class_name = method()
                    #print("class_name", class_name)
                    lines.append(class_name)
                    lines.append(f"    rdf:type owl:Class ;")
                    class_label =  ns_reg.xsd.string(self.build_label(class_name))
                    lines.append(f"    rdfs:label {class_label} ;")
                    parent_class = self.rdfs_subClassOf.get(class_name)
                    if parent_class is not None:
                        lines.append(f"    rdfs:subClassOf " + parent_class + " ;")
                    parent_class = self.more_rdfs_subClassOf.get(class_name)
                    if parent_class is not None:
                        lines.append(f"    rdfs:subClassOf " + parent_class + " ;")
                    class_comment = self.rdfs_comment.get(class_name)
                    if class_comment is not None:
                        class_comment =  ns_reg.xsd.string(class_comment)
                        lines.append(f"    rdfs:comment {class_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")
                    lines.append("    .")
                    lines.append("")
        return lines
        
    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # def set_contains_local_parent(self, some_set):
    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #     for el in some_set:
    #         if el.startswith(":"): return True
    #     return False

    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # def get_root_ancestors(self, some_class):
    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #     parents = self.rdfs_subClassOf.get(some_class) or []
    #     if len(parents)==0:
    #         return { some_class }
    #     else: 
    #         ancestors = set()
    #         for parent in parents:
    #             all_ancestors = self.get_root_ancestors(parent)
    #             has_local_parent = self.set_contains_local_parent(all_ancestors)
    #             for anc in all_ancestors:
    #                 if not has_local_parent or anc.startsWith(":"):
    #                     ancestors.add(anc)
    #                     print("added", anc)
    #             #ancestors.update(self.get_root_ancestors(parent))
    #                 else:
    #                     print("NOT added", anc)
    #         return ancestors


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
        for method_name in dir(ns_reg.onto):
            if callable(getattr(ns_reg.onto, method_name)):
                if method_name[0].islower():
                    # skip those below, they are not ontology terms but helper functions of the super class
                    if method_name in ["prefix", "baseurl", "getTtlPrefixDeclaration", "getSparqlPrefixDeclaration"]: continue 
                    method = getattr(ns_reg.onto, method_name)
                    prop_name = method()
                    prop_label =  ns_reg.xsd.string(self.build_label(prop_name))
                    prop_comment = self.rdfs_comment.get(prop_name)
                    parent_prop = self.rdfs_subPropertyOf.get(prop_name)

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

                    if parent_prop is not None:
                        lines.append(f"    rdfs:subPropertyOf " + parent_prop + " ;")

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

                    domain_to_remove = self.rdfs_domain_to_remove.get(prop_name)
                    if domain_to_remove is not None and domain_to_remove in domains: del domains[domain_to_remove]

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

                    if len(ranges)>1:
                        sr = self.get_simplified_classes(ranges)
                        if sr != ranges:
                            #lines.append("# SIMPLIFIED ranges")
                            ranges = sr

                    range_to_remove = self.rdfs_range_to_remove.get(prop_name)
                    if range_to_remove is not None and range_to_remove in ranges: del ranges[range_to_remove]

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
    # tests
    if 1==2:
        print(builder.build_label("this_is_DNA"))
        print(builder.build_label(ns_reg.onto.mabIsotype()))
        print(builder.build_label(ns_reg.onto.hasDOI()))
        print(builder.build_label(ns_reg.onto.cvclEntryCreated()))
        print(builder.build_label(ns_reg.onto.hlaTyping()))
        print(builder.build_label(ns_reg.onto.HLATyping()))
        print(builder.build_label(ns_reg.onto.AnecdotalComment()))
        print(builder.build_label(ns_reg.onto.anecdotalComment()))

        print(builder.get_root_ancestor(ns_reg.onto.Publication()))
        print(builder.get_root_ancestor(ns_reg.onto.MedicalDegreeMasterThesis()))
        print(builder.get_root_ancestor(ns_reg.onto.AnecdotalComment()))

    # real ontology generation
    else:  
        lines = list()
        lines.extend(builder.get_onto_header(version="1.0"))
        lines.extend(builder.get_classes())
        lines.extend(builder.get_props())
        for line in lines: print(line)