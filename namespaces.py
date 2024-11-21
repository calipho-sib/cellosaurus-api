import hashlib
from ApiCommon import get_rdf_base_IRI, get_help_base_IRI


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Term:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ns, id):
        self.ns = ns; self.id = id; self.iri = ":".join([ns, id]); self.props = dict()

    def __str__(self) -> str:
        return ":".join([self.ns, self.id])
    
    def __repr__(self) -> str:        
        return f"Term({self.iri}, {self.props})"

    def isA(self, owlType):
        value_set = self.props.get("rdf:type") or set()
        result = owlType in value_set
        #print(">>>", self.iri, result, owlType, "-- in ? --", value_set)
        return result

    def ttl_lines(self):
        ordered_props = [
            "a", "rdf:type", "rdfs:label", "rdfs:comment", "rdfs:subClassOf", "rdfs:subPropertyOf",
            "owl:equivalentClass", "owl:equivalentProperty","owl:sameAs", 
            "skos:exactMatch", "skos:closeMatch", "skos:broadMatch", 
            "domain_comments", "rdfs:domain", "range_comments","rdfs:range", "rdfs:seeAlso", "rdfs:isDefinedBy"]
        lines = list()
        lines.append(self.iri)
        label = self.props.get("rdfs:label")
        if label is None:
            if self.ns == "cello" or True:
                # default label built upon id
                label = "".join(["\"", self.build_default_label(),"\"", "^^xsd:string"])
                self.props["rdfs:label"] = { label }
            else:
                # label built upon IRI for external ontologies (nicer in widoco)
                iri_like_label = ":".join([self.ns, self.id])                   
                label = "".join(["\"", iri_like_label,"\"", "^^xsd:string"])
                self.props["rdfs:label"] = { label }

        # build composite comment including label, skos relationships (otherwise invisible in widoco)
        # and textual comment if any
        self.build_composite_comment()

        for pk in ordered_props:
            value_set = self.props.get(pk)
            if value_set is None or value_set == set(): continue
            if pk in ["rdfs:domain", "rdfs:range"] and len(value_set) > 1:
                lines.append(f"    {pk} [ a owl:Class ; owl:unionOf (")
                for value in value_set:
                    line = "        " + value
                    lines.append(line)
                lines.append("        )")
                lines.append("    ] ;")                             
            elif pk in ["range_comments", "domain_comments"]:
                for value in value_set:
                    lines.append(value)
            else:
                values = " , ".join(value_set)
                lines.append(f"    {pk} {values} ;")
        lines.append("    .")
        lines.append("")                        
        return lines

    def unwrap_xsd_string(self, str):
        tmp = str
        # remove left part of the wrapper
        if tmp.startswith("\"\"\""): tmp = tmp[3:]
        elif tmp.startswith("\""): tmp = tmp[1:]
        # remove right part of the wrapper
        if tmp.endswith("\"\"\"^^xsd:string"): tmp = tmp[:-15]
        elif tmp.endswith("\"^^xsd:string"): tmp = tmp[:-13]
        tmp = self.unescape_string(tmp)
        return tmp
        
    def unescape_string(self, str):
        str = str.replace("\\\\","\\")      # inverse of escape backslashes with double backslashes (\ => \\)
        str = str.replace("\\\"", "\"")     # inverse of escape double-quotes (" => \")
        return str

    def build_composite_comment(self):
        parts = list()
        # if a real comment preexist (see ontology_builder.describe_comments()), retrieve it
        existing_elems = list(self.props.get("rdfs:comment") or set())
        real_comment = None
        if len(existing_elems) > 0: 
            real_comment = self.unwrap_xsd_string(existing_elems[0])
        # if term is from external ns, add original label
        label = None
        if self.ns != "cello":
            label_list = list(self.props.get("rdfs:label"))
            if len(label_list) > 0: label = self.unwrap_xsd_string(label_list[0])
        # add skos relationships to other terms
        for pk in ["skos:exactMatch", "skos:closeMatch", "skos:broadMatch", "rdfs:seeAlso"]:
            for elem in self.props.get(pk) or set():
                content = " ".join([pk, elem])
                parts.append(content)
        if label is not None: 
            parts.insert(0, label)
        if real_comment is not None:
            parts.append(real_comment)
        composite_content = " - ".join(parts)
        quote = "\""
        if "\"" in composite_content: quote = "\"\"\"" 
        result = "".join([quote, composite_content, quote, "^^xsd:string"])
        self.props["rdfs:comment"] = { result }


    def build_default_label(self):
        # 1) insert space instead of "_" and on case change  
        chars = list()
        wasupper = False
        for ch in self.id:
            if ch.isupper() and not wasupper and len(chars)>0: chars.append(" "); chars.append(ch)
            elif ch == "_": chars.append(" ")
            else: chars.append(ch)
            wasupper = ch.isupper()
        sentence = "".join(chars).replace("  ", " ")
        words = sentence.split(" ")
        # 2) lower all words except first and those having all chars uppercase
        first = True
        new_words = list()
        for w in words:
            if first: first = False; new_words.append(w)
            else:
                allUpper = True
                for ch in w:
                    if ch.islower(): allUpper = False
                if allUpper: new_words.append(w)
                else: new_words.append(w.lower())
        return " ".join(new_words)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# namespace ancestor class, handles prefix and base URL
