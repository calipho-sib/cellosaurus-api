from namespaces import *
from namespace_cello import CelloOntologyNamespace

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NamespaceRegistry:    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # instanciate local namespaces
    cello = CelloOntologyNamespace(); cvcl = OurCellLineNamespace(); xref = OurXrefNamespace()
    pub = OurPublicationNamespace(); orga = OurOrganizationNamespace(); db = OurDatabaseAndTerminologyNamespace()
    # instanciate other used namespaces
    xsd  = XsdNamespace(); rdf = RdfNamespace(); rdfs = RdfsNamespace(); owl = OwlNamespace()
    skos = SkosNamespace(); dcterms = DctermsNamespace()
    fabio = FabioNamespace(); up = UniProtCoreNamespace() 
    bibo = BiboNamespace(); widoco = WidocoNamespace()
    vann = VannNamespace(); pubmed = PubMedNamespace()
    oa = OaNamespace()
    # org = W3OrgNamespace()
    wdt = WikidataWdtNamespace(); wd = WikidataWdNamespace()
    sh = ShaclNamespace();
    schema = SchemaOrgNamespace()
    #cello = CelloWebsiteNamespace()
    help = HelpNamespace()
    BAO = BAONamespace(); BTO = BTONamespace(); CLO = CLONamespace()
    NCIt = NCItNamespace(); OBI = OBINamespace(); OMIT = OMITNamespace()
    FBcv = FBcvNamespace(); OGG = OGGNamespace()
    GENO = GENONamespace(); CARO = CARONamespace(); CL = CLNamespace()

    namespaces = [cello, cvcl, xref, pub, orga, db, xsd, rdf, rdfs, skos, owl, dcterms, 
                  fabio, up, bibo, widoco, vann, oa, wdt, wd, sh, schema, help, pubmed,
                  BAO, BTO, CLO, NCIt, OBI, OMIT, FBcv , OGG, GENO, CARO, CL ]

    pfx2ns = dict()
    for ns in namespaces: pfx2ns[ns.pfx] = ns

    def getPrefixedIRI(IRI):
        url = IRI 
        if url.startswith("<"): url = url[1:]
        if url.endswith(">"): url = url[:-1]
        for ns in NamespaceRegistry.namespaces:
            if url.startswith(ns.url):
                return ":".join([ns.pfx, url[len(ns.url):]])
        return None

    def getNamespace(IRI):
        url = IRI 
        if url.startswith("<"): url = url[1:]
        if url.endswith(">"): url = url[:-1]
        for ns in NamespaceRegistry.namespaces:
            if url.startswith(ns.url): return ns
            if url.startswith(ns.pfx + ":"): return ns
        return None

    def describe(subj_prefixed_iri, prop_iri, value):
        pfx = subj_prefixed_iri.split(":")[0]
        NamespaceRegistry.pfx2ns[pfx].describe(subj_prefixed_iri, prop_iri, value)             


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
if __name__ == '__main__':
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

    ns = NamespaceRegistry

    for space in [ns.up, ns.fabio, ns.dcterms, ns.cello, ns.FBcv]:
        for id in space.terms:
            term = space.terms[id]
            for line in term.ttl_lines():
                print(line)

    print("----")
    ns.up.registerClass("TestClass", "my nice registered label")
    ns.describe("up:TestClass", ns.rdfs.comment, ns.xsd.string("""this is my " real comment"""))
    #ns.describe("up:TestClass", ns.rdfs.label, ns.xsd.string("Test Class label"))
    ns.describe("up:TestClass", ns.skos.broadMatch, "OBI:broader")
    ns.describe("up:TestClass", ns.skos.exactMatch, "OBI:exact")
    ns.describe("up:TestClass", ns.skos.closeMatch, "OBI:close")
    t = ns.up.terms["TestClass"]
    print("\n".join(t.ttl_lines()))

    print("----")
    ns.cello.registerClass("TestClass")
    ns.describe("cello:TestClass", ns.rdfs.comment, ns.xsd.string("""this is my " real comment"""))
    ns.describe("cello:TestClass", ns.rdfs.label, ns.xsd.string("Test Class label"))
    ns.describe("cello:TestClass", ns.skos.broadMatch, "OBI:broader")
    ns.describe("cello:TestClass", ns.skos.exactMatch, "OBI:exact")
    ns.describe("cello:TestClass", ns.skos.closeMatch, "OBI:close")
    t = ns.cello.terms["TestClass"]
    print("\n".join(t.ttl_lines()))

    print("----")
    for id in ns.wd.terms:
        print("id:", id)
        term = ns.wd.terms[id]
        if "owl:Class" in term.props["rdf:type"]:
            print("YES term", term)
