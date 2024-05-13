import uuid
from namespace import NamespaceRegistry as ns
from ApiCommon import log_it

mmm2mm = { "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
           "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

pubtype_clazz = {
    "article": ns.onto.JournalArticle(),
    "book chapter": ns.onto.BookChapter(), # will be refined
    "patent": ns.onto.Patent(),
    "thesis BSc": ns.onto.BachelorThesis(),
    "thesis MD": ns.onto.MedicalDegreeThesis(),
    "thesis MDSc": ns.onto.MedicalDegreeMasterThesis(),
    "thesis MSc": ns.onto.MasterThesis(),
    "thesis PD": ns.onto.PrivaDocentThesis(),
    "thesis PhD": ns.onto.DoctoralThesis(),
    "thesis VMD": ns.onto.VeterinaryMedicalDegreeThesis(),
}

""" 
TODO: review how we use ns.src (add choice with orga when not done or refactor choice elsewhere )

"""

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
def get_pub_IRI(refOrPub):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    dbac = refOrPub.get("resource-internal-ref")    # exists in reference-list items
    if dbac is None: dbac = refOrPub["internal-id"] # exists in publication-list items 
    (db,ac) = dbac.split("=")
    return ns.pub.IRI(db,ac)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_xref_discontinued(xref):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return xref.get("discontinued")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_xref_label(xref):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return xref.get("label")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_xref_IRI(xref):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # get mandatory fields
    ac = xref["accession"]
    db = xref["database"]
    # get optional fields attached to the xref
    cat = xref.get("category") or ""
    lbl = xref.get("label") or ""
    url = xref.get("url") or ""
    dis = xref.get("discontinued") or ""
    props = f"cat={cat}|lbl={lbl}|dis={dis}|url={url}"
    #if props is not None: print("DEBUG props:", props)
    return ns.xref.IRI(db,ac, props)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ref_class(ref_data):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    typ = ref_data["type"]
    clazz = pubtype_clazz.get(typ) 
    if clazz is None:
        ref_id = ref_data["internal-id"]
        log_it("WARNING", f"unexpected publication type '{typ}' in {ref_id}")
        clazz = ns.onto.Publication() # default, most generic
    return clazz

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_xref_dict():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return ns.xref.dbac_dict


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_xref_key(xref_key):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # split all fields: db, ac, and props: cat(egory), lbl, url, dis(continued)
    (db,ac) = xref_key.split("=")
    xr_dict = get_xref_dict()
    prop_dict = dict()
    for props in xr_dict[xref_key]:
        for prop in props.split("|"):
            pos = prop.find("=")
            name = prop[0:pos]
            value = prop[pos+1:]
            if value != "":
                if name not in prop_dict: prop_dict[name] = set()
                prop_dict[name].add(value)

    # send a WARNING when a prop has multiple values
    singles = [ xref_key ]
    multiples = list()
    for k in sorted(prop_dict):
        vset = prop_dict[k]
        if len(vset)==1:
            for v in vset: break # get first value in set
            singles.append(k + ":" + v)
        else:
            mv = list()
            for v in vset: mv.append(v)
            multiples.append(f"Xref {xref_key} has multiple {k} : " + " | ".join(mv))
    if len(multiples) > 0:
        for m in multiples: log_it("WARNING", m)

    # build the triples and return them
    triples = TripleList()
    xr_IRI = ns.xref.IRI(db, ac, None, store=False)
    triples.append(xr_IRI, ns.rdf.type(), ns.onto.Xref())
    triples.append(xr_IRI, ns.onto.accession(), ns.xsd.string(ac))
    triples.append(xr_IRI, ns.onto.database(), ns.xsd.string(db)) 
    #TODO: represent db as a :OnlineResource and link it to xref ?
    # wait to see how xrefs are represented in other RDFs at SIB
    
    # we usually expect one item in the set associated to each key of prop_dict
    # if we get more than one item, we take the first as the prop value
    if "cat" in prop_dict:
        for value in prop_dict["cat"]: break
        triples.append(xr_IRI, ns.onto.category(), ns.xsd.string(value)) 
    if "lbl" in prop_dict:
        for value in prop_dict["lbl"]: break
        triples.append(xr_IRI, ns.rdfs.label(), ns.xsd.string(value)) 
    if "dis" in prop_dict:
        for value in prop_dict["dis"]: break
        triples.append(xr_IRI, ns.onto.discontinued(), ns.xsd.string(value)) 
    if "url" in prop_dict:
        for url in prop_dict["url"]: break
        url = "". join(["<", encode_url(url), ">"])
        triples.append(xr_IRI, ns.rdfs.seeAlso(), url) 

    return("".join(triples.lines))
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_orga_set():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_orga(name):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    return("".join(triples.lines))
    



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def encode_url(url):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # WARNING: escape to unicode is necessary for < and > and potentially for other characters...
    # some DOIs contain weird chars like in : 
    # https://dx.doi.org/10.1002/(SICI)1096-8652(199910)62:2<93::AID-AJH5>3.0.CO;2-7
    encoded_url = url.replace("<", "\\u003C").replace(">","\\u003E")
    return encoded_url

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_ref(ref_obj):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    ref_data = ref_obj["publication"]    
    ref_IRI = get_pub_IRI(ref_data)

    # class: article, thesis, patent, ... (mandatory)
    ref_class = get_ref_class(ref_data)
    triples.append(ref_IRI, ns.rdf.type(), ref_class)

    # internal id (mandatory) for debug purpose
    ref_id = ref_data["internal-id"]
    triples.append(ref_IRI, ns.onto.hasInternalId(), ns.xsd.string(ref_id))    
    #print("debug", ref_id)

    # authors (mandatory)
    for p in ref_data["author-list"]:
        p_name = p["name"]
        p_BN = get_blank_node()
        triples.append(ref_IRI, ns.onto.creator(), p_BN)
        triples.append(p_BN, ns.rdf.type(), ns.foaf.Person())
        triples.append(p_BN, ns.onto.name(), ns.xsd.string(p_name))

    # title (mandatory)
    ttl = ref_data["title"]
    triples.append(ref_IRI, ns.onto.title(), ns.xsd.string(ttl))

    # date (mandatory)
    dt = ref_data["date"]
    year = dt[-4:]
    triples.append(ref_IRI, ns.onto.hasPublicationYear(), ns.xsd.string(year))
    if len(dt) > 4:
        if len(dt) != 11: raise DataError("Publication", "Unexpecting date format in " + ref_id)
        day = dt[0:2]
        month = mmm2mm[dt[3:6]]
        #print("mydate",year,month,day)
        triples.append(ref_IRI, ns.onto.publicationDate(), ns.xsd.date("-".join([year, month, day])))

    # xref-list (mandatory), we create and xref and a direct link to the url via rdfs:seeAlso
    for xref in ref_data["xref-list"]:
        xref_IRI = get_xref_IRI(xref)
        triples.append(ref_IRI, ns.onto.xref(), xref_IRI)
        url = "". join(["<", encode_url(xref["url"]), ">"])
        triples.append(ref_IRI, ns.rdfs.seeAlso(), url )


    # first page, last page, volume, journal (optional)
    p1 = ref_data.get("first-page")
    if p1 is not None: triples.append(ref_IRI, ns.onto.startingPage(), ns.xsd.string(p1))
    p2 = ref_data.get("last-page")
    if p2 is not None: triples.append(ref_IRI, ns.onto.endingPage(), ns.xsd.string(p2))
    vol = ref_data.get("volume")
    if vol is not None: triples.append(ref_IRI, ns.onto.volume(), ns.xsd.string(vol))
    jou = ref_data.get("journal-name")
    if jou is not None: triples.append(ref_IRI, ns.onto.hasISO4JournalTitleAbbreviation(), ns.xsd.string(jou))
    
    # country and institution (for theses)
    # TODO: check after book chapter refactoring
    country = ref_data.get("country")
    institu = ref_data.get("institution")
    if country is not None and institu is not None:
        orga_IRI = ns.orga.IRI(institu, None, country, None)
        triples.append(ref_IRI, ns.onto.publisher(), orga_IRI)
    
    # city and publisher (for book chapters,...)
    # TODO: check after book chapter refactoring
    city = ref_data.get("city")
    publisher = ref_data.get("publisher")
    if city is not None and publisher is not None:
        orga_IRI = ns.orga.IRI(publisher, city, None, None)
        triples.append(ref_IRI, ns.onto.publisher(), orga_IRI)

    # editors (optional)
    for p in ref_data.get("editor-list") or []:
        p_name = p["name"]
        p_BN = get_blank_node()
        triples.append(ref_IRI, ns.onto.editor(), p_BN)
        triples.append(p_BN, ns.rdf.type(), ns.foaf.Person())
        triples.append(p_BN, ns.onto.name(), ns.xsd.string(p_name))

    return("".join(triples.lines))

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
        xref_IRI = get_xref_IRI(xref)
        triples.append(cl_IRI, ns.onto.xref(), xref_IRI)
        if get_xref_discontinued(xref):
            triples.extend(get_ttl_for_cc_discontinued(cl_IRI, xref["database"], xref["accession"], xref_IRI)) # also used for "CC   Discontinued: " lines       

    # fields: RX
    for rx in cl_data.get("reference-list") or []:
        triples.append(cl_IRI, ns.onto.reference(), get_pub_IRI(rx))
 
    # fields: WW
    for ww in cl_data.get("web-page-list") or []:
        ww_iri = "".join(["<", ww, ">"])
        triples.append(cl_IRI, ns.rdfs.seeAlso(), ww_iri)
    
    # fields: SX
    sx = cl_data.get("sex")
    if sx is not None:
        triples.append(cl_IRI, ns.onto.fromIndividualWithSex(), ns.xsd.string(sx))

    # fields: AG
    ag = cl_data.get("age")
    if ag is not None:
        triples.append(cl_IRI, ns.onto.fromIndividualAtAge(), ns.xsd.string(ag))

    # fields: OI
    for oi in cl_data.get("same-origin-as") or []:
        oi_iri = ns.cvcl.IRI(oi["accession"])
        triples.append(cl_IRI, ns.onto.fromSameIndividualAs(), oi_iri)

    # fields: HI
    for hi in cl_data.get("derived-from") or []:
        hi_iri = ns.cvcl.IRI(hi["accession"])
        triples.append(cl_IRI, ns.onto.parentCellLine(), hi_iri)

    # fields: CH
    for ch in cl_data.get("child-list") or []:
        ch_iri = ns.cvcl.IRI(ch["accession"]["value"])
        triples.append(cl_IRI, ns.onto.childCellLine(), ch_iri)

    # fields: CA
    ca = cl_data["category"] # we expect one value for each cell line
    if ca is not None:
        triples.append(cl_IRI, ns.onto.category(), ns.xsd.string(ca))

    # fields DT, dtc, dtu, dtv
    triples.append(cl_IRI, ns.onto.cvclEntryCreated(), ns.xsd.date(cl_data["created"]))
    triples.append(cl_IRI, ns.onto.cvclEntryLastUpdated(), ns.xsd.date(cl_data["last-updated"]))
    triples.append(cl_IRI, ns.onto.cvclEntryVersion(), ns.xsd.integer(cl_data["entry-version"]))

    # fields: CC, genome-ancestry
    annot = cl_data.get("genome-ancestry")
    if annot is not None:
        annot_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.genomeAncestry(), annot_BN)
        triples.append(annot_BN, ns.rdf.type() ,ns.onto.GenomeAncestry())
        # ref can be publi or organization, but only publi in real data
        src = annot.get("source")
        if src is not None: 
            triples.extend(get_ttl_for_source(annot_BN, src))
        else:
            log_it("ERROR", f"reference of genome-ancestry source is null: {ac}")
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
        src = annot.get("source")
        if src is not None: 
            triples.extend(get_ttl_for_source(annot_BN, src))
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


    # fields: CC str, WARNING: str-list is not a list !!!
    annot = cl_data.get("str-list")
    if annot is not None:
        triples.extend(get_ttl_for_short_tandem_repeat(cl_IRI, annot))

    # fields: di
    for annot in cl_data.get("disease-list") or []:
        triples.extend(get_ttl_for_disease(cl_IRI, annot))

    # fields: ox
    for annot in cl_data.get("species-list") or []:
        triples.extend(get_ttl_for_species(cl_IRI, annot))

    # fields: CC sequence-variation
    for annot in cl_data.get("sequence-variation-list") or []:
        triples.extend(get_ttl_for_sequence_variation(cl_IRI, annot))

    # fields: derived-from-site
    for annot in cl_data.get("derived-from-site-list") or []:
        triples.extend(get_ttl_for_derived_from_site(cl_IRI, annot))

    ct_annot = cl_data.get("cell-type")
    if ct_annot is not None:
        triples.extend(get_ttl_for_cell_type(cl_IRI, ct_annot))

    # fields: CC doubling-time
    for annot in cl_data.get("doubling-time-list") or []:
        triples.extend(get_ttl_for_doubling_time(cl_IRI, annot))

    # fields: CC transformant
    for annot in cl_data.get("transformant-list") or []:
        triples.extend(get_ttl_for_transformant(cl_IRI, annot))

    # fields: CC msi
    for annot in cl_data.get("microsatellite-instability-list") or []:
        triples.extend(get_ttl_for_msi(cl_IRI, annot))

    # fields: CC mab-isotype
    for annot in cl_data.get("monoclonal-antibody-isotype-list") or []:
        triples.extend(get_ttl_for_mab_isotype(cl_IRI, annot))

    # fields: CC mab-target
    for annot in cl_data.get("monoclonal-antibody-target-list") or []:
        triples.extend(get_ttl_for_mab_target(cl_IRI, annot))

    # fields: CC resistance
    for annot in cl_data.get("resistance-list") or []:
        triples.extend(get_ttl_for_resistance(cl_IRI, annot))

    # fields: CC knockout
    for annot in cl_data.get("knockout-cell-list") or []:
        triples.extend(get_ttl_for_cc_knockout_cell(cl_IRI, annot))


    # fields: CC from, ...
    for cc in cl_data.get("comment-list") or []:
        categ = cc["category"]
        if categ == "From": 
            triples.extend(get_ttl_for_cc_from(cl_IRI, cc))
        elif categ == "Part of":
            triples.extend(get_ttl_for_cc_part_of(cl_IRI, cc))            
        elif categ == "Group":
            triples.extend(get_ttl_for_cc_in_group(cl_IRI, cc))
        elif categ == "Breed/subspecies":
            triples.extend(get_ttl_for_cc_breed(cl_IRI, cc))
        elif categ == "Anecdotal":
            triples.extend(get_ttl_for_cc_anecdotal(cl_IRI, cc))
        elif categ == "Biotechnology":
            triples.extend(get_ttl_for_cc_biotechnology(cl_IRI, cc))
        elif categ == "Characteristics":
            triples.extend(get_ttl_for_cc_characteristics(cl_IRI, cc))
        elif categ == "Caution":
            triples.extend(get_ttl_for_cc_caution(cl_IRI, cc))
        elif categ == "Donor information":
            triples.extend(get_ttl_for_cc_donor_info(cl_IRI, cc))
        elif categ == "Discontinued":
            provider, product_id = cc["value"].split("; ")
            triples.extend(get_ttl_for_cc_discontinued(cl_IRI, provider, product_id)) # also used in DR lines
        elif categ == "Karyotypic information":
            triples.extend(get_ttl_for_cc_karyotypic_info(cl_IRI, cc))
        elif categ == "Miscellaneous":
            triples.extend(get_ttl_for_cc_miscellaneous_info(cl_IRI, cc))
        elif categ == "Senescence":
            triples.extend(get_ttl_for_cc_senescence_info(cl_IRI, cc))
        elif categ == "Virology":
            triples.extend(get_ttl_for_cc_virology_info(cl_IRI, cc))
        elif categ == "Omics":
            triples.extend(get_ttl_for_cc_omics_info(cl_IRI, cc))
        elif categ == "Population":
            triples.extend(get_ttl_for_cc_population_info(cl_IRI, cc))

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
        var_sources = annot.get("source-list") or []
        triples.extend(get_ttl_for_sources(annot_BN, var_sources))

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
            if len(hgvs_list) not in [1,2]: log_it("WARNING", f"invalid hgvs in: {label}")
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
        log_it("ERROR", f"{typ} - {details} : {cl_ac}")
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
        log_it("ERROR", f"expected 3-4 tokens in CC From comment '{value}' : {cl_ac}")
        return []
    orga_IRI = ns.orga.IRI(elems[0], elems[1], elems[2], contact)
    triples.append(cl_IRI, ns.onto._from(), orga_IRI)
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_part_of(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    label = cc["value"]
    coll_IRI = ns.coll.IRI(label)
    triples.append(cl_IRI, ns.onto.partOf(), coll_IRI)
    triples.append(coll_IRI, ns.rdf.type(), ns.onto.CellLineCollection())
    triples.append(coll_IRI, ns.rdfs.label(), ns.xsd.string(label))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_in_group(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    label = cc["value"]
    grp_IRI = ns.grp.IRI(label)
    triples.append(cl_IRI, ns.onto.group(), grp_IRI)
    triples.append(grp_IRI, ns.rdf.type(), ns.onto.CellLineGroup())
    triples.append(grp_IRI, ns.rdfs.label(), ns.xsd.string(label))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_breed(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    label = cc["value"]
    inst_IRI = ns.breed.IRI(label)
    triples.append(cl_IRI, ns.onto.breed(), inst_IRI)
    triples.append(inst_IRI, ns.rdf.type(), ns.onto.Breed())
    triples.append(inst_IRI, ns.rdfs.label(), ns.xsd.string(label))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_characteristics(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.characteristicsComment(), inst_BN)
    triples.append(inst_BN, ns.rdf.type(), ns.onto.CharacteristicsComment())
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_caution(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.cautionComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent propery
    triples.append(inst_BN, ns.rdf.type(), ns.onto.CautionComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_biotechnology(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.biotechnologyComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent propery
    triples.append(inst_BN, ns.rdf.type(), ns.onto.BiotechnologyComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_anecdotal(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.anecdotalComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.AnecdotalComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_donor_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.donorInfoComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.DonorInfoComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))

    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_karyotypic_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.karyotypicInfoComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.KaryotypicInfoComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_miscellaneous_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.miscellaneousInfoComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.MiscellaneousInfoComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_senescence_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.senescenceComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.SenescenceComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_virology_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.virologyComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.VirologyComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_knockout_cell(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    method = cc.get("knockout-method")
    comment = cc.get("knockout-cell-note") # optional
    xref = cc.get("xref")
    if method is None or xref is None:
        log_it("WARNING", f"missing method or gene xref in knockout comment in {cl_IRI}")
    else:
        inst_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.knockout(), inst_BN)
        triples.append(inst_BN, ns.rdf.type(), ns.onto.KnockoutComment())
        triples.append(inst_BN, ns.onto.method(), ns.xsd.string(method))
        triples.append(inst_BN, ns.onto.gene(), get_xref_IRI(xref))
        if comment is not None: 
            triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_omics_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.omicsComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.OmicsComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_population_info(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    comment = cc["value"]
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.populationComment(), inst_BN)
    triples.append(cl_IRI, ns.onto.freeTextComment(), inst_BN) # parent property
    triples.append(inst_BN, ns.rdf.type(), ns.onto.PopulationComment())
    triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    return triples



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_derived_from_site(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    site_BN = get_blank_node()
    note = annot.get("site-note")
    site = annot["site"]
    site_type = site["site-type"]
    label = site["value"]
    triples.append(cl_IRI, ns.onto.derivedFromSite(), site_BN)
    triples.append(site_BN, ns.rdf.type(), ns.onto.AnatomicalElement())
    triples.append(site_BN, ns.onto.siteType(), ns.xsd.string(site_type))
    triples.append(site_BN, ns.rdfs.label(), ns.xsd.string(label))
    if note is not None:
        triples.append(site_BN, ns.rdfs.comment(), ns.xsd.string(note)) 
    for xref in site.get("xref-list") or []: 
        triples.append(site_BN, ns.onto.xref(), get_xref_IRI(xref))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cell_type(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    ct_BN = get_blank_node()
    if isinstance(annot, str):  # when we have free text only without a xref
        label, cv = (annot, None)
    else:
        label, cv = (annot["value"], annot.get("xref"))
    triples.append(cl_IRI, ns.onto.cellType(), ct_BN)
    triples.append(ct_BN, ns.rdf.type(), ns.onto.CellType())
    triples.append(ct_BN, ns.rdfs.label(), ns.xsd.string(label))    
    if cv is not None: triples.append(ct_BN, ns.onto.xref(), get_xref_IRI(cv))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_cc_discontinued(cl_IRI, provider, product_id, xref_IRI=None):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.discontinued(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.DiscontinuationRecord())
    triples.append(annot_BN, ns.onto.provider(), ns.xsd.string(provider))
    triples.append(annot_BN, ns.onto.productId(), ns.xsd.string(product_id))
    if xref_IRI is not None:
        triples.append(annot_BN, ns.onto.xref(), xref_IRI)
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_source(parentNode, src):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # TODO: use a source checker here or where we create the sources
    # TODO: decide if we keep the embedding of xref, ref, org, src within a :Source blank node
    triples = TripleList()
    src_BN = get_blank_node()
    triples.append(parentNode, ns.onto.source(), src_BN)
    triples.append(src_BN, ns.rdf.type(), ns.onto.Source())
    if type(src) == dict:
        lbl = src.get("value")
        if lbl is not None:
            triples.append(src_BN, ns.rdfs.label(), ns.xsd.string(lbl))
        xref = src.get("xref")
        if xref is not None:
            triples.append(src_BN, ns.onto.xref(), get_xref_IRI(xref))
        ref =src.get("reference")
        if ref is not None: 
            triples.append(src_BN, ns.onto.reference(), get_pub_IRI(ref))
    elif type(src) == str:
        if src == "Direct_author_submission" or src.startswith("from inference of"):
            triples.append(src_BN, ns.rdfs.label(), ns.xsd.string(src))
        else:
            src_IRI = ns.orga.IRI(src, "", "", "")
            triples.append(src_BN, ns.onto.organization(), src_IRI)
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_sources(parentNode, sources):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    for src in sources or []:
        triples.extend(get_ttl_for_source(parentNode, src))
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_doubling_time(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    duration = annot["doubling-time-value"]
    comment = annot.get("doubling-time-note")
    sources = annot.get("source-list") or [] 
    triples.append(cl_IRI, ns.onto.doublingTimeComment(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.DoublingTimeComment())
    triples.append(annot_BN, ns.onto.duration(), ns.xsd.string(duration))
    if comment is not None: triples.append(annot_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(annot_BN, sources))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_msi(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    value = annot["msi-value"]
    comment = annot.get("microsatellite-instability-note")
    sources = annot.get("source-list") or [] 
    triples.append(cl_IRI, ns.onto.microsatelliteInstability(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.MicrosatelliteInstability())
    triples.append(annot_BN, ns.onto.msiValue(), ns.xsd.string(value))
    if comment is not None: triples.append(annot_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    triples.extend(get_ttl_for_sources(annot_BN, sources))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_mab_isotype(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    heavy = annot["heavy-chain"]
    light = annot.get("light-chain")
    sources = annot.get("source-list") or []
    triples.append(cl_IRI, ns.onto.mabIsotype(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.MabIsotype())
    triples.append(annot_BN, ns.onto.heavyChain(), ns.xsd.string(heavy))
    if light is not None: triples.append(annot_BN, ns.onto.lightChain(), ns.xsd.string(light))
    triples.extend(get_ttl_for_sources(annot_BN, sources))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_mab_target(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.mabTarget(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.Antigen())
    # we might get a simple string in annot (the name of the antigen)
    if type(annot) == str:
        triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(annot))
        return triples
    # or more often we get a dict object
    comment = annot.get("monoclonal-antibody-target-note")
    if comment is not None:
        triples.append(annot_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    # we might get just a name and a comment
    name = annot.get("value")
    xref = annot.get("xref")
    # or the name is in the xref
    if xref is not None:
        name = get_xref_label(xref)
        xref_IRI = get_xref_IRI(xref)
        triples.append(annot_BN, ns.onto.xref(), xref_IRI)
    triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(name))
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_resistance(cl_IRI, annot):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.resistance(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.ChemicalAgent())
    # we might get a simple string in annot (the name of the chemical)
    if type(annot) == str:
        triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(annot))
    # or more often we get a dict object
    else:
        xref = annot.get("xref")
        name = get_xref_label(xref)
        xref_IRI = get_xref_IRI(xref)
        triples.append(annot_BN, ns.onto.xref(), xref_IRI)
        triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(name))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_transformant(cl_IRI, cc):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    inst_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.transformant(), inst_BN)
    triples.append(inst_BN, ns.rdf.type(), ns.onto.TransformantAgent())

    # we might get a simple string in annot (the name of the chemical)
    if type(cc) == str:
        triples.append(inst_BN, ns.rdfs.label(), ns.xsd.string(cc))
    # or more often we get a dict object
    else:
        comment = cc.get("transformant-note") # optional
        term = cc.get("xref") # optional too
        inst_BN = get_blank_node()
        triples.append(cl_IRI, ns.onto.transformant(), inst_BN)
        triples.append(inst_BN, ns.rdf.type(), ns.onto.TransformantAgent())
        if term is not None:
            triples.append(inst_BN, ns.onto.xref(), get_xref_IRI(term))
            label = get_xref_label(term)
            triples.append(inst_BN, ns.rdfs.label(), ns.xsd.string(label))
        else:
            label = cc["value"] 
            triples.append(inst_BN, ns.rdfs.label(), ns.xsd.string(label))
        if comment is not None: 
            triples.append(inst_BN, ns.rdfs.comment(), ns.xsd.string(comment))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_short_tandem_repeat(cl_IRI, annot):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.shortTandemRepeatProfile(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.ShortTandemRepeatProfile())
    sources = annot["source-list"]
    triples.extend(get_ttl_for_sources(annot_BN, sources))
    for marker in annot["marker-list"]:
        marker_id = marker["id"]
        conflict = marker["conflict"]
        for data in marker["marker-data-list"]:
            marker_BN = get_blank_node()
            alleles = data["marker-alleles"]
            triples.append(annot_BN, ns.onto.markerAlleles(), marker_BN)
            triples.append(marker_BN, ns.rdf.type(), ns.onto.MarkerAlleles())
            triples.append(marker_BN, ns.onto.markerId(), ns.xsd.string(marker_id))
            triples.append(marker_BN, ns.onto.conflict(), ns.xsd.boolean(conflict))
            triples.append(marker_BN, ns.onto.alleles(), ns.xsd.string(alleles))
            marker_sources = data.get("source-list") or []
            triples.extend(get_ttl_for_sources(marker_BN, marker_sources))
    return triples


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_disease(cl_IRI, cvterm):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.fromIndividualWithDisease(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.Disease())
    name = get_xref_label(cvterm)
    xref_IRI = get_xref_IRI(cvterm)
    triples.append(annot_BN, ns.onto.xref(), xref_IRI)
    triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(name))
    return triples

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_ttl_for_species(cl_IRI, xref):    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    triples = TripleList()
    annot_BN = get_blank_node()
    triples.append(cl_IRI, ns.onto.fromIndividualBelongingToSpecies(), annot_BN)
    triples.append(annot_BN, ns.rdf.type(), ns.onto.Species())
    name = get_xref_label(xref)
    xref_IRI = get_xref_IRI(xref)
    triples.append(annot_BN, ns.onto.xref(), xref_IRI)
    triples.append(annot_BN, ns.rdfs.label(), ns.xsd.string(name))
    return triples