class BaseNamespace:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, prefix, baseurl):
        self.pfx = prefix; self.url = baseurl; self.terms = dict()

    def getTtlPrefixDeclaration(self): return "".join(["@prefix ", self.pfx, ": <", self.url, "> ."])
    def getSparqlPrefixDeclaration(self): return "".join(["PREFIX ", self.pfx, ": <", self.url, "> "])
    def getSQLforVirtuoso(self): return f"insert into DB.DBA.SYS_XML_PERSISTENT_NS_DECL values ('{self.pfx}', '{self.url}');"

    def describe(self, subj_iri, prop_iri, value):
        #print(">>>", subj_iri, prop_iri,value)
        id = subj_iri.split(":")[1]
        t: Term = self.terms[id]
        if prop_iri not in t.props: t.props[prop_iri] = set()
        t.props[prop_iri].add(value)

    def term(self, iri) -> Term: 
        id = iri.split(":")[1]
        return self.terms.get(id)

    def registerTerm(self, id, p=None, v=None):
        if id not in self.terms: 
            t = Term(self.pfx, id)
            t.props["rdfs:isDefinedBy"] = { self.pfx + ":" }
            if p is not None and v is not None: t.props[p] = v
            self.terms[id] = t
        return self.terms[id].iri

    def registerClass(self, id, label=None):
        iri = self.registerTerm(id, "rdf:type", { "owl:Class" })
        if label is not None: 
            self.describe(iri, "rdfs:label", f"\"{label}\"^^xsd:string")
        return iri
    
    def registerProperty(self, id):
        return self.registerTerm(id, "rdf:type", { "rdf:Property" })

    def registerDatatypeProperty(self, id):
        return self.registerTerm(id, "rdf:type", { "rdf:Property", "owl:DatatypeProperty" })

    def registerObjectProperty(self, id):
        return self.registerTerm(id, "rdf:type", { "rdf:Property", "owl:ObjectProperty" })

    def registerAnnotationProperty(self, id):
        return self.registerTerm(id, "rdf:type", { "rdf:Property", "owl:AnnotationProperty" })


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class XsdNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(XsdNamespace, self).__init__("xsd", "http://www.w3.org/2001/XMLSchema#")
        self.dateDataType = self.registerTerm("date")

    def escape_string(self, str):
        str = str.replace("\\","\\\\")      # escape backslashes with double backslashes (\ => \\)
        str = str.replace("\"", "\\\"")     # escape double-quotes (" => \")
        return str
    def string(self, str):
        if '"' in str: return self.string3(str) # string datatype with triple quotes allow escape chars like \n \t etc.
        else: return self.string1(str)
    def string1(self, str): return "".join(["\"", self.escape_string(str), "\"^^xsd:string"])
    def string3(self, str): return "".join(["\"\"\"", self.escape_string(str), "\"\"\"^^xsd:string"])
    def date(self, str): return "".join(["\"", str, "\"^^xsd:date"])
    def integer(self, int_number): return str(int_number)
    def float(self, float_number): return "".join(["\"", str(float_number), "\"^^xsd:float"])
    def boolean(self, boolean_value): return str(boolean_value).lower() 


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(RdfNamespace, self).__init__("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.type = self.registerTerm("type")
        self.Property = self.registerTerm("Property")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(RdfsNamespace, self).__init__("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        self.Class = self.registerTerm("Class")
        self.subClassOf = self.registerTerm("subClassOf")
        self.subPropertyOf = self.registerTerm("subPropertyOf")
        self.comment = self.registerTerm("comment")
        self.label = self.registerTerm("label")
        self.domain = self.registerTerm("domain")
        self.range = self.registerTerm("range")
        self.seeAlso = self.registerTerm("seeAlso")
        self.isDefinedBy = self.registerTerm("isDefinedBy")
        self.Literal = self.registerTerm("Literal")
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OwlNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OwlNamespace, self).__init__("owl", "http://www.w3.org/2002/07/owl#")
        self.Class  = self.registerTerm("Class")
        self.AnnotationProperty  = self.registerTerm("AnnotationProperty")
        self.DatatypeProperty  = self.registerTerm("DatatypeProperty")
        self.FunctionalProperty  = self.registerTerm("FunctionalProperty")
        self.NamedIndividual  = self.registerTerm("NamedIndividual")
        self.ObjectProperty  = self.registerTerm("ObjectProperty")
        self.TransitiveProperty  = self.registerTerm("TransitiveProperty")
        self.allValuesFrom  = self.registerTerm("allValuesFrom")
        self.sameAs  = self.registerTerm("sameAs")
        self.unionOf  = self.registerTerm("unionOf")
        self.equivalentClass  = self.registerTerm("equivalentClass")
        self.equivalentProperty  = self.registerTerm("equivalentProperty")
        self.versionInfo  = self.registerTerm("versionInfo")
        self.Ontology  = self.registerTerm("Ontology")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SkosNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(SkosNamespace, self).__init__("skos", "http://www.w3.org/2004/02/skos/core#")
        self.Concept = self.registerTerm("Concept")
        self.ConceptScheme = self.registerTerm("ConceptScheme")
        self.inScheme = self.registerTerm("inScheme")
        self.notation = self.registerTerm("notation")
        self.prefLabel = self.registerTerm("prefLabel")
        self.altLabel = self.registerTerm("altLabel")
        self.broader = self.registerTerm("broader")
        self.exactMatch = self.registerTerm("exactMatch")
        self.closeMatch = self.registerTerm("closeMatch")
        self.broadMatch = self.registerTerm("broadMatch")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FabioNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(FabioNamespace, self).__init__("fabio", "http://purl.org/spar/fabio/")
    
        self.Expression = self.registerClass("Expression")
        self.Thesis = self.registerClass("Thesis")
        self.BachelorsThesis = self.registerClass("BachelorsThesis", label = "Bachelor's thesis")
        self.MastersThesis = self.registerClass("MastersThesis", label = "Master's thesis")
        self.DoctoralThesis = self.registerClass("DoctoralThesis")
        self.PatentDocument = self.registerClass("PatentDocument")
        self.JournalArticle = self.registerClass("JournalArticle")
        self.Book = self.registerClass("Book")
        self.BookChapter = self.registerClass("BookChapter")
        self.ConferencePaper = self.registerClass("ConferencePaper")
        self.ReportDocument = self.registerClass("ReportDocument")
        self.hasPubMedCentralId = self.registerDatatypeProperty("hasPubMedCentralId")
        self.hasPubMedId = self.registerDatatypeProperty("hasPubMedId")
        self.hasPublicationYear = self.registerDatatypeProperty("hasPublicationYear")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class UniProtCoreNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(UniProtCoreNamespace, self).__init__("up", "http://purl.uniprot.org/core/")

        self.Citation = self.registerClass("Citation")
        self.Published_Citation = self.registerClass("Published_Citation")
        self.Patent_Citation = self.registerClass("Patent_Citation")
        self.Thesis_Citation = self.registerClass("Thesis_Citation")
        self.Book_Citation = self.registerClass("Book_Citation", label="Book chapter citation")
        self.Journal_Citation = self.registerClass("Journal_Citation", label = "Journal article citation")    
        
        self.Annotation = self.registerClass("Annotation")
        self.Database = self.registerClass("Database")
        self.Protein = self.registerClass("Protein")

        self.annotation = self.registerObjectProperty("annotation")
        self.volume = self.registerDatatypeProperty("volume")
        self.title = self.registerDatatypeProperty("title")

        #self.version = self.registerDatatypeProperty("version")   # warning: invompatible domain (Protein, Sequence, Cluster)
        #self.modified = self.registerDatatypeProperty("modified") # warning: incompatible domain (Protein, Sequence, Cluster)
        #self.created = self.registerDatatypeProperty("created")   # warning: incompatible domain (Protein, Sequence, Cluster)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ShaclNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(ShaclNamespace, self).__init__("sh", "http://www.w3.org/ns/shacl#")
        self.declare = self.registerTerm("declare")
        self._prefix = self.registerTerm("prefix")
        self.namespace = self.registerTerm("namespace")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WikidataWdNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(WikidataWdNamespace, self).__init__("wd", "http://www.wikidata.org/entity/")
        self.P3289_AC = self.registerDatatypeProperty("P3289")
        self.P3578_OI = self.registerObjectProperty("P3578")   
        self.P9072_OX = self.registerObjectProperty("P9072")
        self.P5166_DI = self.registerObjectProperty("P5166")
        self.P3432_HI = self.registerObjectProperty("P3432")
        self.P21_SX = self.registerObjectProperty("P21") # could not figure out how sex is related to cell lines in wikidata

        # cell line classes with label as found in cellosaurus.txt
        self.Q23058136 = self.registerClass("Q23058136", label="Cancer cell line")
        self.Q27653145 = self.registerClass("Q27653145", label="Conditionally immortalized cell line")
        self.Q107102664 = self.registerClass("Q107102664", label="Embryonic stem cell")
        self.Q27627225 = self.registerClass("Q27627225", label="Factor-dependent cell line")
        self.Q27671617 = self.registerClass("Q27671617", label="Finite cell line")
        self.Q27555050 = self.registerClass("Q27555050", label="Hybrid cell line")
        self.Q27554370 = self.registerClass("Q27554370", label="Hybridoma")
        self.Q107103143 = self.registerClass("Q107103143", label="Induced pluripotent stem cell")
        self.Q107103129 = self.registerClass("Q107103129", label="Somatic stem cell")
        self.Q27555319 = self.registerClass("Q27555319", label="Spontaneously immortalized cell line")
        self.Q27671698 = self.registerClass("Q27671698", label="Stromal cell line")
        self.Q27653701 = self.registerClass("Q27653701", label="Telomerase immortalized cell line")
        self.Q27555384 = self.registerClass("Q27555384", label="Transformed cell line")
        self.CellLine = self.registerClass("Q21014462", label="Cell line") # with human readable var name because used at several locations


    def IRI(self, ac): return "wd:" + ac


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WikidataWdtNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(WikidataWdtNamespace, self).__init__("wdt", "http://www.wikidata.org/prop/direct/")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OaNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OaNamespace, self).__init__("oa", "http://www.w3.org/ns/oa#")
        self.Annotation = self.registerClass("Annotation")


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class W3OrgNamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def __init__(self): 
#         super(W3OrgNamespace, self).__init__("org", "http://www.w3.org/ns/org#")
#         self.Organization = self.registerClass("Organization")
#         self.memberOf = self.registerTerm("memberOf")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SchemaOrgNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(SchemaOrgNamespace, self).__init__("schema", "https://schema.org/")
        self.location = self.registerDatatypeProperty("location")   # only a rdf:Property in original ontology but useful for protege, widoco, ...
        self.memberOf = self.registerObjectProperty("memberOf")     # only a rdf:Property in original ontology but useful for protege, widoco, ...
        self.Organization = self.registerClass("Organization")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FoafNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(FoafNamespace, self).__init__("foaf", "http://xmlns.com/foaf/0.1/")
        self.Agent =        self.registerClass("Agent")
        self.Person =       self.registerClass("Person")
        self.name =         self.registerDatatypeProperty("name")
        self.Organization = self.registerClass("Organization")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class DctermsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(DctermsNamespace, self).__init__("dcterms", "http://purl.org/dc/terms/")
        self.created =      self.registerAnnotationProperty("created")
        self.modified =     self.registerAnnotationProperty("modified")
        self.hasVersion =   self.registerAnnotationProperty("hasVersion")
        self.description =  self.registerDatatypeProperty("description")
        self.license =      self.registerDatatypeProperty("license")
        self.abstract =     self.registerDatatypeProperty("abstract")
        self.title =        self.registerDatatypeProperty("title")
        self.creator =      self.registerObjectProperty("creator")
        self.publisher =    self.registerObjectProperty("publisher")
        self.contributor =  self.registerObjectProperty("contributor")
        self.identifier =   self.registerDatatypeProperty("identifier")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class VannNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(VannNamespace, self).__init__("vann", "http://purl.org/vocab/vann/")
        self.preferredNamespacePrefix = self.registerTerm("preferredNamespacePrefix")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BiboNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(BiboNamespace, self).__init__("bibo", "http://purl.org/ontology/bibo/")
        self.status = self.registerTerm("status")
        self.doi = self.registerTerm("doi")
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WidocoNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(WidocoNamespace, self).__init__("widoco", "https://w3id.org/widoco/vocab#")
        self.introduction = self.registerTerm("introduction")
        self.rdfxmlSerialization = self.registerTerm("rdfxmlSerialization")
        self.turtleSerialization = self.registerTerm("turtleSerialization")
        self.ntSerialization = self.registerTerm("ntSerialization")
        self.jsonldSerialization = self.registerTerm("jsonldSerialization")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BAONamespace(BaseNamespace):
    def __init__(self): super(BAONamespace, self).__init__("BAO", "http://www.bioassayontology.org/bao#BAO_")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BTONamespace(BaseNamespace):
    def __init__(self): super(BTONamespace, self).__init__("BTO", "http://purl.obolibrary.org/obo/BTO_")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CLONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(CLONamespace, self).__init__("CLO", "http://purl.obolibrary.org/obo/CLO_")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NCItNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(NCItNamespace, self).__init__("NCIt", "http://purl.obolibrary.org/obo/NCIT_")
        self.C17262 = self.registerClass("C17262", label="X-ray")             # genome modification method subclass
        self.C44386 = self.registerClass("C44386", label="Gamma radiation")   # genome modification method subclass


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OBINamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OBINamespace, self).__init__("OBI", "http://purl.obolibrary.org/obo/OBI_")

        # most generic class for genome modification methods and its subclasses
        self.GenomeModificationMethod = self.registerClass("0600043", label="Genome modification method")  
        self._0001152 = self.registerClass("0001152", label="Transfection")   
        self._0001154 = self.registerClass("0001154", label="Mutagenesis")
        self._0002626 = self.registerClass("0002626", label="siRNA knockdown")
        self._0003134 = self.registerClass("0003134", label="TALEN")
        self._0003135 = self.registerClass("0003135", label="ZFN")
        self._0003137 = self.registerClass("0003137", label="Gene trap")
        self._0600059 = self.registerClass("0600059", label="Transduction")

        self._0001404 = self.registerClass("0001404", label="Genetic characteristics information")
        self._0001364 = self.registerClass("0001364", label="Genetic alteration information")
        self._0001225 = self.registerClass("0001225", label="Genetic population background information")
                

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OMITNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OMITNamespace, self).__init__("OMIT", "http://purl.obolibrary.org/obo/OMIT_")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FBcvNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(FBcvNamespace, self).__init__("FBcv", "http://purl.obolibrary.org/obo/FBcv_")
        self.Database = self.registerClass("0000790")
        self._0003008 = self.registerClass("0003008", label="CRISPR/Cas9")   # genome modification method subclass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OGGNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OGGNamespace, self).__init__("OGG", "http://purl.obolibrary.org/obo/OGG_")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class PubMedNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(PubMedNamespace, self).__init__("pubmed", "https://www.ncbi.nlm.nih.gov/pubmed/")





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurCellLineNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OurCellLineNamespace, self).__init__("cvcl", get_rdf_base_IRI() + "/cvcl/")
    def IRI(self, primaryAccession): return "cvcl:" + primaryAccession

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurXrefNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_dict = dict()
    def __init__(self): 
        super(OurXrefNamespace, self).__init__("xref", get_rdf_base_IRI() + "/xref/")
    def cleanDb(self, db):
        return db.replace("/", "-") # necessary for db="IPD-IMGT/HLA" otherwise IRI contains SLASH which is forbidden
    def IRI(self, db, ac, props, store=True):
        our_dict = OurXrefNamespace.dbac_dict
        # we expect to get props as a string like: cat={cat}|lbl={lbl}|dis={dis}|url={url}
        xref_key = "".join([db,"=", ac])
        if store == True:
            # store requested db ac pairs and optional props for which an IRI was requested 
            # so that we can describe Xref afterwards
            # we use a string to store props rather a dict for memory spare
            if xref_key not in our_dict: our_dict[xref_key] = set()
            # we want to store all distinct props for merging and debug purpose
            our_dict[xref_key].add(props)
        # build a md5 based IRI from db and ac only 
        xref_md5 = hashlib.md5(xref_key.encode('utf-8')).hexdigest()
        return "".join(["xref:", self.cleanDb(db), "_", xref_md5])
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOrganizationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # we store name, shortname, country, city, contact
    nccc_dict = dict()
    def __init__(self): super(OurOrganizationNamespace, self).__init__("orga", get_rdf_base_IRI() + "/orga/")
    def IRI(self, name, shortname, city, country, contact, store=True):
        our_dict = OurOrganizationNamespace.nccc_dict
        # store name, shortname, city, country, contact tuples for which an IRI was requested 
        # so that we can describe Organization afterwards
        org_key = "".join([name, "|", shortname or '', "|", city or '', "|", country or '', "|", contact or ''])
        if store == True:
            if org_key not in our_dict: our_dict[org_key] = 0
            our_dict[org_key] += 1        
        org_md5 = hashlib.md5(org_key.encode('utf-8')).hexdigest()
        org_iri = "".join(["orga:", org_md5])
        return org_iri


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class CelloWebsiteNamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def __init__(self): 
#         super(CelloWebsiteNamespace, self).__init__("cello", "https://www.cellosaurus.org/")
#     def IRI(self, primaryAccession): return "cello:" + primaryAccession


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class HelpNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(HelpNamespace, self).__init__("help", get_help_base_IRI() + "/")
    def IRI(self, page): return "help:" + page


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurDatabaseAndTerminologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OurDatabaseAndTerminologyNamespace, self).__init__("db", get_rdf_base_IRI() + "/db/")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurPublicationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_set = set()
    def __init__(self): super(OurPublicationNamespace, self).__init__("pub", get_rdf_base_IRI() + "/pub/")
    def IRI(self, db, ac):
        pub_key = "".join([db, "|", ac])
        # store requested db ac pairs for which an IRI was requested so that we can describe Xref afterwards
        OurPublicationNamespace.dbac_set.add(pub_key)
        pub_md5 = hashlib.md5(pub_key.encode('utf-8')).hexdigest()
        return "".join(["pub:", db, "_", pub_md5])


