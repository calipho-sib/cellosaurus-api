import uuid
from namespace import NamespaceRegistry as ns

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class DataError(Exception): 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class TripleList:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self): 
        self.lines = list()
    def append(self, s, p, o, punctuation="."):
        line = " ".join([s,p,o, punctuation, "\n"])
        self.lines.append(line)
    def extend(self, triple_list):
        self.lines.extend(triple_list.lines)


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# def get_triple(s, p, o, punctuation="."):
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#     return 


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
def get_sparql_prefixes():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    lines = list()
    for item in ns.namespaces:
        lines.append(item.getSparqlPrefixDeclaration())
    return "\n".join(lines) + "\n"




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_pub_IRI(ref):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    (db,ac) = ref["resource-internal-ref"].split("=")
    return ns.pub.IRI(db,ac)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_xref_IRI(xref):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    ac = xref["accession"]
    db = xref["database"]
    return ns.xref.IRI(db,ac)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cl(ac, cl_obj):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # print(cl_obj)
    triples = TripleList()
    cl_IRI = ns.cvcl.IRI(ac)
    triples.append(cl_IRI, ns.rdf.type(), ns.onto.CellLine())
    cl_data = cl_obj["cell-line"]

    # fields: AC, AS, ACAS
    for ac_obj in cl_data["accession-list"]:
        some_ac = ns.xsd.string(ac_obj["value"])
        triples.append(cl_IRI, ns.onto.accession(), some_ac)
        pred = ns.onto.primaryAccession() if ac_obj["type"] == "primary" else ns.onto.secondaryAccession()        
        triples.append(cl_IRI, pred, some_ac)

    # fields: ID, SY, IDSY
    for name_obj in cl_data["name-list"]:
        # blank node for name
        name_BN = get_blank_node()
        triples.append(name_BN, ns.rdf.type(), ns.onto.CellLineName())
        label = ns.xsd.string(name_obj["value"])
        triples.append(name_BN, ns.rdfs.label(), label)
        # connect cell line to name entity
        triples.append(cl_IRI, ns.onto.name(), name_BN)
        pred = ns.onto.recommendedName() if name_obj["type"] == "identifier" else ns.onto.alternativeName()
        triples.append(cl_IRI, pred, name_BN)
    
    # fields: CC, registration
    for reg_obj in cl_data.get("registration-list") or []:
        name_BN = get_blank_node()
        triples.append(name_BN, ns.rdf.type(), ns.onto.CellLineName())      
        label = ns.xsd.string(reg_obj["registration-number"])
        triples.append(name_BN, ns.rdfs.label(), label)
        org_name = reg_obj["registry"]
        org_IRI = ns.orga.IRI(org_name, "", "", "") # not yet split into name, city, country, contact
        triples.append(name_BN, ns.onto.source(), org_IRI)
        triples.append(cl_IRI, ns.onto.name(), name_BN)
        triples.append(cl_IRI, ns.onto.registeredName(), name_BN)

    # fields: CC, misspelling
    for msp_obj in cl_data.get("misspelling-list") or []:
        name_BN = get_blank_node()
        triples.append(name_BN, ns.rdf.type(), ns.onto.CellLineName())        
        label = ns.xsd.string(msp_obj["misspelling-name"])
        triples.append(name_BN, ns.rdfs.label(), label)
        note = msp_obj.get("misspelling-note")
        if note is not None: triples.append(name_BN, ns.rdfs.comment(), ns.xsd.string(note))
        for ref in msp_obj.get("reference-list") or []:
            triples.append(name_BN, ns.onto.appearsIn(), get_pub_IRI(ref))
        for xref in msp_obj.get("xref-list") or []:             
            triples.append(name_BN, ns.onto.appearsIn(), get_xref_IRI(xref))
        triples.append(cl_IRI, ns.onto.name(), name_BN)
        triples.append(cl_IRI, ns.onto.misspellingName(), name_BN)

    # fields: DR
    for xref in cl_data.get("xref-list") or []:
        triples.append(cl_IRI, ns.onto.xref(), get_xref_IRI(xref))
        
    # fields: RX
    for rx in cl_data.get("reference-list") or []:
        triples.append(cl_IRI, ns.onto.reference(), get_pub_IRI(rx))
 
    # fields: WW
    for ww in cl_data.get("web-page-list") or []:
        ww_iri = "".join(["<", ww, ">"])
        triples.append(cl_IRI, ns.rdfs.seeAlso(), ww_iri)

    # fields: CC, genome-ancestry
    annot = cl_data.get("genome-ancestry")
    if annot is not None:
        annot_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.genomeAncestry(), annot_BN)
        triples.append(annot_BN, ns.rdf.type() ,ns.onto.GenomeAncestry())
        # ref can be publi or organization, but only publi in real data
        ref = annot["genome-ancestry-source"].get("reference")
        if ref is not None:
            triples.append(annot_BN, ns.onto.source(), get_pub_IRI(ref))
        else:
            print("ERROR: reference of genome-ancestry-source is null: " + ac)
        for pop in annot["population-list"]:
            pop_BN = get_blank_node()
            triples.append(annot_BN, ns.onto.component(), pop_BN)
            triples.append(pop_BN, ns.rdf.type(), ns.onto.PopulationPercentage())
            pop_name = ns.xsd.string(pop["population-name"])
            triples.append(pop_BN, ns.onto.populationName(), pop_name)
            percent = ns.xsd.float(pop["population-percentage"])
            triples.append(pop_BN, ns.onto.percentage(), percent)

    # fields: CC hla
    for annot in cl_data.get("hla-typing-list") or []:
        annot_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.hlaTyping(), annot_BN)
        triples.append(annot_BN, ns.rdf.type() ,ns.onto.HLATyping())
        hts = annot.get("hla-typing-source")
        if hts is not None:
            xref = hts.get("xref")
            if xref is not None:
                triples.append(annot_BN, ns.onto.source(), get_xref_IRI(xref))
            ref = hts.get("reference")
            if ref is not None:
                triples.append(annot_BN, ns.onto.source(), get_pub_IRI(ref))
            src = hts.get("source")
            if src is not None:
                src_IRI = ns.src.IRI(src) if src == "Direct_author_submission" else ns.orga.IRI(src, "", "", "")
                triples.append(annot_BN, ns.onto.source(), src_IRI)
        for gall in annot["hla-gene-alleles-list"]:
            gall_BN = get_blank_node()
            triples.append(annot_BN, ns.onto.geneAlleles(), gall_BN)
            triples.append(gall_BN, ns.rdf.type(), ns.onto.GeneAlleles())
            gene_BN = get_blank_node()
            triples.append(gall_BN, ns.onto.gene(), gene_BN)
            triples.append(gene_BN, ns.rdf.type(), ns.onto.Gene())
            gene_name = ns.xsd.string(gall["gene"])
            triples.append(gene_BN, ns.rdfs.label(), gene_name)
            alleles = ns.xsd.string(gall["alleles"])            
            triples.append(gall_BN, ns.onto.alleles(), alleles)


    # fields: CC sequence-variation
    for annot in cl_data.get("sequence-variation-list") or []:
        triples.extend(get_ttl_for_sequence_variation(cl_IRI, annot))


    # fields: CC from, ...
    for cc in cl_data.get("comment-list") or []:
        categ = cc["category"]
        if categ == "From": 
            triples.extend(get_ttl_for_cc_from(cl_IRI, cc))
            

    return("".join(triples.lines))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def extract_hgvs_list(label):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # How to test if description is hgvs ? based on mut type ? and/or parser ?
    # hgvs formal only in Mutation | Simple(_edited/_corrected)
    # hgvs ends at first <space>
    # hgvs formal only if starts with c. , m. , n. , p. , chrN:g.
    # if first hgvs is p.* and first in paranthese is starts with c. => c.* => additional hgvs 
    hgvs_list = list()
    if label is None or label == "": return hgvs_list
    elems = label.split(" ")
    elem = elems[0]
    if   elem.startswith("c."): hgvs_list.append(elem)
    elif elem.startswith("m."): hgvs_list.append(elem)
    elif elem.startswith("n."): hgvs_list.append(elem)
    elif elem.startswith("p."): hgvs_list.append(elem)
    elif elem.startswith("chr") and elem.find(":g.") in  [4,5]: hgvs_list.append(elem)
    # add hgvs of cRNA if comes right after a protein hgvs
    # i.e. p.Ala119Glnfs*5 (c.353_354dupCA) (c.354_355insCA) 
    if len(hgvs_list)>0 and hgvs_list[0].startswith("p.") and len(elems)>1:
        syn = elems[1].split(" ")[0]
        if syn.startswith("(c."): hgvs_list.append(syn[1:-1])        
    return hgvs_list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_sequence_variation(cl_IRI, annot):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    try:
        triples = TripleList()

        annot_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.sequenceVariationComment(), annot_BN)
        triples.append(annot_BN, ns.rdf.type(), ns.onto.SequenceVariationComment())
        mut_type = annot.get("mutation-type")
        variationStatus = "Natural"
        if mut_type is not None and "edited" in mut_type: variationStatus = "Edited"
        if mut_type is not None and "corrected" in mut_type: variationStatus = "Corrected"
        triples.append(annot_BN, ns.onto.variationStatus(), ns.xsd.string(variationStatus))
        var_sources = annot.get("variation-sources") or {}
        for ref in var_sources.get("reference-list") or []:    
            triples.append(annot_BN, ns.onto.source(), get_pub_IRI(ref))
        src = var_sources.get("source")
        if src is not None: 
            triples.append(annot_BN, ns.onto.source(), ns.src.IRI(src))

        seqvar_BN = get_blank_node()
        triples.append(annot_BN, ns.onto.sequenceVariation(), seqvar_BN)
        var_type = annot.get("variation-type")
        sv_clazz = get_sequence_variation_class(var_type, mut_type)
        triples.append(seqvar_BN, ns.rdf.type(), sv_clazz)
        none_reported = (mut_type == "None_reported")
        triples.append(seqvar_BN, ns.onto.noneReported(), ns.xsd.boolean(none_reported))
        note = annot.get("variation-note")
        if note is not None: triples.append(seqvar_BN, ns.rdfs.comment(), ns.xsd.string(note))        
        zygo = annot.get("zygosity-type")
        if zygo is not None: triples.append(seqvar_BN, ns.onto.zygosity(), ns.xsd.string(zygo))
        label = annot.get("mutation-description")
        if none_reported: label = "None_reported"
        if var_type=="Gene deletion" and label is None: label = var_type
        elif var_type=="Gene amplification" and label is None: label = mut_type # Duplication, Triplication, ...
        triples.append(seqvar_BN, ns.rdfs.label(), ns.xsd.string(label)) # TODO? remove first hgvs from label ?        
        if var_type=="Mutation" and mut_type.startswith("Simple"): 
            hgvs_list = extract_hgvs_list(label)
            if len(hgvs_list) not in [1,2]: print(f"WARN, invalid hgvs in: {label}")
            for hgvs in hgvs_list: triples.append(seqvar_BN, ns.onto.hgvs(), ns.xsd.string(hgvs))
        for xref in annot.get("xref-list"):
            db = xref["database"]
            if db in ["HGNC", "MGI", "RGD", "VGNC", "UniProtKB"]:
                triples.append(seqvar_BN, ns.onto.gene(), get_xref_IRI(xref)) # gene(s) related to the variation
            elif db in ["ClinVar", "dbSNP"]:
                triples.append(seqvar_BN, ns.onto.reference(), get_xref_IRI(xref)) # reference of the variant desciption

        #print(f"varmut-desc | {var_type} | {mut_type} | {label}")
        return triples

    except DataError as e:
        (typ,details) = e.args        
        cl_ac = cl_IRI.split(":")[1]
        print(f"ERROR, {typ} - {details} : {cl_ac}")
        return TripleList()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_sequence_variation_class(var_type, mut_type):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #   47793 varmut | Mutation | Simple
    #     177 varmut | Mutation | Simple_corrected
    #     364 varmut | Mutation | Simple_edited
    #     780 varmut | Mutation | Repeat_expansion
    #       8 varmut | Mutation | Repeat_expansion_corrected
    #       1 varmut | Mutation | Repeat_expansion_edited
    #     782 varmut | Mutation | Unexplicit
    #       1 varmut | Mutation | Unexplicit_corrected
    #      11 varmut | Mutation | Unexplicit_edited
    #     361 varmut | Mutation | None_reported
    #    8273 varmut | Gene fusion | 
    #    2557 varmut | Gene deletion | 
    #      85 varmut | Gene amplification | Triplication
    #      25 varmut | Gene amplification | Duplication
    #      12 varmut | Gene amplification | Quadruplication
    #      12 varmut | Gene amplification | Extensive
    # ordering of "if" based on data: most frequent cases first to ensure best performance
    if var_type == "Mutation":
        if mut_type.startswith("Simple"): return ns.onto.SimpleMutation()
        if mut_type.startswith("Repeat"): return ns.onto.RepeatExpansion()
        if mut_type.startswith("Unexplicit"): return ns.onto.UnexplicitMutation()
        if mut_type == "None_reported": return ns.onto.GeneMutation()
    elif var_type == "Gene fusion": return ns.onto.GeneFusion()
    elif var_type == "Gene deletion": return ns.onto.GeneDeletion()
    elif var_type == "Gene amplification":
        if mut_type == "Triplication": return ns.onto.GeneTriplication()
        if mut_type == "Duplication": return ns.onto.GeneDuplication()
        if mut_type == "Quadruplication": return ns.onto.GeneQuarduplication()
        if mut_type == "Extensive": return ns.onto.GeneExtensiveAmplification()
        if mut_type == "None_reported": return ns.onto.GeneMutation() # not in data so far...    
    raise DataError("SequenceVariation", f"Unexpected variation-type / mutation-type combination: {var_type} / {mut_type}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_from(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    value = cc["value"]
    elems = value.split("; ")
    contact=elems.pop(0) if len(elems) == 4 else ""
    if len(elems) != 3: 
        cl_ac = cl_IRI.split(":")[1]
        print(f"ERROR, expected 3-4 tokens in CC From comment '{value}' : {cl_ac}")
        return []
    orga_IRI = ns.orga.IRI(elems[0], elems[1], elems[2], contact)
    triples.append(cl_IRI, ns.onto._from(), orga_IRI)
    return triples

