import uuid
from namespace import NamespaceRegistry as ns


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_triple(s, p, o, punctuation="."):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return " ".join([s,p,o, punctuation, "\n"])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_blank_node():
# -- - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return "_:BN" + uuid.uuid4().hex


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_prefixes():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    lines = list()
    for item in ns.namespaces:
        lines.append(item.getTtlPrefixDeclaration())
    return "\n".join(lines) + "\n"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cl(ac, cl_obj):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # print(cl_obj)
    lines = list()
    cl_IRI = ns.cvcl.IRI(ac)
    lines.append(get_triple(cl_IRI, ns.rdf.type(), ns.onto.CellLine()))
    cl_data = cl_obj["cell-line"]

    # fields: AC, AS, ACAS
    for ac_obj in cl_data["accession-list"]:
        some_ac = ns.xsd.string(ac_obj["value"])
        lines.append(get_triple(cl_IRI, ns.onto.accession(), some_ac))
        pred = ns.onto.primaryAccession() if ac_obj["type"] == "primary" else ns.onto.secondaryAccession()        
        lines.append(get_triple(cl_IRI, pred, some_ac))

    # fields: ID, SY, IDSY
    for name_obj in cl_data["name-list"]:
        # blank node for name
        name_bn = get_blank_node()
        lines.append(get_triple(name_bn, ns.rdf.type(), ns.onto.CellLineName()))
        label = ns.xsd.string(name_obj["value"])
        lines.append(get_triple(name_bn, ns.rdfs.label(), label))
        # connect cell line to name entity
        lines.append(get_triple(cl_IRI, ns.onto.name(), name_bn))
        pred = ns.onto.recommendedName() if ac_obj["type"] == "identifier" else ns.onto.alternativeName()
        lines.append(get_triple(cl_IRI, pred, name_bn))
    
    # fields: CC, registration
    for reg_obj in cl_data.get("registration-list") or []:
        name_bn = get_blank_node()
        lines.append(get_triple(name_bn, ns.rdf.type(), ns.onto.CellLineName()))        
        label = ns.xsd.string(reg_obj["registration-number"])
        lines.append(get_triple(name_bn, ns.rdfs.label(), label))
        org_name = reg_obj["registry"]
        org_IRI = ns.orga.IRI(org_name, "", "", "") # not yet split into name, city, country, contact
        lines.append(get_triple(name_bn, ns.onto.source(), org_IRI))
        lines.append(get_triple(cl_IRI, ns.onto.name(), name_bn))
        lines.append(get_triple(cl_IRI, ns.onto.registeredName(), name_bn))

    # fields: CC, misspelling
    for msp_obj in cl_data.get("misspelling-list") or []:
        name_bn = get_blank_node()
        lines.append(get_triple(name_bn, ns.rdf.type(), ns.onto.CellLineName()))        
        label = ns.xsd.string(msp_obj["misspelling-name"])
        lines.append(get_triple(name_bn, ns.rdfs.label(), label))
        note = msp_obj.get("misspelling-note")
        if note is not None: lines.append(get_triple(name_bn, ns.rdfs.comment(), ns.xsd.string(note))) 
        for ref in msp_obj.get("reference-list") or []:
            (db,ac) = ref["resource-internal-ref"].split("=")
            ref_IRI = ns.pub.IRI(db,ac)
            lines.append(get_triple(name_bn, ns.onto.appearsIn(), ref_IRI))
        for xref in msp_obj.get("xref-list") or []:
            ac = xref["accession"]
            db = xref["database"]
            xref_IRI = ns.xref.IRI(db,ac)
            lines.append(get_triple(name_bn, ns.onto.appearsIn(), xref_IRI))
        lines.append(get_triple(cl_IRI, ns.onto.name(), name_bn))
        lines.append(get_triple(cl_IRI, ns.onto.misspellingName(), name_bn))

    # fields: DR
    for xref in cl_data.get("xref-list") or []:
        ac = xref["accession"]
        db = xref["database"]
        xref_IRI = ns.xref.IRI(db,ac)
        lines.append(get_triple(cl_IRI, ns.onto.xref(), xref_IRI))
        
    # fields: RX
    for rx in cl_data.get("reference-list") or []:
        (db,ac) = rx["resource-internal-ref"].split("=")
        rx_IRI = ns.pub.IRI(db,ac)
        lines.append(get_triple(cl_IRI, ns.onto.reference(), rx_IRI))

    # fields: WW
    for ww in cl_data.get("web-page-list") or []:
        ww_iri = "".join(["<", ww, ">"])
        lines.append(get_triple(cl_IRI, ns.rdfs.seeAlso(), ww_iri))


    return("".join(lines))


