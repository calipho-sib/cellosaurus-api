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

    # fields: CC, genome-ancestry
    annot = cl_data.get("genome-ancestry")
    if annot is not None:
        annot_bn = get_blank_node()
        lines.append(get_triple(cl_IRI, ns.onto.genomeAncestry(), annot_bn))
        lines.append(get_triple(annot_bn, ns.rdf.type() ,ns.onto.GenomeAncestry()))
        # ref can be publi or organization, but only publi in real data
        ref = annot["genome-ancestry-source"].get("reference")
        if ref is not None:
            (db,ac) = ref["resource-internal-ref"].split("=")
            ref_IRI = ns.pub.IRI(db,ac)
            lines.append(get_triple(annot_bn, ns.onto.source(), ref_IRI))
        else:
            print("ERROR: reference of genome-ancestry-source is null: " + ac)
        for pop in annot["population-list"]:
            pop_bn = get_blank_node()
            lines.append(get_triple(annot_bn, ns.onto.component(), pop_bn))
            lines.append(get_triple(pop_bn, ns.rdf.type(), ns.onto.PopulationPercentage()))
            pop_name = ns.xsd.string(pop["population-name"])
            lines.append(get_triple(pop_bn, ns.onto.populationName(), pop_name))
            percent = ns.xsd.float(pop["population-percentage"])
            lines.append(get_triple(pop_bn, ns.onto.percentage(), percent))

    # fields: hla
    for annot in cl_data.get("hla-typing-list") or []:
        annot_bn = get_blank_node()
        lines.append(get_triple(cl_IRI, ns.onto.hlaTyping(), annot_bn))
        lines.append(get_triple(annot_bn, ns.rdf.type() ,ns.onto.HLATyping()))
        hts = annot.get("hla-typing-source")
        if hts is not None:
            xref = hts.get("xref")
            if xref is not None:
                ac = xref["accession"]
                db = xref["database"]
                xref_IRI = ns.xref.IRI(db,ac)
                lines.append(get_triple(annot_bn, ns.onto.source(), xref_IRI))
            ref = hts.get("reference")
            if ref is not None:
                (db,ac) = ref["resource-internal-ref"].split("=")
                ref_IRI = ns.pub.IRI(db,ac)
                lines.append(get_triple(annot_bn, ns.onto.source(), ref_IRI))
            src = hts.get("source")
            if src is not None:
                src_IRI = ns.src.IRI(src) if src == "Direct_author_submission" else ns.orga.IRI(src, "", "", "")
                lines.append(get_triple(annot_bn, ns.onto.source(), src_IRI))
        for gall in annot["hla-gene-alleles-list"]:
            gall_bn = get_blank_node()
            lines.append(get_triple(annot_bn, ns.onto.geneAlleles(), gall_bn))
            lines.append(get_triple(gall_bn, ns.rdf.type(), ns.onto.GeneAlleles()))
            gene_bn = get_blank_node()
            lines.append(get_triple(gall_bn, ns.onto.gene(), gene_bn))
            lines.append(get_triple(gene_bn, ns.rdf.type(), ns.onto.Gene()))
            gene_name = ns.xsd.string(gall["gene"])
            lines.append(get_triple(gene_bn, ns.rdfs.label(), gene_name))
            alleles = ns.xsd.string(gall["alleles"])            
            lines.append(get_triple(gall_bn, ns.onto.alleles(), alleles))

    return("".join(lines))


