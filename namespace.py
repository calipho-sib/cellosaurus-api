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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def getSparqlPrefixDeclaration(prefix, baseurl):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    return "".join(["PREFIX ", prefix, ": <", baseurl, "> "])


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
    def getSparqlPrefixDeclaration(self): 
        return getSparqlPrefixDeclaration(self.prefix(), self.baseurl())


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
    def boolean(self, boolean_value): return str(boolean_value).lower() 


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
    def Gene(self): return ":Gene"
    def GeneAlleles(self): return ":GeneAlleles"  # used in HLA
    def MarkerAlleles(self): return ":MarkerAlleles"    # used in short repeat tandem
    def Source(self): return ":Source" # a superclass of Publication, Organization, Xref (used for direct author submision, from parent cell, ...)
    def SequenceVariation(self): return ":SequenceVariation"
    def GeneAmplification(self): return ":GeneAmplification"
    def GeneDuplication(self): return ":GeneDuplication"
    def GeneTriplication(self): return ":GeneTriplication"
    def GeneQuarduplication(self): return ":GeneQuadruplication"
    def GeneExtensiveAmplification(self): return ":GeneExtensiveAmplification"
    def GeneDeletion(self): return ":GeneDeletion"
    def GeneFusion(self): return ":GeneFusion"
    def GeneMutation(self): return ":GeneMutation"
    def RepeatExpansion(self): return ":RepeatExpansion"
    def SimpleMutation(self): return ":SimpleMutation"
    def UnexplicitMutation(self): return ":UnexplicitMutation"
    def Breed(self): return ":BreedComment"
    def AnatomicalElement(self): return ":AnotomicalElement"
    def CellType(self): return ":CellType"    
    def CellLineCollection(self): return ":CellLineCollection"
    def CellLineGroup(self): return ":CellLineGroup"


    def StructuredComment(self): return ":StructuredComment"# a superclass for structured comments / annotations
    def SequenceVariationComment(self): return ":SequenceVariationComment"
    def DoublingTimeComment(self): return ":DoublingTimeComment"
    def DiscontinuationRecord(self): return ":DiscontinuationRecord"
    def KnockoutComment(self): return ":KnockoutComment"

    def FreeTextComment(self): return ":FreeTextComment" # a superclass for text-only comments (with or without source)
    def AnecdotalComment(self): return ":AnecdotalComment"
    def CharacteristicsComment(self): return ":CharacteristicsComment"
    def BiotechnologyComment(self): return ":BiotechnologyComment"
    def DonorInfoComment(self): return ":DonorInfoComment"
    def CautionComment(self): return ":CautionComment"
    def KaryotypicInfoComment(self): return ":KaryotypicInfoComment"
    def MiscellaneousInfoComment(self): return ":MiscellaneousInfoComment"
    def SenescenceComment(self): return ":SenescenceComment"
    def VirologyComment(self): return ":VirologyComment"
    def OmicsComment(self) : return ":OmicsComment"
    def PopulationComment(self) : return ":PopulationComment"
    def MicrosatelliteInstability(self): return ":MicrosatelliteInstability"
    def MabIsotype(self): return ":MabIsotype"
    def Antigen(self): return ":Antigen" # uniprot, chebi (+free text)
    def ChemicalAgent(self): return ":ChemicalAgent" # drugbank, uniprot, ncit, chebi (+free text)
    def TransformantAgent(self): return ":TransformantAgent" # ChEBI, NCBI_TaxID, NCIt, DrugBank (+free text)
    def ShortTandemRepeatProfile(self): return ":ShortTandemRepeatProfile"

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
    def markerAlleles(self): return ":markerAlleles"
    def alleles(self): return ":alleles"
    def markerId(self): return ":markerId"
    def gene(self): return ":gene"
    def partOf(self): return ":partOf"

    def _from(self): return ":from" # cannot use function name "from" (is python reserved word)
    
    def sequenceVariation(self): return ":sequenceVariation"
    def zygosity(self): return ":zygosity"
    def hgvs(self): return ":hgvs"
    def noneReported(self): return ":noneReported"
    def variationStatus(self): return ":variationStatus"
    def breed(self): return ":breed"
    def structuredComment(self): return ":structuredComment"    # super property for compex, structured comments
    def sequenceVariationComment(self): return ":sequenceVariationComment"
    def freeTextComment(self): return ":freeTextComment"        # super property for text based comments (with or without source)
    def anecdotalComment(self): return ":anecdotalComment"
    def characteristicsComment(self): return ":characteristicsComment"
    def biotechnologyComment(self): return ":biotechnologyComment"
    def cautionComment(self): return ":cautionComment"
    def siteType(self): return ":siteType"
    def sampledFromSite(self): return ":sampledFromSite" # TODO: to be used if we define :Sample and connect it to a :AnatomicalEntity
    def derivedFromSite(self): return ":derivedFromSite" 
    def cellType(self): return ":cellType" 
    def donorInfoComment(self): return ":donorInfoComment"
    def doublingTimeComment(self): return ":doublingTimeComment"
    def duration(self): return ":duration"
    def group(self): return ":group"
    def karyotypicInfoComment(self): return ":karyotypicInfoComment"
    def miscellaneousInfoComment(self): return ":miscellaneousInfoComment"
    def senescenceComment(self): return ":senescenceComment"
    def virologyComment(self): return ":virologyComment"
    def omicsComment(self) : return ":omicsComment"
    def populationComment(self) : return ":populationComment"

    def knockout(self): return ":knockout"
    def method(self): return ":method"

    def discontinued(self): return ":discontinued"
    def provider(self): return ":provider"
    def productId(self): return ":productId"
    def microsatelliteInstability(self): return ":microsatelliteInstability"
    def msiValue(self): return ":msiValue"
    def mabIsotype(self): return ":mabIsotype"
    def mabTarget(self): return ":mabTarget"
    def heavyChain(self): return ":heavyChain"
    def lightChain(self): return ":lightChain"
    def resistance(self): return ":resistance"
    def transformant(self): return ":transformant"
    def shortTandemRepeatProfile(self): return ":shortTandemRepeatProfile"
    def conflict(self): return ":conflict"
    

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
    def IRI(self, db, ac, props=None):
        # we expect to get props like: "name=Joe&discontinued=probable"
        # store requested db ac pairs (and optional name) for which an IRI was requested so that we can describe Xref afterwards
        OurXrefNamespace.dbac_set.add("".join([db,"|", ac, "|", props or '']))
        # build a md5 based IRI from db and ac only 
        xref_key = "".join([db,"|", ac])
        xref_md5 = hashlib.md5(xref_key.encode('utf-8')).hexdigest()
        return "".join(["xref:", db, "_", xref_md5])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurPublicationNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dbac_set = set()
    def __init__(self): super(OurPublicationNamespace, self).__init__("pub", "http://cellosaurus.org/pub/")
    def IRI(self, db, ac):
        pub_key = "".join([db, "|", ac])
        # store requested db ac pairs fo which an IRI was requested so that we can describe Xref afterwards
        OurPublicationNamespace.dbac_set.add(pub_key)
        pub_md5 = hashlib.md5(pub_key.encode('utf-8')).hexdigest()
        return "".join(["pub:", db, "_", pub_md5])


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
class OurCellLineCollectionNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # the IRI for cell line collection is based on their label
    name_set = set()
    def __init__(self): super(OurCellLineCollectionNamespace, self).__init__("coll", "http://cellosaurus.org/coll/")
    def IRI(self, name):
        # store names for which an IRI was requested so that we can describe Source afterwards
        OurCellLineCollectionNamespace.name_set.add(name)
        some_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
        some_iri = "".join(["coll:", some_md5])
        return some_iri

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurCellLineGroupNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # the IRI for cell line group is based on their label
    name_set = set()
    def __init__(self): super(OurCellLineGroupNamespace, self).__init__("grp", "http://cellosaurus.org/grp/")
    def IRI(self, name):
        # store names for which an IRI was requested so that we can describe Source afterwards
        OurCellLineGroupNamespace.name_set.add(name)
        some_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
        some_iri = "".join(["grp:", some_md5])
        return some_iri

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class OurBreedNamespace(BaseNamespace):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # the IRI for cell line collection is based on their label
    name_set = set()
    def __init__(self): 
        super(OurBreedNamespace, self).__init__("breed", "http://cellosaurus.org/breed/")
    def IRI(self, name):
        # store names for which an IRI was requested so that we can describe Source afterwards
        OurBreedNamespace.name_set.add(name)
        src_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
        src_iri = "".join(["breed:", src_md5])
        return src_iri


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class OurStrMarkerNamespace(BaseNamespace):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     # the IRI for short tandem profile marker is based on their label
#     name_set = set()
#     def __init__(self): 
#         super(OurStrMarkerNamespace, self).__init__("str", "http://cellosaurus.org/str/")
#     def IRI(self, name):
#         # store names for which an IRI was requested so that we can describe Source afterwards
#         OurStrMarkerNamespace.name_set.add(name)
#         src_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
#         src_iri = "".join(["str:", src_md5])
#         return src_iri



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
    coll = OurCellLineCollectionNamespace()
    grp = OurCellLineGroupNamespace()
    breed = OurBreedNamespace()
    xsd  = XsdNamespace()
    rdf = RdfNamespace()
    rdfs = RdfsNamespace()
    skos = SkosNamespace()
    owl = OwlNamespace()
    foaf = FoafNamespace()
    namespaces = [onto, cvcl, xref, pub, orga, src, coll, grp, breed, xsd, rdf, rdfs, skos, owl, foaf]


