from namespaces import *
from namespace_cello import CelloOntologyNamespace
from namespace_term import Term


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NamespaceRegistry:    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # instanciate local namespaces
    cello = CelloOntologyNamespace()
    cvcl = OurCellLineNamespace()
    xref = OurXrefNamespace()
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
    FBcv = FBcvNamespace() 
    GENO = GENONamespace(); CARO = CARONamespace(); CL = CLNamespace()
    CHEBI = CHEBINamespace(); ORDO = ORDONamespace(); IAO = IAONamespace()
    EDAM = EDAMNamespace(); prism = PrismNamespace(); BFO = BFONamespace()

    namespaces = [cello, cvcl, xref, pub, orga, db, xsd, rdf, rdfs, skos, owl, dcterms, 
                  fabio, up, bibo, widoco, vann, oa, wdt, wd, sh, schema, help, pubmed,
                  BAO, BTO, CLO, NCIt, OBI, OMIT, FBcv, GENO, CARO, CL, CHEBI, ORDO, IAO, EDAM, prism, BFO ]

    pfx2ns = dict()
    for ns in namespaces: pfx2ns[ns.pfx] = ns

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # seems unused
    def getPrefixedIRI(IRI):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        url = IRI 
        if url.startswith("<"): url = url[1:]
        if url.endswith(">"): url = url[:-1]
        for ns in NamespaceRegistry.namespaces:
            if url.startswith(ns.url):
                return ":".join([ns.pfx, url[len(ns.url):]])
        return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def getNamespace(IRI):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        url = IRI 
        if url.startswith("<"): url = url[1:]
        if url.endswith(">"): url = url[:-1]
        for ns in NamespaceRegistry.namespaces:
            if url.startswith(ns.url): return ns
            if url.startswith(ns.pfx + ":"): return ns
        return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def describe(subj_prefixed_iri, prop_iri, value):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        pfx = subj_prefixed_iri.split(":")[0]
        NamespaceRegistry.pfx2ns[pfx].describe(subj_prefixed_iri, prop_iri, value)             


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term(prefixed_iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        pfx, id = prefixed_iri.split(":")
        return NamespaceRegistry.pfx2ns[pfx].term(prefixed_iri)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def ttl_lines_for_ns_term(term: Term):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Note:
    # the class Term cannot have its own ttl_line() method because if requires the usage of
    # some NamespaceRegistry methods causing a circular dependency

        if term.hidden: return list()
        ordered_props = [
            "a", "rdf:type", "rdfs:label", "rdfs:comment", "rdfs:subClassOf", "rdfs:subPropertyOf",
            "owl:equivalentClass", "owl:equivalentProperty", "owl:inverseOf", "owl:sameAs", 
            "skos:exactMatch", "skos:closeMatch", "skos:broadMatch", 
            "domain_comments", "rdfs:domain", "range_comments","rdfs:range", "rdfs:seeAlso", "rdfs:isDefinedBy"]
        lines = list()
        lines.append(term.iri)
        label = term.props.get("rdfs:label")
        if label is None:
            label = "".join(["\"", term.get_label_str(), "\"", "^^xsd:string"])
            term.props["rdfs:label"] = { label }

        # build composite comment including label, skos relationships (otherwise invisible in widoco)
        # and textual comment if any
        NamespaceRegistry.build_composite_comment(term)

        for pk in ordered_props:
            value_set = term.props.get(pk)
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


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def build_composite_comment(term: Term):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Note:
    # the class Term cannot have its own build_composite_comment() method because if requires the usage of
    # some NamespaceRegistry methods causing a circular dependency
    #

        if term.composite_comment_already_built is True: return

        parts = list()

        # if a real comment preexist (see ontology_builder.describe_comments()), retrieve it
        existing_elems = list(term.props.get("rdfs:comment") or set())
        real_comment = None
        if len(existing_elems) > 0: real_comment = term.unwrap_xsd_string(existing_elems[0])
        if real_comment is not None: parts.append(real_comment)
        
        # # if term is from external ns, add original label
        # label = None
        # if term.ns != "cello": label = term.get_label_str()
        # if label is not None: parts.insert(0, label)
        
        # add skos relationships to other terms
        relatedElems = list()
        for pk in ["skos:exactMatch", "skos:closeMatch", "skos:broadMatch", "rdfs:seeAlso"]:
            for elem in term.props.get(pk) or set():
                if elem.startswith("<") and elem.endswith(">"):
                    href = elem[1:-1]
                    obj = f"<a href=\"{href}\">{href}</a>"
                else:
                    objId = elem.split(":")[1]
                    objNs = NamespaceRegistry.getNamespace(elem)
                    if objNs is not None:
                        objTerm = NamespaceRegistry.term(elem)
                        objLabel = objTerm.get_label_str()
                        objUrl = "".join([objNs.url, objId])
                        obj = f"<a href=\"#{objUrl}\" title=\"{objUrl}\">{objLabel}</a>"
                    else:
                        obj = elem
                content = " ".join([pk, "<b>with</b>", obj])
                relatedElems.append(content)
        if len(relatedElems)>0:
            parts.append("".join( ["<dt>has relation</td>", "<dd>", "<br />".join(relatedElems), "</dd>"] ))

        # add domain info for annotation properties
        if "owl:AnnotationProperty" in (term.props.get("rdf:type") or set()):
            domainElems = list()
            for dom in term.props.get("rdfs:domain") or set():
                domId = dom.split(":")[1]
                if dom.startswith("cello:"):
                    domTerm = NamespaceRegistry.term(dom)
                    print(">>>> term", term, "dom:", dom)
                    domLabel = domTerm.get_label_str()
                    domUrl = "/".join([get_rdf_base_IRI(), domId]) 
                    domainElems.append(f"<a href=\"#{domId}\" title=\"{domUrl}\">{domLabel}</a>")
                else:
                    domNs = NamespaceRegistry.getNamespace(dom)
                    if domNs is not None:
                        domTerm = NamespaceRegistry.term(dom)
                        domLabel = domTerm.get_label_str()
                        domUrl = "".join([domNs.url, domId])
                        domainElems.append(f"<a href=\"#{domUrl}\" title=\"{domUrl}\">{domLabel}</a>")
                    else:                        
                        domainElems.append(f"{dom}")
            if len(domainElems) > 1: # when domain is not a union of classes (only 1 class), it is properly displayed by widoco
                domainInfo = " <b>or</b> ".join(domainElems)
                parts.append(f"<dt>has domain</dt><dd>{domainInfo}</dd>")

        composite_content = "<br>".join(parts)
        quote = "\""
        if "\"" in composite_content: quote = "\"\"\"" 
        result = "".join([quote, composite_content, quote, "^^xsd:string"])
        if len(result)>0:
            term.props["rdfs:comment"] = { result } 
        term.composite_comment_already_built = True       

    

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
