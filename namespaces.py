import hashlib
from ApiCommon import get_rdf_base_IRI, get_help_base_IRI
from namespace_term import Term


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

    def registerTerm(self, id, p=None, v=None, hidden=False):
        if id not in self.terms: 
            t = Term(self.pfx, id, hidden)
            t.props["rdfs:isDefinedBy"] = { self.pfx + ":" }
            if p is not None and v is not None: t.props[p] = v
            self.terms[id] = t
        return self.terms[id].iri

    def registerNamedIndividual(self, id, label=None, comment=None, hidden=False):
        iri = self.registerTerm(id, p="rdf:type", v={ "owl:NamedIndividual" }, hidden=hidden)
        if label   is not None: self.describe(iri, "rdfs:label",   f"\"{label}\"^^xsd:string")
        if comment is not None: self.describe(iri, "rdfs:comment", f"\"{comment}\"^^xsd:string")
        return iri
    
    def registerClass(self, id, label=None, comment=None, hidden=False):
        iri = self.registerTerm(id, p="rdf:type", v={ "owl:Class" }, hidden=hidden)
        if label   is not None: self.describe(iri, "rdfs:label",   f"\"{label}\"^^xsd:string")
        if comment is not None: self.describe(iri, "rdfs:comment", f"\"{comment}\"^^xsd:string")
        return iri
    
    def registerProperty(self, id, hidden=False):
        return self.registerTerm(id, p="rdf:type", v={ "rdf:Property" }, hidden=hidden)

    def registerDatatypeProperty(self, id,   label=None, comment=None, hidden=False):
        iri = self.registerTerm(id, p="rdf:type", v={ "rdf:Property", "owl:DatatypeProperty" }, hidden=hidden)
        if label   is not None: self.describe(iri, "rdfs:label",   f"\"{label}\"^^xsd:string")
        if comment is not None: self.describe(iri, "rdfs:comment", f"\"{comment}\"^^xsd:string")
        return iri
    
    def registerObjectProperty(self, id,  label=None, comment=None, hidden=False):
        iri = self.registerTerm(id, p="rdf:type", v={ "rdf:Property", "owl:ObjectProperty" }, hidden=hidden)
        if label   is not None: self.describe(iri, "rdfs:label",   f"\"{label}\"^^xsd:string")
        if comment is not None: self.describe(iri, "rdfs:comment", f"\"{comment}\"^^xsd:string")
        return iri

    def registerAnnotationProperty(self, id,  label=None, comment=None, hidden=False):
        iri = self.registerTerm(id, p="rdf:type", v={ "rdf:Property", "owl:AnnotationProperty" }, hidden=hidden)
        if label   is not None: self.describe(iri, "rdfs:label",   f"\"{label}\"^^xsd:string")
        if comment is not None: self.describe(iri, "rdfs:comment", f"\"{comment}\"^^xsd:string")
        return iri


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
        self.Class = self.registerTerm("Class", hidden=True)
        self.subClassOf = self.registerTerm("subClassOf", hidden=True)
        self.subPropertyOf = self.registerTerm("subPropertyOf", hidden=True)
        self.comment = self.registerTerm("comment", hidden=True)
        self.label = self.registerTerm("label", hidden=True)
        self.domain = self.registerTerm("domain", hidden=True)
        self.range = self.registerTerm("range", hidden=True)
        self.seeAlso = self.registerTerm("seeAlso", hidden=False)
        self.isDefinedBy = self.registerTerm("isDefinedBy", hidden=True)
        self.Literal = self.registerTerm("Literal", hidden=True)
        

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
        self.inverseOf = self.registerTerm("inverseOf")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SkosNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(SkosNamespace, self).__init__("skos", "http://www.w3.org/2004/02/skos/core#")
        self.Concept = self.registerTerm("Concept")
        self.ConceptScheme = self.registerTerm("ConceptScheme")
        self.inScheme = self.registerTerm("inScheme")
        self.notation = self.registerDatatypeProperty("notation", comment=" Notations are symbols which are not normally recognizable as words or sequences of words in any natural language and are thus usable independently of natural-language contexts. They are typically composed of digits, complemented with punctuation signs and other characters.")
        self.prefLabel = self.registerAnnotationProperty("prefLabel")
        self.altLabel = self.registerAnnotationProperty("altLabel")
        self.hiddenLabel = self.registerAnnotationProperty("hiddenLabel", comment="A hidden lexical label, represented by means of the skos:hiddenLabel property, is a lexical label for a resource, where a KOS designer would like that character string to be accessible to applications performing text-based indexing and search operations, but would not like that label to be visible otherwise. Hidden labels may for instance be used to include misspelled variants of other lexical labels.")
        self.broader = self.registerObjectProperty("broader", label="has broader concept")
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

        self.hasPubMedCentralId = self.registerDatatypeProperty("hasPubMedCentralId", label="has PubMed Central Identifier") # not hidden because super of cello:term ans sub of dcterms:term
        self.hasPubMedId = self.registerDatatypeProperty("hasPubMedId", label="has PubMed Identifier")                       # not hidden because super of cello:term ans sub of dcterms:term
        self.hasPublicationYear = self.registerDatatypeProperty("hasPublicationYear", label="has Publication Year", hidden=True)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class PrismNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(PrismNamespace, self).__init__("prism", "http://prismstandard.org/namespaces/basic/2.0/")

        comment="An identifier for a particular volume of a resource, such as a journal or a multi-volume book."
        self.volume = self.registerDatatypeProperty("volume", comment=comment)      # not hidden because super of cello:term ans sub of dcterms:term   
        self.hasDOI = self.registerDatatypeProperty("doi", label="has DOI")         # not hidden because super of cello:term ans sub of dcterms:term
        self.publicationDate = self.registerDatatypeProperty("publicationDate", label="has publication date", hidden=True)
        self.startingPage = self.registerDatatypeProperty("startingPage", hidden=True )              
        self.endingPage = self.registerDatatypeProperty("endingPage", hidden=True)    
        
                       


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
        
        #self.Annotation = self.registerClass("Annotation")
        self.Database = self.registerClass("Database", hidden=True)
        self.Protein = self.registerClass("Protein", hidden=True)

        #self.annotation = self.registerObjectProperty("annotation")
        #self.volume = self.registerDatatypeProperty("volume")
        #self.title = self.registerDatatypeProperty("title")

        #self.version = self.registerDatatypeProperty("version")   # warning: incompatible domain (Protein, Sequence, Cluster)
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
        self.P3289_AC = self.registerDatatypeProperty("P3289", label="Cellosaurus ID")
        self.P3578_OI = self.registerObjectProperty("P3578", label="autologous cell line")   
        self.P9072_OX = self.registerObjectProperty("P9072", label="derived from organism type")
        self.P5166_DI = self.registerObjectProperty("P5166", label="established from medical condition")
        self.P3432_HI = self.registerObjectProperty("P3432", label="parent cell line")
        self.P21_SX = self.registerObjectProperty("P21", label="Sex") # could not figure out how sex is related to cell lines in wikidata

        # cell line classes with label as found in cellosaurus.txt
        self.Q23058136 = self.registerClass("Q23058136", label="Cancer cell line", hidden=True)
        self.Q27653145 = self.registerClass("Q27653145", label="Conditionally immortalized cell line", hidden=True)
        self.Q107102664 = self.registerClass("Q107102664", label="Embryonic stem cell", hidden=True)
        self.Q27627225 = self.registerClass("Q27627225", label="Factor-dependent cell line", hidden=True)
        self.Q27671617 = self.registerClass("Q27671617", label="Finite cell line", hidden=True)
        self.Q27555050 = self.registerClass("Q27555050", label="Hybrid cell line", hidden=True)
        self.Q27554370 = self.registerClass("Q27554370", label="Hybridoma", hidden=True)
        self.Q107103143 = self.registerClass("Q107103143", label="Induced pluripotent stem cell", hidden=True)
        self.Q107103129 = self.registerClass("Q107103129", label="Somatic stem cell", hidden=True)
        self.Q27555319 = self.registerClass("Q27555319", label="Spontaneously immortalized cell line", hidden=True)
        self.Q27671698 = self.registerClass("Q27671698", label="Stromal cell line", hidden=True)
        self.Q27653701 = self.registerClass("Q27653701", label="Telomerase immortalized cell line", hidden=True)
        self.Q27555384 = self.registerClass("Q27555384", label="Transformed cell line", hidden=True)
        self.Q21014462 = self.registerClass("Q21014462", label="Cell line", hidden=True)


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
        #self.Annotation = self.registerClass("Annotation")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SchemaOrgNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(SchemaOrgNamespace, self).__init__("schema", "https://schema.org/")
        self.location = self.registerDatatypeProperty("location")                   # only a rdf:Property in original ontology but useful for protege, widoco, ...
        self.memberOf = self.registerObjectProperty("memberOf", hidden=True)        # only a rdf:Property in original ontology but useful for protege, widoco, ...
        self.Organization = self.registerClass("Organization")
        self.Person = self.registerClass("Person")
        self.provider = self.registerObjectProperty("provider", hidden=True)
        self.Observation = self.registerClass("Observation")
        self.observationAbout = self.registerObjectProperty("observationAbout", hidden = False)
        self.category = self.registerDatatypeProperty("category", comment="A category for the item.")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class DctermsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(DctermsNamespace, self).__init__("dcterms", "http://purl.org/dc/terms/")
        self.created =      self.registerDatatypeProperty("created", hidden=True)       # hidden because redundant with cello equivalent
        self.modified =     self.registerDatatypeProperty("modified", hidden=True)      # hidden because redundant with cello equivalent
        self.hasVersion =   self.registerDatatypeProperty("hasVersion", hidden=True)    # hidden because redundant with cello equivalent
        self.description =  self.registerDatatypeProperty("description", hidden=True)   # hidden because irrelevant to cello data
        self.license =      self.registerDatatypeProperty("license", hidden=True)       # hidden because irrelevant to cello data
        self.abstract =     self.registerDatatypeProperty("abstract", hidden=True)      # hidden because irrelevant to cello data
        self.title =        self.registerDatatypeProperty("title")
        self.creator =      self.registerObjectProperty("creator", hidden=True)         # hidden because redundant with cello equivalent
        self.publisher =    self.registerObjectProperty("publisher", hidden=True)       # hidden because redundant with cello equivalent
        self.contributor =  self.registerObjectProperty("contributor")
        self.identifier =   self.registerDatatypeProperty("identifier")
        self.source =       self.registerObjectProperty("source", hidden=False)             # not hidden because parent of 2 cello props
        self.references =   self.registerAnnotationProperty("references", hidden=True)      # hidden because redundant with cello equivalent
        


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BFONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(BFONamespace, self).__init__("BFO", "http://purl.obolibrary.org/obo/BFO_")
        self._0000051_has_part = self.registerObjectProperty("0000051", label="has part", comment="a core relation that holds between a whole and its part")
        #self._0000050_part_of = self.registerObjectProperty("0000050", label="part of", comment="a core relation that holds between a part and its whole")


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
class IAONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(IAONamespace, self).__init__("IAO", "http://purl.org/ontology/IAO_")
        comment = "A (currently) primitive relation that relates an information artifact to an entity."
        self.is_about_0000136 = self.registerObjectProperty("0000136", label="is about", comment=comment)
        comment = "An information content entity that is intended to be a truthful statement about something (modulo, e.g., measurement precision or other systematic errors) and is constructed/acquired by a method which reliably tends to produce (approximately) truthful statements."
        self.DataItem_0000027 = self.registerClass("0000027", label = "Data item", comment=comment)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class EDAMNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(EDAMNamespace, self).__init__("EDAM", "http://edamontology.org/")
        comment = "A category denoting a rather broad domain or field of interest, study, application, work, data, or technology. Topics have no clearly defined borders between each other."
        self.Topic_0003 = self.registerClass("topic_0003", label="Topic", comment=comment)
        comment = "'A has_topic B' defines for the subject A, that it has the object B as its topic (A is in the scope of a topic B)."
        self.has_topic = self.registerObjectProperty("has_topic", label="has topic", comment=comment)


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

        self.C15426_Database = self.registerClass("C15426", label="Database", hidden=True)          # superclass of cello:Database

        comment = "Any abnormal condition of the body or mind that causes discomfort, dysfunction, or distress to the person affected or those in contact with the person. The term is often used broadly to include injuries, disabilities, syndromes, symptoms, deviant behaviors, and atypical variations of structure and function."
        self.C2991_Disease = self.registerClass("C2991", label="Disease or disorder", comment=comment)
        
        comment="A group of animals homogeneous in appearance and other characteristics that distinguish it from other animals of the same species."
        self.C53692_Breed = self.registerClass("C53692", label="Breed", comment=comment, hidden=True)

        comment="Ranked categories for the classification of organisms according to their suspected evolutionary relationships."
        self.C40098_Taxon = self.registerClass("C40098", label="Taxon", comment=comment)
        
        self.C43621_Xref = self.registerClass("C43621", label="Cross-Reference", hidden=True)       # superclass of cello:Xref
        self.C17262 = self.registerClass("C17262", label="X-ray")                                   # genome modification method subclass
        self.C44386 = self.registerClass("C44386", label="Gamma radiation")                         # genome modification method subclass
        self.C16612 = self.registerClass("C16612", label="Gene", hidden=True)                       # owl:equClass cello:Gene
        #self.C45822 = self.registerClass("C45822", label="Locus", hidden=True)                      # unused owl:equClass cello:Locus
        self.C13441_ShortTandemRepeat = self.registerClass("C13441", label="Short Tandem Repeat", hidden= True)   # owl:equClass cello:Marker
        self.C16717_IGH = self.registerClass("C16717", label="Immunoglobulin Heavy Chain", hidden=True) # has owl:equClass in cello:
        self.C16720_IGL = self.registerClass("C16720", label="Immunoglobulin Light Chain", hidden=True) # has owl:equClass in cello:

        # Topic classes for comments
        self.C94346 = self.registerClass("C94346", label="Doubling time")
        self.C205365 = self.registerClass("C205365", label="Omics")
        self.C17467 = self.registerClass("C17467", label="Senescence")
        self.C17256 = self.registerClass("C17256", label="Virology")
        self.C16351 = self.registerClass("C16351", label="Biotechnology")

        # # replaced with HGNC xrefs
        # self.C101157 = self.registerClass("C101157", label="HLA-DRA Gene")   # described as a cello:HLAGene subclass
        # self.C190000 = self.registerClass("C190000", label="HLA-DRB2 Gene")   # described as a cello:HLAGene subclass
        # self.C19409 = self.registerClass("C19409", label="HLA-DRB1 Gene")   # described as a cello:HLAGene subclass
        # self.C28585 = self.registerClass("C28585", label="HLA-A Gene")   # described as a cello:HLAGene subclass
        # self.C29953 = self.registerClass("C29953", label="HLA-DPB1 Gene")   # described as a cello:HLAGene subclass
        # self.C62758 = self.registerClass("C62758", label="HLA-C Gene")   # described as a cello:HLAGene subclass
        # self.C62778 = self.registerClass("C62778", label="HLA-B Gene")   # described as a cello:HLAGene subclass
        # self.C70614 = self.registerClass("C70614", label="HLA-DQB1 Gene")   # described as a cello:HLAGene subclass
        # self.C71259 = self.registerClass("C71259", label="HLA-DRB3 Gene")   # described as a cello:HLAGene subclass
        # self.C71261 = self.registerClass("C71261", label="HLA-DRB4 Gene")   # described as a cello:HLAGene subclass
        # self.C71263 = self.registerClass("C71263", label="HLA-DRB5 Gene")   # described as a cello:HLAGene subclass
        # self.C71265 = self.registerClass("C71265", label="HLA-DQA1 Gene")   # described as a cello:HLAGene subclass
        # self.C71267 = self.registerClass("C71267", label="HLA-DPA1 Gene")   # described as a cello:HLAGene subclass

        # SequenceVariation class, aleternative 1)
        # SequenceVariation class, aleternative 2) Note: Gene Abnormality is a direct subclass of Molecular Genetic Variation
        #comment = "A variation in or modification of the nucleic acid sequence of a gene that can alter its expression and may result in either a congenital disorder or the clinical presentation of a disease."
        #self.SequenceVariation = self.registerClass("C36327", label = "Gene Abnormality", comment = comment) # as generic class for SequenceVariation
        # ... sub classes first level        
        
        self.SequenceVariation = self.registerClass("C36391", hidden=True, label = "Molecular Genetic Variation", comment = "A variation in or modification of the molecular sequence of a gene or gene product.") # as generic class for SequenceVariation
        self.GeneAmplification = self.registerClass("C45581", hidden=True, label="Gene Amplification Abnormality", comment="An increase in the copy number of a particular gene. This type of abnormality can be either inherited or somatic")
        self.GeneDeletion = self.registerClass("C16606", hidden=True, label="Gene Deletion", comment="A deletion that results in the loss of a DNA segment encompassing an entire gene sequence")
        self.GeneFusion = self.registerClass("C45584", hidden=True, label="Gene Fusion Abnormality", comment="Any hybrid gene formed from two previously separate genes. Such fusions occur as a result of translocation, intersititial deletion or chromosomal inversion, and often result in gene products with functions different from the two fusion partners. Gene fusions are associated frequently with hematological cancers, sarcomas and prostate cancer")
        self.GeneMutation = self.registerClass("C18093", hidden=True, label="Gene Mutation", comment="The result of any gain, loss or alteration of the sequences comprising a gene, including all sequences transcribed into RN")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class GENONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(GENONamespace, self).__init__("GENO", "http://purl.obolibrary.org/obo/GENO_")
        self._0000512_Allele = self.registerClass("0000512", label="Allele")
        self._0000608_has_zygozity = self.registerDatatypeProperty("0000608", hidden=True)
        #self._0000413_has_allele = self.registerObjectProperty("0000413", label="has allele", hidden=True )
        #self._0000408_is_allele_of = self.registerObjectProperty("0000408", hidden=True)
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ORDONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(ORDONamespace, self).__init__("ORDO", "http://www.orpha.net/ORDO/Orphanet_")
        comment = "A generic term used to describe the clinical items included in the Orphanet nomenclature of rare diseases."
        self.C001_Clinical_Entity = self.registerClass("C001", label="Clinical entity", comment=comment)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OBINamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(OBINamespace, self).__init__("OBI", "http://purl.obolibrary.org/obo/OBI_")

        # most generic class for genome modification methods and its subclasses
        comment = "The introduction, alteration or integration of genetic material into a cell or organism."
        self.GeneticTransformation = self.registerClass("0600043", label="Genetic transformation", comment=comment, hidden=False) # not hidden because cello:GenomeModificationMethod has not the same label
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
        self._0002769 = self.registerClass("0002769", label="Karyotype information", hidden=True) # hidden because has same label as cello:KaryotypeInfoComment       

        self._0000181 = self.registerClass("0000181", label="Population", hidden=True) # hidden because has same label as cello:Population
                

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OMITNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OMITNamespace, self).__init__("OMIT", "http://purl.obolibrary.org/obo/OMIT_")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FBcvNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(FBcvNamespace, self).__init__("FBcv", "http://purl.obolibrary.org/obo/FBcv_")
        self._0003008 = self.registerClass("0003008", label="CRISPR/Cas9")   # genome modification method subclass



# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class OGGNamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def __init__(self): 
#         super(OGGNamespace, self).__init__("OGG", "http://purl.obolibrary.org/obo/OGG_")
#         self._3000003128 = self.registerClass("3000003128", label="Major histocompatibility complex, class II, DR beta 6")   # described as a cello:HLAGene subclass
#         self._3000003132 = self.registerClass("3000003132", label="Major histocompatibility complex, class II, DR beta 9")   # described as a cello:HLAGene subclass


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CARONamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CARONamespace, self).__init__("CARO", "http://purl.obolibrary.org/obo/CARO_")
        # superclass for UBERON and PO anatomical entities
        comment = "A part of a cellular organism that is either an immaterial entity or a material entity with granularity above the level of a protein complex. Or, a substance produced by a cellular organism with granularity above the level of a protein complex."
        self.AnatomicalEntity = self.registerClass("0000000", label="Anatomical entity", comment=comment, hidden=True)   
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CLNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CLNamespace, self).__init__("CL", "http://purl.obolibrary.org/obo/CL_")
        # superclass for CL cell types
        # see also https://ontobee.org/ontology/rdf/CL?iri=http://purl.obolibrary.org/obo/CL_0000000
        self.CellType = self.registerClass("0000000", label="Cell type", hidden=True)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CHEBINamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(CHEBINamespace, self).__init__("CHEBI", "http://purl.obolibrary.org/obo/CHEBI_")
        # superclass for Chemical substances
        # see also https://ontobee.org/ontology/rdf/CHEBI?iri=http://purl.obolibrary.org/obo/CHEBI_24431
        comment = "A chemical entity is a physical entity of interest in chemistry including molecular entities, parts thereof, and chemical substances."
        self.ChemicalEntity = self.registerClass("24431", label="Chemical Entity", comment=comment, hidden=True)
        comment = "A biological macromolecule minimally consisting of one polypeptide chain synthesized at the ribosome."
        self.Protein = self.registerClass("36080", label="Protein", comment=comment, hidden=True)


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


