import re
import hashlib


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def replace_non_alphanumeric(input_string):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Use a regular expression to replace non-alphanumeric characters with underscore
    return re.sub(r'[^a-zA-Z0-9]', '_', input_string)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def getTtlPrefixDeclaration(prefix, baseurl):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    return "".join(["@prefix ", prefix, ": <", baseurl, "> ."])


# namespace ancestor class 
# handles prefix and base URL
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BaseNamespace:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, prefix, baseurl):
        self.pfx = prefix
        self.url = baseurl
    def prefix(self): return self.pfx
    def baseurl(self): return self.url
    def getTtlPrefixDeclaration(self): 
        return getTtlPrefixDeclaration(self.prefix(), self.baseurl())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class XsdNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): 
        super(XsdNamespace, self).__init__("xsd", "http://www.w3.org/2001/XMLSchema#")

    def escape_string(self, str):
        # escape backslashes with double backslashes (\ => \\)
        str=str.replace("\\","\\\\")
        # escape double-quotes (" => \")
        str = str.replace("\"", "\\\"")
        return str

    # string datatype with triple quotes allow escape chars like \n \t etc.
    def string(self, str):
        return "".join(["\"", self.escape_string(str), "\"^^xsd:string"])

    def string3(self, str): 
        return "".join(["\"\"\"", self.escape_string(str), "\"\"\"^^xsd:string"])
    
    def date(self, str): return "".join(["\"", str, "\"^^xsd:date"])
    def integer(self, int_number): return str(int_number)
    def float(self, float_number): return "".join(["\"", str(float_number), "\"^^xsd:float"])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(RdfNamespace, self).__init__("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    def type(self): return "rdf:type"
    def Property(self): return "rdf:Property"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RdfsNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(RdfsNamespace, self).__init__("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    def Class(self): return "rdfs:Class"
    def subClassOf(self): return "rdfs:subClassOf"
    def subPropertyOf(self): return "rdfs:subPropertyOf"
    def comment(self): return "rdfs:comment"
    def label(self): return "rdfs:label"
    def domain(self): return "rdfs:domain"
    def range(self): return "rdfs:range"
    def seeAlso(self): return "rdfs:seeAlso"
    def isDefinedBy(self): return "rdfs:isDefinedBy"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OwlNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OwlNamespace, self).__init__("owl", "http://www.w3.org/2002/07/owl#")
    def Class(self): return "owl:Class"
    def DatatypeProperty(self): return "owl:DatatypeProperty"
    def FunctionalProperty(self): return "owl:FunctionalProperty"
    def NamedIndividual(self): return "owl:NamedIndividual"
    def ObjectProperty(self): return "owl:ObjectProperty"
    def TransitiveProperty(self): return "owl:TransitiveProperty"
    def allValuesFrom(self): return "owl:allValuesFrom"
    def sameAs(self): return "owl:sameAs"
    def unionOf(self): return "owl:unionOf"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SkosNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(SkosNamespace, self).__init__("skos", "http://www.w3.org/2004/02/skos/core#")
    def Concept(self): return "skos:Concept"
    def ConceptScheme(self): return "skos:ConceptScheme"
    def inScheme(self): return "skos:inScheme"
    def notation(self): return "skos:notation"
    def prefLabel(self): return "skos:prefLabel"
    def altLabel(self): return "skos:altLabel"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class FoafNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(FoafNamespace, self).__init__("foaf", "http://xmlns.com/foaf/0.1/")
    def Person(self): return "foaf:Person"


# Cellosaurus ontology namespace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOntologyNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OurOntologyNamespace, self).__init__("", "http://cellosaurus.org/rdf#")

    # Classes
    def CellLine(self): return ":CellLine"
    def CellLineName(self): return ":CellLineName"
    def Organization(self): return ":Organization"
    def Publication(self): return ":Publication"
    def Xref(self): return ":Xref"
    def GenomeAncestry(self): return ":GenomeAncestry"
    def PopulationPercentage(self): return ":PopulationPercentage"
    def HLATyping(self): return ":HLATyping"
    def GeneAlleles(self): return ":GeneAlleles"
    def Gene(self): return ":Gene"
    def Source(self): return ":Source" # a superclass of Publication, Organization, Xref (used for direct author submision)

    # Properties
    def accession(self): return ":accession"
    def primaryAccession(self): return ":primaryAccession"
    def secondaryAccession(self): return ":secondaryAccession"
    
    def name(self): return ":name"
    def recommendedName(self): return ":recommendedName"
    def alternativeName(self): return ":alternativeName"
    def registeredName(self): return ":registeredName"
    def misspellingName(self): return ":misspellingName"

    def appearsIn(self): return ":appearsIn"
    def source(self): return ":source"
    def xref(self): return ":xref"
    def reference(self): return ":reference"

    def genomeAncestry(self): return ":genomeAncestry"
    def component(self): return ":component" # component object = population percentage of geome ancestry
    def percentage(self): return ":percentage"
    def populationName(self): return ":populationName" # as sub property of rdfs:label

    def hlaTyping(self): return ":hlaTyping"
    def geneAlleles(self): return ":geneAlleles"
    def gene(self): return ":gene"
    def alleles(self): return ":alleles"


# Cellosaurus cell-line instances namespace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurCellLineNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self): super(OurCellLineNamespace, self).__init__("cvcl", "http://cellosaurus.org/cvcl/")
    def IRI(self, primaryAccession): return "cvcl:" + primaryAccession


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurXrefNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_set = set()
    def __init__(self): super(OurXrefNamespace, self).__init__("xref", "http://cellosaurus.org/xref/")
    def IRI(self, db, ac):
        # store requested db ac pairs fo which an IRI was requested so that we can describe Xref afterwards
        OurXrefNamespace.dbac_set.add("".join([db, "|", ac]))
        # TODO: review the IRI naming convention or use a MD5
        # handle special characters in db:  " ", "/", "_", "-"
        clean_db = replace_non_alphanumeric(db)
        clean_ac = ac.replace(":", "_")
        return "".join(["xref:", clean_db, "_", clean_ac])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurPublicationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_set = set()
    def __init__(self): super(OurPublicationNamespace, self).__init__("pub", "http://cellosaurus.org/pub/")
    def IRI(self, db, ac):
        # store requested db ac pairs fo which an IRI was requested so that we can describe Xref afterwards
        OurPublicationNamespace.dbac_set.add("".join([db, "|", ac]))
        # TODO: review the IRI naming convention or use a MD5 especially for DOI accessions
        return "".join(["pub:", db, "_", ac])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurOrganizationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # we store name, country, city, contact but multiple contact might arrive in same organization so
    # the IRI for organization is based on name, city, country and does NOT include contact
    nccc_set = set()
    def __init__(self): super(OurOrganizationNamespace, self).__init__("orga", "http://cellosaurus.org/orga/")
    def IRI(self, name, city, country, contact):
        # store name, city, country, contact tuples for which an IRI was requested so that we can describe Organizazion afterwards
        OurOrganizationNamespace.nccc_set.add("".join([name, "|", city or '', "|", country or '', "|", contact or '']))
        org_key = "".join([name, "|", city or '', "|", country or ''])
        org_md5 = hashlib.md5(org_key.encode('utf-8')).hexdigest()
        org_iri = "".join(["orga:", org_md5])
        return org_iri

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurSourceNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # we store name, country, city, contact but multiple contact might arrive in same organization so
    # the IRI for organization is based on name, city, country and does NOT include contact
    name_set = set()
    def __init__(self): super(OurSourceNamespace, self).__init__("src", "http://cellosaurus.org/src/")
    def IRI(self, name):
        # store names for which an IRI was requested so that we can describe Source afterwards
        OurSourceNamespace.name_set.add(name)
        src_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
        src_iri = "".join(["src:", src_md5])
        return src_iri


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NamespaceRegistry:    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # instanciate namespaces
    onto = OurOntologyNamespace()
    cvcl = OurCellLineNamespace()
    xref = OurXrefNamespace()
    pub = OurPublicationNamespace()
    orga = OurOrganizationNamespace()
    src = OurSourceNamespace()
    xsd  = XsdNamespace()
    rdf = RdfNamespace()
    rdfs = RdfsNamespace()
    skos = SkosNamespace()
    owl = OwlNamespace()
    foaf = FoafNamespace()
    namespaces = [onto, cvcl, xref, pub, orga, src, xsd, rdf, rdfs, skos, owl, foaf]


