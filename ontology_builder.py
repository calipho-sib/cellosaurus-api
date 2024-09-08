from namespace import NamespaceRegistry as ns
from ApiCommon import log_it, split_string
from sparql_client import EndpointClient
import sys
from datetime import datetime
from tree_functions import Tree




#-------------------------------------------------
class OntologyBuilder:
#-------------------------------------------------


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.ontodata = {

                ns.onto.Publication(): { ns.rdfs.subClassOf() : { ns.fabio.Expression() },
                                        ns.skos.closeMatch() : { ns.up.Published_Citation()} },
                ns.onto.Thesis(): { ns.rdfs.subClassOf() : { ns.onto.Publication(), ns.fabio.Thesis() },
                                    ns.skos.closeMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.BachelorThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.BachelorsThesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.MasterThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.MastersThesis()  },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.DoctoralThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.DoctoralThesis()  },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.MedicalDegreeMasterThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }}, 
                ns.onto.MedicalDegreeThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis()   },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.PrivaDocentThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis()   },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }},
                ns.onto.VeterinaryMedicalDegreeThesis(): { ns.rdfs.subClassOf() : {ns.onto.Thesis(), ns.fabio.Thesis() },
                                            ns.skos.broadMatch() : { ns.up.Thesis_Citation() }}, 
                ns.onto.Patent(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.Patent() }},
                ns.onto.JournalArticle(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.JournalArticle() },
                                            ns.skos.closeMatch() : { ns.up.Journal_Citation() }}, 
                ns.onto.Book(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.Book()  },
                                            ns.skos.broadMatch() : { ns.up.Published_Citation() }},
                ns.onto.BookChapter(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.BookChapter() },
                                            ns.skos.closeMatch() : { ns.up.Book_Citation() }},
                ns.onto.TechnicalDocument(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.TechnicalReport() },
                                            ns.skos.broadMatch() : { ns.up.Citation() }},
                ns.onto.MiscellaneousDocument(): { ns.rdfs.subClassOf() : {ns.onto.Publication()  },
                                            ns.skos.broadMatch() : { ns.up.Citation() }},
                ns.onto.ConferencePublication(): { ns.rdfs.subClassOf() : {ns.onto.Publication(), ns.fabio.ConferencePaper() },
                                            ns.skos.broadMatch() : { ns.up.Published_Citation() }},

                ns.onto.GeneMutation() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation() }},
                ns.onto.RepeatExpansion() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.SimpleMutation() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.UnexplicitMutation() : { ns.rdfs.subClassOf() : { ns.onto.GeneMutation()  }},
                ns.onto.GeneFusion() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation()  }},
                ns.onto.GeneAmplification() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation() }}, 
                ns.onto.GeneDuplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneTriplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneQuarduplication() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification()  }},
                ns.onto.GeneExtensiveAmplification() : { ns.rdfs.subClassOf() : { ns.onto.GeneAmplification() }}, 
                ns.onto.GeneDeletion() : { ns.rdfs.subClassOf() : { ns.onto.SequenceVariation()  }},

                ns.onto.CelloTerminology() : { ns.rdfs.subClassOf() : { ns.skos.ConceptScheme() }},


                ns.onto.accession(): { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.primaryAccession(): { ns.rdfs.subPropertyOf() : { ns.onto.accession() }},
                ns.onto.secondaryAccession(): { ns.rdfs.subPropertyOf() : { ns.onto.accession() }},

                ns.onto.name() : { ns.rdfs.subPropertyOf() : { ns.foaf.name() }},
                ns.onto.registeredName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.misspellingName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.populationName() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.shortname() : { ns.rdfs.subPropertyOf() : { ns.onto.name() }},
                ns.onto.recommendedName() : { ns.rdfs.subPropertyOf() : { ns.skos.prefLabel(), ns.onto.name() }},
                ns.onto.alternativeName() : { ns.rdfs.subPropertyOf() : { ns.skos.altLabel(), ns.onto.name() }},

                ns.onto.creator() : { ns.rdfs.subPropertyOf() : { ns.dcterms.creator() }},

                ns.onto.title() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title()         }},
                ns.onto.bookTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.documentTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.conferenceTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                ns.onto.documentSerieTitle() : { ns.rdfs.subPropertyOf() : { ns.dcterms.title() }},
                
                ns.onto.more_specific_than() : { ns.rdfs.subPropertyOf() : { ns.skos.broader() }},

                ns.onto.productId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.issn13() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.hasDOI() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.bibo.doi() }},
                ns.onto.hasInternalId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier() }},
                ns.onto.hasPMCId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.fabio.hasPubMedCentralId() }},
                ns.onto.hasPubMedId() : { ns.rdfs.subPropertyOf() : { ns.dcterms.identifier(), ns.fabio.hasPubMedId() }},
                ns.onto.volume() : { ns.rdfs.subPropertyOf() : { ns.up.volume() }},
                
                # ns.xsd.dateDataType() : { ns.rdfs.subClassOf() : { ns.rdfs.Literal() }}, hack not needed 
            }

        # build tree with local child - parent relationships based on rdfs:subClassOf()
        edges = dict()
        for child in self.ontodata:
            child_rec = self.ontodata.get(child) or {}
            parents = child_rec.get(ns.rdfs.subClassOf()) or {}
            for parent in parents:
                if self.term_is_local(parent): 
                    edges[child]=parent
        self.tree = Tree(edges)                    

        lines = list()
        for this_ns in ns.namespaces: lines.append(this_ns.getSparqlPrefixDeclaration())
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
        # domain / ranges to remove
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_domain_to_remove = dict()
        self.rdfs_domain_to_remove[ns.onto.accession()] = ns.skos.Concept() 
        self.rdfs_domain_to_remove[ns.onto.category()] = ns.skos.Concept() 
        self.rdfs_domain_to_remove[ns.onto.database()] = ns.skos.Concept() 
        self.rdfs_domain_to_remove[ns.onto.version()] = ns.owl.NamedIndividual()
        self.rdfs_domain_to_remove[ns.onto.more_specific_than()] = ns.onto.Xref() 

        self.rdfs_range_to_remove = dict()
        self.rdfs_range_to_remove[ns.onto.xref()] = ns.skos.Concept() 
        self.rdfs_range_to_remove[ns.onto.more_specific_than()] = ns.onto.Xref() 



        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # non default labels for classes and properties
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.rdfs_label = dict()
        self.rdfs_label[ns.onto.HLATyping()] = "HLA typing"
        self.rdfs_label[ns.onto.hlaTyping()] = "has HLA typing"
        self.rdfs_label[ns.onto.MabIsotype()] = "Monoclonal antibody isotype"
        self.rdfs_label[ns.onto.mabIsotype()] = "has monoclonal antibody isotype"
        self.rdfs_label[ns.onto.mabTarget()] = "has monoclonal antibody target"
        self.rdfs_label[ns.onto.cvclEntryCreated()] = "cellosaurus cell line record creation date"
        self.rdfs_label[ns.onto.cvclEntryLastUpdated()] = "cellosaurus cell line record last update"
        self.rdfs_label[ns.onto.cvclEntryVersion()] = "cellosaurus cell line record version"
        self.rdfs_label[ns.onto.hasPMCId()] = "has PMC identifier"
        self.rdfs_label[ns.onto.hasPubMedId()] = "has PubMed identifier"
        self.rdfs_label[ns.onto.hasDOI()] = "has DOI identifier"
        self.rdfs_label[ns.onto.msiValue()] = "has microsatellite instability value"
        self.rdfs_label[ns.onto.productId()] = "product identifier"
        self.rdfs_label[ns.onto.xref()] = "has cross-reference"
        self.rdfs_label[ns.onto.Xref()] = "Cross-reference"
        self.rdfs_label[ns.onto.CelloTerminology()] = "Cellosaurus terminology"


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # comments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.rdfs_comment = dict()
        # comments for classes
        self.rdfs_comment[ns.onto.CellLine()] = "Cell line as defined in the Cellosaurus"
        # comments for props
        self.rdfs_comment[ns.onto.recommendedName()] = "Most frequently the name of the cell line as provided in the original publication"
        self.rdfs_comment[ns.onto.alternativeName()] = "Different synonyms for the cell line, including alternative use of lower and upper cases characters. Misspellings are not included in synonyms"
        self.rdfs_comment[ns.onto.more_specific_than()] = "Links two concepts. The subject concept is more specific than the object concept. The semantics is the similar to the skos:broader property but its label less ambiguous."


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
        onto_url = ns.onto.baseurl()
        if onto_url.endswith("#"): onto_url = onto_url[:-1]
        return onto_url


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_header(self, version="alpha"):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()

        # append prefixes fefined in our namespace
        for this_ns in ns.namespaces: lines.append(this_ns.getTtlPrefixDeclaration())
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
        lines.append("    " + ns.rdfs.label() + " " + ns.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    dcterms:created " + ns.xsd.date("2024-07-30") + " ;")
        lines.append("    dcterms:modified " + ns.xsd.date(date_string) + " ;")
        lines.append("    dcterms:description " + ns.xsd.string3(onto_descr) + " ;")
        lines.append("    dcterms:license <http://creativecommons.org/licenses/by/4.0> ;")
        lines.append("    dcterms:title " + ns.xsd.string("Cellosaurus ontology") + " ;")
        lines.append("    dcterms:versionInfo " + ns.xsd.string(version) + " ;")
        lines.append("    dcterms:abstract " + ns.xsd.string3(onto_abstract) + " ;")
        lines.append("    vann:preferredNamespacePrefix " + ns.xsd.string(onto_prefix) + " ;")
        lines.append("    bibo:status <http://purl.org/ontology/bibo/status/published> ;")
        lines.append("    widoco:introduction " + ns.xsd.string3(onto_intro) + " ;")
        lines.append("    .")
        lines.append("")
        return lines


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_classes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology Classes", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        for method_name in dir(ns.onto):
            if callable(getattr(ns.onto, method_name)):
                if method_name[0].isupper():
                    #print("method name", method_name)
                    method = getattr(ns.onto, method_name)
                    class_name = method()
                    #print("class_name", class_name)
                    lines.append(class_name)
                    lines.append(f"    rdf:type owl:Class ;")
                    class_label =  ns.xsd.string(self.build_label(class_name))
                    lines.append(f"    rdfs:label {class_label} ;")

                    for p in self.ontodata.get(class_name) or {}:
                        for o in self.ontodata[class_name][p]:
                            lines.append(f"    {p} {o} ;")

                    class_comment = self.rdfs_comment.get(class_name)
                    if class_comment is not None:
                        class_comment =  ns.xsd.string(class_comment)
                        lines.append(f"    rdfs:comment {class_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")
                    lines.append("    .")
                    lines.append("")
        return lines
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term_is_local(self, term):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return term.startswith(":")


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_props(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = [ "#", "# Cellosaurus ontology properties", "#" , "" ]
        onto_url = self.get_onto_url()
        onto_url = "<" + onto_url + ">"
        prop_count = 0
        for method_name in dir(ns.onto):
            if callable(getattr(ns.onto, method_name)):
                if method_name[0].islower():
                    # skip those below, they are not ontology terms but helper functions of the super class
                    if method_name in ["prefix", "baseurl", "getTtlPrefixDeclaration", "getSparqlPrefixDeclaration", "getSQLforVirtuoso"]: continue 
                    method = getattr(ns.onto, method_name)
                    prop_name = method()
                    prop_label =  ns.xsd.string(self.build_label(prop_name))
                    prop_comment = self.rdfs_comment.get(prop_name)

                    #if prop_count > 10: break
                    prop_count += 1

                    log_it("DEBUG", "querying prop_name", prop_name, "domains")
                    domain_dic = dict()
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
                        domain_dic[value]=count

                    log_it("DEBUG", "querying prop_name", prop_name, "ranges")
                    range_dic = dict()
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
                        range_dic[value]=count

                    # prop type
                    prop_types = set() # we should have a single item in this set (otherwise OWL reasoners dislike it)
                    for r in range_dic:
                        if r.startswith("xsd:") or r == ns.rdfs.Literal(): 
                            prop_types.add("owl:DatatypeProperty") 
                        else:
                            prop_types.add("owl:ObjectProperty") 
                    lines.append(prop_name)
                    lines.append("    a rdf:Property ;")
                    for typ in prop_types: lines.append("    a " + typ + " ;")

                    #prop label, comment, definition
                    lines.append(f"    rdfs:label {prop_label} ;")
                    if prop_comment is not None:
                        prop_comment =  ns.xsd.string(prop_comment)
                        lines.append(f"    rdfs:comment {prop_comment} ;")
                    lines.append(f"    rdfs:isDefinedBy {onto_url} ;")

                    # add props declared in onto data
                    for p in self.ontodata.get(prop_name) or {}:
                        for o in self.ontodata[prop_name][p]:
                            lines.append(f"    {p} {o} ;")

                    # ttl comment about domain classes found in data
                    tmp = ["domain classes found in data are"]
                    for k in domain_dic: tmp.append(f"{k}({domain_dic[k]})")
                    for line in split_string(" ".join(tmp), 120):
                        lines.append("#   " + line)

                    # prop domain definition
                    domain_set = set(domain_dic.keys())
                    if len(domain_set)>1: 
                        sd = self.tree.get_close_parent_set(domain_set)
                        if sd != domain_set: domain_set = sd

                    domain_to_remove = self.rdfs_domain_to_remove.get(prop_name)
                    if domain_to_remove is not None: domain_set = domain_set - { domain_to_remove }

                    if len(domain_set)==1:
                        name = domain_set.pop()
                        line = "    rdfs:domain " + name + " ;"
                        lines.append(line)
                    elif len(domain_set)>1:
                        lines.append("    rdfs:domain [ a owl:Class ; owl:unionOf (")
                        for name in domain_set:
                            line = "        " + name
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    # ttl comment about prop range
                    tmp = ["range classes found in data are"]
                    for k in range_dic: tmp.append(f"{k}({range_dic[k]})")
                    for line in split_string(" ".join(tmp), 120):
                        lines.append("#   " + line)

                    # prop range definition
                    range_set = set(range_dic.keys())
                    if len(range_set)>1:
                        sr = self.tree.get_close_parent_set(range_set)
                        if sr != range_set: range_set = sr

                    # hack to replace xsd:date with rdfs:Literal to be OWL2 frienly                    
                    if ns.xsd.dateDataType() in range_set:
                        range_set = range_set - { ns.xsd.dateDataType() }
                        range_set.add(ns.rdfs.Literal())
                        
                    range_to_remove = self.rdfs_range_to_remove.get(prop_name)
                    if range_to_remove is not None:
                        range_set = range_set - { range_to_remove } 

                    if len(range_set)==1:
                        name = range_set.pop()
                        line = "    rdfs:range " + name + " ;"
                        lines.append(line)
                    elif len(range_set)>1:
                        lines.append("    rdfs:range [ a owl:Class ; owl:unionOf (")
                        for name in range_set:
                            line = "        " + name
                            lines.append(line)
                        lines.append("        )")
                        lines.append("    ] ;")                             

                    lines.append("    .")
                    lines.append("")

        return lines


# --------------------------------------------
if __name__ == '__main__':
# --------------------------------------------

    # print(ontodata)
    # builder = OntologyBuilder()
    # node_set = {
    #     #":GeneMutation",
    #     #":Patent",
    #     #":MedicalDegreeThesis", 
    #     #":MedicalDegreeMasterThesis",
    #     #":DoctoralThesis",
    #     #":MasterThesis",
    #     #":TechnicalDocument", 
    #     #":BachelorThesis", 
    #     #":VeterinaryMedicalDegreeThesis",
    #     #":ConferencePublication",
    #     #":BookChapter",
    #     #":PrivaDocentThesis",
    #     #":Book",
    #     #":MiscellaneousDocument",
    #     #":JournalArticle"
    # }
    # result = builder.tree.get_close_parent_set(node_set)
    # print(result)
    # # c1 = ns.onto.BachelorThesis()
    # # c2 = ns.onto.Publication()
    # # c3 = ns.onto.AnatomicalElement()
    # # print(builder.tree.get_close_parent_set({c1,c2,c3}))    
    # #print("remote root if thesis", builder.get_root_ancestors(ns.onto.Thesis(), locality=False))
    # sys.exit()

    builder = OntologyBuilder()
    # tests
    if 1==2:
        print(builder.build_label("this_is_DNA"))
        print(builder.build_label(ns.onto.mabIsotype()))
        print(builder.build_label(ns.onto.hasDOI()))
        print(builder.build_label(ns.onto.cvclEntryCreated()))
        print(builder.build_label(ns.onto.hlaTyping()))
        print(builder.build_label(ns.onto.HLATyping()))
        print(builder.build_label(ns.onto.AnecdotalComment()))
        print(builder.build_label(ns.onto.anecdotalComment()))

        print(builder.get_root_ancestor(ns.onto.Publication()))
        print(builder.get_root_ancestor(ns.onto.MedicalDegreeMasterThesis()))
        print(builder.get_root_ancestor(ns.onto.AnecdotalComment()))

    # real ontology generation
    else:  
        lines = list()
        lines.extend(builder.get_onto_header(version="1.0"))
        lines.extend(builder.get_classes())
        lines.extend(builder.get_props())
        for line in lines: print(line)