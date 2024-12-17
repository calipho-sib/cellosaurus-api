import uuid
import unicodedata
from namespace_registry import NamespaceRegistry as ns
from ApiCommon import log_it
from organizations import Organization
from terminologies import Term, Terminologies, Terminology
from databases import Database, Databases, get_db_category_IRI
from sexes import Sexes, Sex, get_sex_IRI

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


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  
class RdfBuilder:
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, known_orgs): 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        self.known_orgs = known_orgs

        self.mmm2mm = { 
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", 
            "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

        # publication type label => publication class
        self.pubtype_clazz = {
            "article": ns.fabio.JournalArticle,
            "book chapter": ns.fabio.BookChapter,
            "patent":       ns.fabio.PatentDocument,
            "thesis BSc":   ns.fabio.BachelorsThesis,
            "thesis MSc":   ns.fabio.MastersThesis,
            "thesis PhD":   ns.fabio.DoctoralThesis,
            "book":         ns.fabio.Book,
            "conference":   ns.fabio.ConferencePaper,
            "thesis MDSc":  ns.cello.MedicalDegreeMasterThesis,
            "thesis MD":    ns.cello.MedicalDegreeThesis,
            "thesis PD":    ns.cello.PrivaDocentThesis,
            "thesis VMD":   ns.cello.VeterinaryMedicalDegreeThesis,
            "technical document":       ns.cello.TechnicalDocument,
            "miscellaneous document":   ns.cello.MiscellaneousDocument,            
        }

        self.hla_clazz = {
            "HLA-DRA": ns.NCIt.C101157,
            "HLA-DRB2": ns.NCIt.C190000,
            "HLA-DRB1": ns.NCIt.C19409,
            "HLA-A": ns.NCIt.C28585,
            "HLA-DPB1": ns.NCIt.C29953,
            "HLA-C": ns.NCIt.C62758,
            "HLA-B": ns.NCIt.C62778,
            "HLA-DQB1": ns.NCIt.C70614,
            "HLA-DRB3": ns.NCIt.C71259,
            "HLA-DRB4": ns.NCIt.C71261,
            "HLA-DRB5": ns.NCIt.C71263,
            "HLA-DQA1": ns.NCIt.C71265,
            "HLA-DPA1": ns.NCIt.C71267,
            "HLA-DRB6": ns.OGG._3000003128,
            "HLA-DRB9": ns.OGG._3000003132,
        }

        # genome editing method labels => class
        self.gem_clazz = {
            "CRISPR/Cas9": ns.FBcv._0003008,
            "X-ray": ns.NCIt.C17262,
            "Gamma radiation": ns.NCIt.C44386,
            "Transfection": ns.OBI._0001152,
            "Mutagenesis": ns.OBI._0001154,
            "siRNA knockdown": ns.OBI._0002626,
            "TALEN": ns.OBI._0003134,
            "ZFN": ns.OBI._0003135,
            "Gene trap": ns.OBI._0003137,
            "Not specified": ns.OBI.GenomeModificationMethod,
            "Transduction": ns.OBI._0600059,
            "BAC homologous recombination": ns.cello.BacHomologousRecombination,
            "Cre/loxP": ns.cello.CreLoxp,
            "CRISPR/Cas9n": ns.cello.CrisprCas9N,
            "EBV-based vector siRNA knockdown": ns.cello.EbvBasedVectorSirnaKnockdown,
            "Floxing/Cre recombination": ns.cello.FloxingCreRecombination,
            "Gene-targeted KO mouse": ns.cello.GeneTargetedKoMouse,
            "Helper-dependent adenoviral vector": ns.cello.HelperDependentAdenoviralVector,
            "Homologous recombination": ns.cello.HomologousRecombination,
            "Knockout-first conditional": ns.cello.KnockoutFirstConditional,
            "KO mouse": ns.cello.KoMouse,
            "KO pig": ns.cello.KoPig,
            "miRNA knockdown": ns.cello.MirnaKnockdown,
            "Null mutation": ns.cello.NullMutation,
            "P-element": ns.cello.PElement,
            "PiggyBac transposition": ns.cello.PiggybacTransposition,
            "Prime editing": ns.cello.PrimeEditing,
            "Promoterless gene targeting": ns.cello.PromoterlessGeneTargeting,
            "Recombinant Adeno-Associated Virus": ns.cello.RecombinantAdenoAssociatedVirus,
            "shRNA knockdown": ns.cello.ShrnaKnockdown,
            "Sleeping Beauty transposition": ns.cello.SleepingBeautyTransposition,
            "Spontaneous mutation": ns.cello.SpontaneousMutation,
            "Targeted integration": ns.cello.TargetedIntegration,
            "Transduction/transfection": ns.cello.TransductionTransfection,
            "Transfection/transduction": ns.cello.TransfectionTransduction,
            "Transgenic fish": ns.cello.TransgenicFish,
            "Transgenic mouse": ns.cello.TransgenicMouse,
            "Transgenic rat": ns.cello.TransgenicRat,
        }

        # cell line category => cell line class
        self.clcat_clazz = dict()
        for id in ns.wd.terms:
            term = ns.wd.terms[id]
            if "owl:Class" in term.props["rdf:type"]:
                xsdlabel = term.props["rdfs:label"].pop()
                label = xsdlabel.split("\"")[1]
                self.clcat_clazz[label] = term.iri
        self.clcat_clazz["Undefined cell line type"] = ns.wd.CellLine # generic cell line


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_blank_node(self):
    # -- - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return "_:BN" + uuid.uuid4().hex


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for item in ns.namespaces:
            lines.append(item.getTtlPrefixDeclaration())
        return "\n".join(lines) + "\n"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_sparql_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for item in ns.namespaces:
            lines.append(item.getSparqlPrefixDeclaration())
        return "\n".join(lines) + "\n"





    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_pub_IRI(self, refOrPub):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        #print(">>>",refOrPub)
        dbac = refOrPub.get("resource-internal-ref")    # exists in reference-list items
        if dbac is None: dbac = refOrPub["internal-id"] # exists in publication-list items
        (db,ac) = dbac.split("=")
        return ns.pub.IRI(db,ac)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_discontinued(self, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return xref.get("discontinued")


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_label(self, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return xref.get("label")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_url(self, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return xref.get("url")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_db(self, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return xref.get("database")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_IRI(self, xref):
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
    def get_amelogenin_gene_xref_IRI(self, chr):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ac = "461" if chr == "X" else "462"
        db = "HGNC"
        cat = "Organism-specific databases"
        lbl = "AMEL" + chr
        url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:{ac}"
        dis = ""
        props = f"cat={cat}|lbl={lbl}|dis={dis}|url={url}"
        return ns.xref.IRI(db,ac, props)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_amelogenin_gene_instance(self, gene_BN, chr):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
        triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(f"AMEL{chr}"))
        xref_IRI = self.get_amelogenin_gene_xref_IRI(chr)
        triples.append(gene_BN, ns.cello.xref, xref_IRI)
        return triples
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_hla_gene_class_IRI(self, our_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        clazz = self.hla_clazz.get(our_label)
        if clazz is None:
            log_it("ERROR", f"unexpected HLA Gene label '{our_label}'")
            clazz = ns.cello.HLAGene # default, most generic
        return clazz


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_gem_class_IRI(self, gem_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        clazz = self.gem_clazz.get(gem_label)
        if clazz is None:
            log_it("ERROR", f"unexpected genome editing method '{gem_label}'")
            clazz = ns.OBI.GenomeModificationMethod # default, most generic
        return clazz


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_gem_clean_label(self, label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if label == "Not specified": return "Genome modification method" # return label of generic class name
        return label


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_cl_category_class_IRI(self, category_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        clazz = self.clcat_clazz.get(category_label)
        if clazz is None:
            log_it("ERROR", f"unexpected cell line category '{category_label}'")
            clazz = ns.wd.CellLine # default, most generic
        return clazz


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ref_class_IRI(self, ref_data):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        typ = ref_data["type"]
        clazz = self.pubtype_clazz.get(typ) 
        if clazz is None:
            ref_id = ref_data["internal-id"]
            log_it("ERROR", f"unexpected publication type '{typ}' in {ref_id}")
            clazz = ns.cello.Publication # default, most generic
        return clazz

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_xref_dict(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return ns.xref.dbac_dict



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_sex(self, sex: Sex):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        sex_IRI = get_sex_IRI(sex.label)
    
        # either 
        # as a subclass of :Sex (more compatible with wikidata sexes ?)
        # triples.append(sex_IRI, ns.rdf.type, ns.owl.Class)
        # triples.append(sex_IRI, ns.rdfs.subClassOf, ns.cello.Sex)
        # triples.append(sex_IRI, ns.rdfs.label, ns.xsd.string(sex.label))

        # or 
        # as a named individual of type :Sex
        triples.append(sex_IRI, ns.rdf.type, ns.cello.Sex)
        triples.append(sex_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.append(sex_IRI, ns.rdfs.label, ns.xsd.string(sex.label))    

        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(sex_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)
    


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cello_terminology_individual(self, termi):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # Note: some databases are also declared as terminologies
        triples = TripleList()
        termi_IRI = self.get_terminology_or_database_IRI(termi.abbrev)
        triples.append(termi_IRI, ns.rdf.type, ns.cello.CelloConceptScheme)
        triples.append(termi_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.append(termi_IRI, ns.rdfs.label, ns.xsd.string(termi.name))
        triples.append(termi_IRI, ns.cello.shortname, ns.xsd.string(termi.abbrev))
        triples.append(termi_IRI, ns.cello.hasVersion, ns.xsd.string(termi.version))
        triples.append(termi_IRI, ns.rdfs.seeAlso, "<" + termi.url + ">")
        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(termi_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cello_database_individual(self, db: Database):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # Note1 : some databases are also declared as terminologies
        # Note2 : in UniProt, a database is an instance of class up:Database
        #       : in cello, we define a database as an instance of cello:Database subclass
        #       : and as a NamedIndividual
        triples = TripleList()
        db_IRI = self.get_terminology_or_database_IRI(db.rdf_id)
        triples.append(db_IRI, ns.rdf.type, get_db_category_IRI(db.cat))
        triples.append(db_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.append(db_IRI, ns.rdfs.label, ns.xsd.string(db.name))
        triples.append(db_IRI, ns.cello.shortname, ns.xsd.string(db.abbrev))
        if db.in_up:
            up_db = "<http://purl.uniprot.org/database/" + db.abbrev + ">"
            #triples.append(db_IRI, ns.owl.sameAs, up_db) # <=============== link between up and cello instances
            triples.append(db_IRI, ns.skos.exactMatch, up_db) # <=============== link between up and cello instances
        triples.append(db_IRI, ns.rdfs.seeAlso, "<" + db.url + ">")
        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(db_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_term(self, term):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        # term IRI is built like xref IRI
        # note that sometimes an IRI is both a :Xref and a:Concept 
        db = term.scheme
        ac = term.id
        xr_IRI = ns.xref.IRI(db, ac, None, store=False)
        triples.append(xr_IRI, ns.rdf.type, ns.skos.Concept)
        triples.append(xr_IRI, ns.skos.inScheme, self.get_terminology_or_database_IRI(term.scheme))
        no_accent_label = self.remove_accents(term.prefLabel)
        triples.append(xr_IRI, ns.skos.prefLabel, ns.xsd.string(no_accent_label))
        triples.append(xr_IRI, ns.skos.notation, ns.xsd.string(term.id))
        for alt in term.altLabelList:
            no_accent_label = self.remove_accents(alt)
            triples.append(xr_IRI, ns.skos.altLabel, ns.xsd.string(no_accent_label))
        for parent_id in term.parentIdList:
            parent_IRI = ns.xref.IRI(db, parent_id, None, store=False)
            triples.append(xr_IRI, ns.cello.more_specific_than, parent_IRI)

        return("".join(triples.lines))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_terminology_or_database_IRI(self, abbrev):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return  "db:" + abbrev


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_xref_key(self, xref_key):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # split all fields: db, ac, and props: cat(egory), lbl, url, dis(continued)
        (db,ac) = xref_key.split("=")
        xr_dict = self.get_xref_dict()
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
        triples.append(xr_IRI, ns.rdf.type, ns.cello.Xref)
        triples.append(xr_IRI, ns.cello.accession, ns.xsd.string(ac))

        # TODO: represent db as a :OnlineResource and link it to xref ?
        # wait to see how xrefs are represented in other RDFs at SIB
        # triples.append(xr_IRI, ns.cello.database, ns.xsd.string(db))
        # if "cat" in prop_dict:
        #     for value in prop_dict["cat"]: break
        #     triples.append(xr_IRI, ns.cello.category, ns.xsd.string(value)) 
        # DONE
        triples.append(xr_IRI, ns.cello.database,  self.get_terminology_or_database_IRI(ns.xref.cleanDb(db))) 

        # we usually expect one item in the set associated to each key of prop_dict
        # if we get more than one item, we take the first as the prop value
        if "lbl" in prop_dict:
            for value in prop_dict["lbl"]: break
            triples.append(xr_IRI, ns.rdfs.label, ns.xsd.string(value)) 
        if "dis" in prop_dict:
            for value in prop_dict["dis"]: break
            triples.append(xr_IRI, ns.cello.discontinued, ns.xsd.string(value)) 
        if "url" in prop_dict:
            for url in prop_dict["url"]: break
            url = "". join(["<", self.encode_url(url), ">"])
            triples.append(xr_IRI, ns.rdfs.seeAlso, url) 

        return("".join(triples.lines))
        

    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_orga_dict(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return ns.orga.nccc_dict

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_org_merged_with_known_org(self, org: Organization):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # if we just have a name, try to merge with a known org 
        # defined in institution_list and cellosaurus_xrefs.txt

        korg = self.known_orgs.get(org.name) 
        if korg is not None: 
            # if one of the following fields is not None or a non empty string, emit WARNING
            if org.shortname or org.city or org.country or org.contact:
                print(f"WARNING, we are merging\n{org}\nwith\n{korg}")
            # merge org with korg
            org.name = korg.name
            org.shortname = korg.shortname
            org.city = korg.city
            org.country = korg.country
            org.contact = korg.contact
            org.isInstitute = korg.isInstitute
            org.isOnlineResource = korg.isOnlineResource
        return org

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_orga(self, data, count):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # build an org object from data collected from annotations
        (name, shortname, city, country, contact) = data.split("|")
        if shortname == "": shortname = None
        if city == "": city = None
        if country == "": country = None
        if contact == "": contact = None
        org = Organization(name=name, shortname=shortname, city=city, country=country, contact=contact)

        #print("org",count, org)
        
        # build the triples and return them
        triples = TripleList()

        orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store = False)
        triples.append(orga_IRI, ns.rdf.type, ns.schema.Organization)
        triples.append(orga_IRI, ns.cello.name, ns.xsd.string(org.name))

        if org.shortname is not None and len(org.shortname)>0:
            triples.append(orga_IRI, ns.cello.shortname, ns.xsd.string(org.shortname))

        if org.city is not None and len(org.city)>0:
            triples.append(orga_IRI, ns.cello.city, ns.xsd.string(org.city))

        if org.country is not None and len(org.country)>0:
            triples.append(orga_IRI, ns.cello.country, ns.xsd.string(org.country))

        if org.contact is not None and len(org.contact)>0:
            for name in org.contact.split(" and "):
                p_BN = self.get_blank_node()
                triples.append(p_BN, ns.rdf.type, ns.schema.Person)
                triples.append(p_BN, ns.cello.name, ns.xsd.string(name))
                triples.append(p_BN, ns.cello.memberOf, orga_IRI)

        return("".join(triples.lines))
        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def remove_accents(self, input_str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - 
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def encode_url(self, url):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # WARNING: escape to unicode is necessary for < and > and potentially for other characters...
        # some DOIs contain weird chars like in : 
        # https://dx.doi.org/10.1002/(SICI)1096-8652(199910)62:2<93::AID-AJH5>3.0.CO;2-7
        encoded_url = url.replace("<", "\\u003C").replace(">","\\u003E")
        return encoded_url

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_ref(self, ref_obj):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        ref_data = ref_obj["publication"]    
        ref_IRI = self.get_pub_IRI(ref_data)

        # class: article, thesis, patent, ... (mandatory)
        ref_class = self.get_ref_class_IRI(ref_data)
        triples.append(ref_IRI, ns.rdf.type, ref_class)

        # internal id (mandatory) for debug purpose
        ref_id = ref_data["internal-id"]
        triples.append(ref_IRI, ns.cello.hasInternalId, ns.xsd.string(ref_id))    
        #print("debug", ref_id)

        # authors (mandatory)
        for p in ref_data["author-list"]:
            p_type = p.get("type")
            p_name = p["name"]
            if p_type == "consortium":
                orga_IRI = ns.orga.IRI(p_name, None, None, None, None)
                triples.append(ref_IRI, ns.dcterms.creator, orga_IRI)
            else:
                for name in p_name.split(" and "):                
                    p_BN = self.get_blank_node()
                    triples.append(ref_IRI, ns.dcterms.creator, p_BN)
                    triples.append(p_BN, ns.rdf.type, ns.schema.Person)
                    triples.append(p_BN, ns.cello.name, ns.xsd.string(name))

        # title (mandatory)
        ttl = ref_data["title"]
        triples.append(ref_IRI, ns.dcterms.title, ns.xsd.string(ttl))

        # date (mandatory)
        dt = ref_data["date"]
        year = dt[-4:]
        triples.append(ref_IRI, ns.fabio.hasPublicationYear, ns.xsd.string(year))
        if len(dt) > 4:
            if len(dt) != 11: raise DataError("Publication", "Unexpecting date format in " + ref_id)
            day = dt[0:2]
            month = self.mmm2mm[dt[3:6]]
            #print("mydate",year,month,day)
            triples.append(ref_IRI, ns.prism.publicationDate, ns.xsd.date("-".join([year, month, day])))

        # xref-list (mandatory), we create and xref and a direct link to the url via rdfs:seeAlso
        for xref in ref_data["xref-list"]:
            accession = xref["accession"]
            if self.get_xref_db(xref) == "PubMed": triples.append(ref_IRI, ns.fabio.hasPubMedId, ns.xsd.string(accession))
            elif self.get_xref_db(xref) == "DOI": triples.append(ref_IRI, ns.prism.hasDOI, ns.xsd.string3(accession))
            elif self.get_xref_db(xref) == "PMCID": triples.append(ref_IRI, ns.fabio.hasPubMedCentralId, ns.xsd.string(accession))
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(ref_IRI, ns.cello.xref, xref_IRI)
            url = "". join(["<", self.encode_url(xref["url"]), ">"])
            triples.append(ref_IRI, ns.rdfs.seeAlso, url )


        # first page, last page, volume, journal (optional)
        p1 = ref_data.get("first-page")
        if p1 is not None: triples.append(ref_IRI, ns.prism.startingPage, ns.xsd.string(p1))
        p2 = ref_data.get("last-page")
        if p2 is not None: triples.append(ref_IRI, ns.prism.endingPage, ns.xsd.string(p2))
        vol = ref_data.get("volume")
        if vol is not None: triples.append(ref_IRI, ns.prism.volume, ns.xsd.string(vol))
        jou = ref_data.get("journal-name")
        if jou is not None: triples.append(ref_IRI, ns.cello.hasISO4JournalTitleAbbreviation, ns.xsd.string(jou))
        
        # city, country, institution and publisher
        city = ref_data.get("city")
        country = ref_data.get("country")
        institu = ref_data.get("institution")
        if institu is not None:
            orga_IRI = ns.orga.IRI(institu, None, city, country, None)
            triples.append(ref_IRI, ns.dcterms.publisher, orga_IRI)        
        publisher = ref_data.get("publisher")
        if publisher is not None:
            orga_IRI = ns.orga.IRI(publisher, None, city, country, None)
            triples.append(ref_IRI, ns.dcterms.publisher, orga_IRI)

        # issn13 and entity titles        
        issn13 = ref_data.get("issn-13")
        if issn13 is not None: 
            triples.append(ref_IRI, ns.cello.issn13, ns.xsd.string(issn13))
        book_title = ref_data.get("book-title")
        if book_title is not None: 
            triples.append(ref_IRI, ns.cello.bookTitle, ns.xsd.string(book_title))
        doc_title = ref_data.get("document-title")
        if doc_title is not None: 
            triples.append(ref_IRI, ns.cello.documentTitle, ns.xsd.string(doc_title))
        doc_serie_title = ref_data.get("document-serie-title")
        if doc_serie_title is not None: 
            triples.append(ref_IRI, ns.cello.documentSerieTitle, ns.xsd.string(doc_serie_title))
        conf_title = ref_data.get("conference-title")
        if conf_title is not None: 
            triples.append(ref_IRI, ns.cello.conferenceTitle, ns.xsd.string(conf_title))

        # editors (optional)
        for p in ref_data.get("editor-list") or []:
            p_name = p["name"]
            for name in p_name.split(" and "):
                p_BN = self.get_blank_node()
                triples.append(ref_IRI, ns.cello.editor, p_BN)
                triples.append(p_BN, ns.rdf.type, ns.schema.Person)
                triples.append(p_BN, ns.cello.name, ns.xsd.string(name))

        return("".join(triples.lines))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cl(self, ac, cl_obj):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # print(cl_obj)
        triples = TripleList()
        cl_IRI = ns.cvcl.IRI(ac)
        #triples.append(cl_IRI, ns.rdf.type, ns.cello.CellLine) # set below, see field 'CA'
        triples.append(cl_IRI, ns.rdfs.seeAlso, f"<https://www.cellosaurus.org/{ac}>")
        cl_data = cl_obj["cell-line"]

        # fields: AC, AS, ACAS
        for ac_obj in cl_data["accession-list"]:
            some_ac = ns.xsd.string(ac_obj["value"])
            triples.append(cl_IRI, ns.cello.accession, some_ac)
            pred = ns.cello.primaryAccession if ac_obj["type"] == "primary" else ns.cello.secondaryAccession        
            triples.append(cl_IRI, pred, some_ac)

        # fields: ID, SY, IDSY
        for name_obj in cl_data["name-list"]:
            name = ns.xsd.string(name_obj["value"])
            triples.append(cl_IRI, ns.cello.name, name)
            pred = ns.cello.recommendedName if name_obj["type"] == "identifier" else ns.cello.alternativeName
            triples.append(cl_IRI, pred, name)
        
        # fields: CC, registration
        for reg_obj in cl_data.get("registration-list") or []:
            
            name = ns.xsd.string(reg_obj["registration-number"])
            triples.append(cl_IRI, ns.cello.name, name)
            triples.append(cl_IRI, ns.cello.registeredName, name)
            
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.isRegistered, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.RegistrationRecord)      
            triples.append(annot_BN, ns.cello.registeredName, name)
            org_name = reg_obj["registry"]
            org_IRI = ns.orga.IRI(org_name, "", "", "", "")
            triples.append(annot_BN, ns.cello.inRegister, org_IRI)
 
        # fields: CC, misspelling
        for msp_obj in cl_data.get("misspelling-list") or []:
            
            name = ns.xsd.string(msp_obj["misspelling-name"])
            triples.append(cl_IRI, ns.cello.name, name)
            triples.append(cl_IRI, ns.cello.misspellingName, name)

            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.misspellingComment, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.MisspellingComment)
            triples.append(annot_BN, ns.cello.misspellingName, name)
            note = msp_obj.get("misspelling-note")
            if note is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(note))
            for ref in msp_obj.get("reference-list") or []:
                triples.append(annot_BN, ns.cello.appearsIn, self.get_pub_IRI(ref))
            for xref in msp_obj.get("xref-list") or []:             
                triples.append(annot_BN, ns.cello.appearsIn, self.get_xref_IRI(xref))

        # fields: DR
        for xref in cl_data.get("xref-list") or []:
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(cl_IRI, ns.cello.xref, xref_IRI)
            if self.get_xref_db(xref)=="Wikidata":
                # we use owl:sameAs because our cell lines and their equivalent in wikidata are instances (as opposed as classes)
                triples.append(cl_IRI, ns.owl.sameAs, ns.wd.IRI(xref["accession"])) 
            if self.get_xref_discontinued(xref):
                # also used for "CC   Discontinued: " lines       
                triples.extend(self.get_ttl_for_cc_discontinued(cl_IRI, xref["database"], xref["accession"], xref_IRI)) 
                
        # fields: RX
        for rx in cl_data.get("reference-list") or []:
            triples.append(cl_IRI, ns.cello.reference, self.get_pub_IRI(rx))
    
        # fields: WW
        for ww in cl_data.get("web-page-list") or []:
            ww_iri = "".join(["<", ww, ">"])
            triples.append(cl_IRI, ns.rdfs.seeAlso, ww_iri)
        
        # fields: SX
        sx = cl_data.get("sex")
        if sx is not None:
            #triples.append(cl_IRI, ns.cello.fromIndividualWithSex, ns.xsd.string(sx))
            triples.append(cl_IRI, ns.cello.fromIndividualWithSex, get_sex_IRI(sx))

        # fields: AG
        ag = cl_data.get("age")
        if ag is not None:
            triples.append(cl_IRI, ns.cello.fromIndividualAtAge, ns.xsd.string(ag))

        # fields: OI
        for oi in cl_data.get("same-origin-as") or []:
            oi_iri = ns.cvcl.IRI(oi["accession"])
            triples.append(cl_IRI, ns.cello.fromSameIndividualAs, oi_iri)

        # fields: HI
        for hi in cl_data.get("derived-from") or []:
            hi_iri = ns.cvcl.IRI(hi["accession"])
            triples.append(cl_IRI, ns.cello.parentCellLine, hi_iri)

        # fields: CH
        for ch in cl_data.get("child-list") or []:
            ch_iri = ns.cvcl.IRI(ch["accession"]["value"])
            triples.append(cl_IRI, ns.cello.childCellLine, ch_iri)

        # fields: CA
        ca = cl_data["category"] # we expect one value for each cell line
        if ca is not None:
            triples.append(cl_IRI, ns.rdf.type, self.get_cl_category_class_IRI(ca))
        else:
            triples.append(cl_IRI, ns.rdf.type, ns.wd.CellLine)
            

        # fields DT, dtc, dtu, dtv
        triples.append(cl_IRI, ns.cello.created, ns.xsd.date(cl_data["created"]))
        triples.append(cl_IRI, ns.cello.modified, ns.xsd.date(cl_data["last-updated"]))
        triples.append(cl_IRI, ns.cello.hasVersion, ns.xsd.string(cl_data["entry-version"]))

        # fields: CC, genome-ancestry
        annot = cl_data.get("genome-ancestry")
        if annot is not None:
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.genomeAncestry, annot_BN)
            triples.append(annot_BN, ns.rdf.type ,ns.cello.GenomeAncestry)
            # ref can be publi or organization, but only publi in real data
            src = annot.get("source")
            if src is not None: 
                triples.extend(self.get_ttl_for_source(annot_BN, src))
            else:
                log_it("ERROR", f"reference of genome-ancestry source is null: {ac}")
            for pop in annot["population-list"]:
                pop_percent_BN = self.get_blank_node()
                triples.append(annot_BN, ns.cello.component, pop_percent_BN)
                triples.append(pop_percent_BN, ns.rdf.type, ns.cello.PopulationPercentage)
                pop_name = ns.xsd.string(pop["population-name"])
                pop_BN = self.get_blank_node()
                triples.append(pop_BN, ns.rdf.type, ns.cello.Population)
                triples.append(pop_BN, ns.cello.populationName, pop_name)
                triples.append(pop_percent_BN, ns.cello.population, pop_BN)
                percent = ns.xsd.float(pop["population-percentage"])
                triples.append(pop_percent_BN, ns.cello.percentage, percent)

        # fields: CC hla
        for annot in cl_data.get("hla-typing-list") or []:
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hlaTyping, annot_BN)
            triples.append(annot_BN, ns.rdf.type ,ns.cello.HLATyping)
            src = annot.get("source")
            if src is not None: 
                triples.extend(self.get_ttl_for_source(annot_BN, src))
            # for gall in annot["hla-gene-alleles-list"]:
            #     gene_label = gall["gene"]
            #     gene_clazz = self.get_hla_gene_class_IRI(gene_label)
            #     for allele in gall["alleles"].split(","):
            #         allele_BN = self.get_blank_node()
            #         triples.append(annot_BN, ns.cello.includesObservation, allele_BN)
            #         allele_id = "*".join([gene_label, allele])
            #         triples.append(allele_BN, ns.rdf.type, ns.cello.HLA_Allele)
            #         triples.append(allele_BN, ns.cello.alleleIdentifier, ns.xsd.string(allele_id))
            #         # alternative 1)
            #         gene_BN = self.get_blank_node()
            #         triples.append(gene_BN, ns.rdf.type, gene_clazz)
            #         triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(gene_label))
            #         triples.append(allele_BN, ns.cello.isAlleleOf, gene_BN)
            #         # alternative 2) - we loose domain / range in widoco, we break instance / class separation
            #         # triples.append(allele_BN, ns.GENO._0000408_is_allele_of, gene_clazz)
            for gall in annot["hla-gene-alleles-list"]:
                gene_label = gall["gene"]
                gene_clazz = self.get_hla_gene_class_IRI(gene_label)
                for allele in gall["alleles"].split(","):
                    obs_BN = self.get_blank_node()
                    triples.append(annot_BN, ns.cello.includesObservation, obs_BN)                    
                    triples.append(obs_BN, ns.rdf.type, ns.schema.Observation)
                    gene_BN = self.get_blank_node()
                    triples.append(obs_BN, ns.cello.hasTarget, gene_BN)
                    triples.append(gene_BN, ns.rdf.type, gene_clazz)
                    triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(gene_label))
                    allele_BN = self.get_blank_node()
                    allele_id = "*".join([gene_label, allele])
                    triples.append(obs_BN, ns.cello.detectedAllele, allele_BN)
                    triples.append(allele_BN, ns.rdf.type, ns.cello.HLA_Allele)
                    triples.append(allele_BN, ns.cello.alleleIdentifier, ns.xsd.string(allele_id))

        # fields: CC str, WARNING: str-list is not a list !!!
        annot = cl_data.get("str-list")
        if annot is not None:
            triples.extend(self.get_ttl_for_short_tandem_repeat(cl_IRI, annot))

        # fields: di
        for annot in cl_data.get("disease-list") or []:
            triples.extend(self.get_ttl_for_disease(cl_IRI, annot))

        # fields: ox
        for annot in cl_data.get("species-list") or []:
            triples.extend(self.get_ttl_for_species(cl_IRI, annot))

        # field: breed
        breed_annot = cl_data.get("breed")
        if breed_annot is not None:
            triples.extend(self.get_ttl_for_breed(cl_IRI, breed_annot))

        # fields: CC sequence-variation
        for annot in cl_data.get("sequence-variation-list") or []:
            triples.extend(self.get_ttl_for_sequence_variation(cl_IRI, annot))

        # fields: derived-from-site
        for annot in cl_data.get("derived-from-site-list") or []:
            triples.extend(self.get_ttl_for_derived_from_site(cl_IRI, annot))

        ct_annot = cl_data.get("cell-type")
        if ct_annot is not None:
            triples.extend(self.get_ttl_for_cell_type(cl_IRI, ct_annot))

        # fields: CC doubling-time
        for annot in cl_data.get("doubling-time-list") or []:
            triples.extend(self.get_ttl_for_doubling_time(cl_IRI, annot))

        # fields: CC transformant
        for annot in cl_data.get("transformant-list") or []:
            triples.extend(self.get_ttl_for_transformant(cl_IRI, annot))

        # fields: CC msi
        for annot in cl_data.get("microsatellite-instability-list") or []:
            triples.extend(self.get_ttl_for_msi(cl_IRI, annot))

        # fields: CC mab-isotype
        for annot in cl_data.get("monoclonal-antibody-isotype-list") or []:
            triples.extend(self.get_ttl_for_mab_isotype(cl_IRI, annot))

        # fields: CC mab-target
        for annot in cl_data.get("monoclonal-antibody-target-list") or []:
            triples.extend(self.get_ttl_for_mab_target(cl_IRI, annot))

        # fields: CC resistance
        for annot in cl_data.get("resistance-list") or []:
            triples.extend(self.get_ttl_for_resistance(cl_IRI, annot))

        # fields: CC knockout
        for annot in cl_data.get("knockout-cell-list") or []:
            triples.extend(self.get_ttl_for_cc_knockout_cell(cl_IRI, annot))

        # fields: CC integration
        for annot in cl_data.get("genetic-integration-list") or []:
            triples.extend(self.get_ttl_for_cc_genetic_integration(cl_IRI, annot))

        # fields: CC from, ...
        for cc in cl_data.get("comment-list") or []:
            categ = cc["category"]
            if categ == "From": 
                triples.extend(self.get_ttl_for_cc_from(cl_IRI, cc))
            elif categ == "Part of":
                triples.extend(self.get_ttl_for_cc_part_of(cl_IRI, cc))            
            elif categ == "Group":
                triples.extend(self.get_ttl_for_cc_in_group(cl_IRI, cc))
#            elif categ == "Breed/subspecies":
#                triples.extend(self.get_ttl_for_cc_breed(cl_IRI, cc))
            elif categ == "Anecdotal":
                triples.extend(self.get_ttl_for_cc_anecdotal(cl_IRI, cc))
            elif categ == "Biotechnology":
                triples.extend(self.get_ttl_for_cc_biotechnology(cl_IRI, cc))
            elif categ == "Characteristics":
                triples.extend(self.get_ttl_for_cc_characteristics(cl_IRI, cc))
            elif categ == "Caution":
                triples.extend(self.get_ttl_for_cc_caution(cl_IRI, cc))
            elif categ == "Donor information":
                triples.extend(self.get_ttl_for_cc_donor_info(cl_IRI, cc))
            elif categ == "Discontinued":
                provider, product_id = cc["value"].split("; ")
                triples.extend(self.get_ttl_for_cc_discontinued(cl_IRI, provider, product_id)) # also used in DR lines
            elif categ == "Karyotypic information":
                triples.extend(self.get_ttl_for_cc_karyotypic_info(cl_IRI, cc))
            elif categ == "Miscellaneous":
                triples.extend(self.get_ttl_for_cc_miscellaneous_info(cl_IRI, cc))
            elif categ == "Senescence":
                triples.extend(self.get_ttl_for_cc_senescence_info(cl_IRI, cc))
            elif categ == "Virology":
                triples.extend(self.get_ttl_for_cc_virology_info(cl_IRI, cc))
            elif categ == "Omics":
                triples.extend(self.get_ttl_for_cc_omics_info(cl_IRI, cc))
            elif categ == "Population":
                triples.extend(self.get_ttl_for_cc_population_info(cl_IRI, cc))

        return("".join(triples.lines))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def extract_hgvs_list(self, label):
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
    def get_ttl_for_sequence_variation(self, cl_IRI, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        try:
            triples = TripleList()

            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.sequenceVariationComment, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.SequenceVariationComment)
            mut_type = annot.get("mutation-type")
            variationStatus = "Natural"
            if mut_type is not None and "edited" in mut_type: variationStatus = "Edited"
            if mut_type is not None and "corrected" in mut_type: variationStatus = "Corrected"
            triples.append(annot_BN, ns.cello.variationStatus, ns.xsd.string(variationStatus))
            var_sources = annot.get("source-list") or []
            triples.extend(self.get_ttl_for_sources(annot_BN, var_sources))

            seqvar_BN = self.get_blank_node()
            triples.append(annot_BN, ns.cello.sequenceVariation, seqvar_BN)
            var_type = annot.get("variation-type")
            sv_clazz = self.get_sequence_variation_class(var_type, mut_type)
            triples.append(seqvar_BN, ns.rdf.type, sv_clazz)
            none_reported = (mut_type == "None_reported")
            triples.append(seqvar_BN, ns.cello.noneReported, ns.xsd.boolean(none_reported))
            note = annot.get("variation-note")
            if note is not None: triples.append(seqvar_BN, ns.rdfs.comment, ns.xsd.string(note))        
            zygo = annot.get("zygosity-type")
            if zygo is not None: triples.append(seqvar_BN, ns.cello.zygosity, ns.xsd.string(zygo))
            label = annot.get("mutation-description")
            if none_reported: label = "None_reported"
            if var_type=="Gene deletion" and label is None: label = var_type
            elif var_type=="Gene amplification" and label is None: label = mut_type # Duplication, Triplication, ...
            triples.append(seqvar_BN, ns.rdfs.label, ns.xsd.string(label)) # TODO? remove first hgvs from label ?        
            if var_type=="Mutation" and mut_type.startswith("Simple"): 
                hgvs_list = self.extract_hgvs_list(label)
                if len(hgvs_list) not in [1,2]: log_it("WARNING", f"invalid hgvs in: {label}")
                for hgvs in hgvs_list: triples.append(seqvar_BN, ns.cello.hgvs, ns.xsd.string(hgvs))
            for xref in annot.get("xref-list"):
                db = xref["database"]
                if db in ["HGNC", "MGI", "RGD", "VGNC", "UniProtKB"]:
                    gene_BN = self.get_blank_node()
                    triples.append(seqvar_BN, ns.cello.gene, gene_BN)
                    triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
                    gene_label =  self.get_xref_label(xref)
                    if gene_label is not None and len(gene_label) > 0:
                        triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(gene_label))
                    triples.append(gene_BN, ns.cello.xref, self.get_xref_IRI(xref)) # gene(s) related to the variation
                elif db in ["ClinVar", "dbSNP"]:
                    triples.append(seqvar_BN, ns.cello.xref, self.get_xref_IRI(xref)) # reference of the variant description

            #print(f"varmut-desc | {var_type} | {mut_type} | {label}")
            return triples

        except DataError as e:
            (typ,details) = e.args        
            cl_ac = cl_IRI.split(":")[1]
            log_it("ERROR", f"{typ} - {details} : {cl_ac}")
            return TripleList()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_sequence_variation_class(self, var_type, mut_type):
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

        if var_type == "Mutation":
            if mut_type.startswith("Simple"): return ns.NCIt.GeneMutation
            if mut_type.startswith("Repeat"): return ns.cello.RepeatExpansion
            if mut_type.startswith("Unexplicit"): return ns.NCIt.GeneMutation
            if mut_type == "None_reported": return ns.NCIt.GeneMutation
        elif var_type == "Gene fusion": return ns.NCIt.GeneFusion
        elif var_type == "Gene deletion": return ns.NCIt.GeneDeletion
        elif var_type == "Gene amplification":
            if mut_type == "Triplication": return ns.cello.GeneTriplication
            if mut_type == "Duplication": return ns.cello.GeneDuplication
            if mut_type == "Quadruplication": return ns.cello.GeneQuadruplication
            if mut_type == "Extensive": return ns.cello.GeneExtensiveAmplification
            if mut_type == "None_reported": return ns.NCIt.GeneAmplification # not in data but we never know    
        raise DataError("SequenceVariation", f"Unexpected variation-type / mutation-type combination: {var_type} / {mut_type}")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_from(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        value = cc["value"]
        elems = value.split("; ")
        contact=elems.pop(0) if len(elems) == 4 else ""
        if len(elems) != 3: 
            cl_ac = cl_IRI.split(":")[1]
            log_it("ERROR", f"expected 3-4 tokens in CC From comment '{value}' : {cl_ac}")
            return triples
        orga_IRI = ns.orga.IRI(elems[0], "", elems[1], elems[2], contact)
        triples.append(cl_IRI, ns.cello._from, orga_IRI)
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_part_of(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        label = cc["value"]
        triples.append(cl_IRI, ns.cello.partOf, ns.xsd.string(label))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_in_group(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        label = cc["value"]
        triples.append(cl_IRI, ns.cello.group, ns.xsd.string(label))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_breed(self, cl_IRI, breed):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.fromIndividualBelongingToBreed, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Breed)
        if type(breed) == str:
            label = breed
            triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(label))
        else:
            label = breed["value"]
            triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(label))
            for xref in breed.get("xref-list") or []:
                triples.append(annot_BN, ns.cello.xref, self.get_xref_IRI(xref))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_characteristics(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.characteristicsComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.CharacteristicsComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_caution(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.cautionComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.CautionComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_biotechnology(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.biotechnologyComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.BiotechnologyComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_anecdotal(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.anecdotalComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.AnecdotalComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_donor_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.donorInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.DonorInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))

        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_karyotypic_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.karyotypicInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.KaryotypicInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_miscellaneous_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.miscellaneousInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.MiscellaneousInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_senescence_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.senescenceComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.SenescenceComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_virology_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.virologyComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.VirologyComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_genetic_integration(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        method = cc.get("method")
        note = cc.get("genetic-integration-note")
        xref = cc.get("xref")
        nameonly = cc.get("value")
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.geneticIntegration, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.GeneticIntegration)
        method_BN = self.get_blank_node()
        triples.append(method_BN, ns.rdf.type, self.get_gem_class_IRI(method))
        triples.append(method_BN, ns.rdfs.label, ns.xsd.string(self.get_gem_clean_label(method)))
        triples.append(inst_BN, ns.cello.genomeModificationMethod, method_BN)
        if note is not None: 
            triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(note))
        gene_BN = self.get_blank_node()
        triples.append(inst_BN, ns.cello.gene, gene_BN)
        triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
        if nameonly is not None:
            triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(nameonly))
        else:
            triples.append(gene_BN, ns.cello.xref, self.get_xref_IRI(xref))
            gene_name =  self.get_xref_label(xref)
            if gene_name is not None and len(gene_name)>0:
                triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(gene_name))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_knockout_cell(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        method = cc.get("method")
        comment = cc.get("knockout-cell-note") # optional
        xref = cc.get("xref")
        if method is None or xref is None:
            log_it("WARNING", f"missing method or gene xref in knockout comment in {cl_IRI}")
        else:
            inst_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.geneKnockout, inst_BN)
            triples.append(inst_BN, ns.rdf.type, ns.cello.GeneKnockout)
            method_BN = self.get_blank_node()
            triples.append(method_BN, ns.rdf.type, self.get_gem_class_IRI(method))
            triples.append(method_BN, ns.rdfs.label, ns.xsd.string(self.get_gem_clean_label(method)))
            triples.append(inst_BN, ns.cello.genomeModificationMethod, method_BN)
            gene_BN = self.get_blank_node()
            triples.append(inst_BN, ns.cello.gene, gene_BN)
            triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
            triples.append(gene_BN, ns.cello.xref, self.get_xref_IRI(xref))
            gene_name =  self.get_xref_label(xref)
            if gene_name is not None and len(gene_name)>0:
                triples.append(gene_BN, ns.rdfs.label, ns.xsd.string(gene_name))
            if comment is not None: 
                triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_omics_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.omicsComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.OmicsComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_population_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        nameOrNames = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.fromIndividualBelongingToPopulation, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.Population)
        triples.append(inst_BN, ns.cello.populationName, ns.xsd.string(nameOrNames))
        return triples



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_derived_from_site(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        site_BN = self.get_blank_node()
        note = annot.get("site-note")
        site = annot["site"]
        site_type = site["site-type"]
        label = site["value"]
        triples.append(cl_IRI, ns.cello.derivedFromSite, site_BN)
        triples.append(site_BN, ns.rdf.type, ns.CARO.AnatomicalEntity)
        triples.append(site_BN, ns.cello.siteType, ns.xsd.string(site_type))
        triples.append(site_BN, ns.rdfs.label, ns.xsd.string(label))
        if note is not None:
            triples.append(site_BN, ns.rdfs.comment, ns.xsd.string(note)) 
        for xref in site.get("xref-list") or []: 
            triples.append(site_BN, ns.cello.xref, self.get_xref_IRI(xref))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cell_type(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        ct_BN = self.get_blank_node()
        if isinstance(annot, str):  # when we have free text only without a xref
            label, cv = (annot, None)
        else:
            label, cv = (annot["value"], annot.get("xref"))
        triples.append(cl_IRI, ns.cello.cellType, ct_BN)
        triples.append(ct_BN, ns.rdf.type, ns.CL.CellType)
        triples.append(ct_BN, ns.rdfs.label, ns.xsd.string(label))    
        if cv is not None: triples.append(ct_BN, ns.cello.xref, self.get_xref_IRI(cv))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cc_discontinued(self, cl_IRI, provider, product_id, xref_IRI=None):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.discontinuationRecord, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.DiscontinuationRecord)
        triples.append(annot_BN, ns.cello.provider, ns.xsd.string(provider))
        triples.append(annot_BN, ns.cello.productId, ns.xsd.string(product_id))
        if xref_IRI is not None:
            triples.append(annot_BN, ns.cello.xref, xref_IRI)
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_source(self, parentNode, src):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        src_BN = self.get_blank_node()
        triples.append(parentNode, ns.cello.source, src_BN)
        triples.append(src_BN, ns.rdf.type, ns.cello.Source)
        if type(src) == dict:
            lbl = src.get("value")
            if lbl is not None:
                triples.append(src_BN, ns.rdfs.label, ns.xsd.string(lbl))
            xref = src.get("xref")
            if xref is not None:
                triples.append(src_BN, ns.cello.xref, self.get_xref_IRI(xref))
            ref =src.get("reference")
            if ref is not None: 
                triples.append(src_BN, ns.cello.reference, self.get_pub_IRI(ref))
        elif type(src) == str:
            #print("string/src", src)
            if src == "Direct_author_submission" or src.startswith("from inference of"):
                triples.append(src_BN, ns.rdfs.label, ns.xsd.string(src))
            else:
                # build an org object from label 'src' and get 
                # optional params from known orgs 
                # BEFORE we build the IRI and store the params 
                org = Organization(src, "", "", "", "")
                org = self.get_org_merged_with_known_org(org)
                orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store=True)
                triples.append(src_BN, ns.cello.organization, orga_IRI)
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_key_for_source(self, src):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if type(src) == dict:
            xref = src.get("xref")
            if xref is not None: return "=".join([xref["database"], xref["accession"]])
            ref =src.get("reference")
            if ref is not None: return ref.get("resource-internal-ref")
            lbl = src.get("value")
            if lbl is not None: return lbl
        elif type(src) == str:
            return src
        else:
            print("ERROR, don't know how to build ksy for source", src) 
            return str(src)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_sources(self, parentNode, sources):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        for src in sources or []:
            triples.extend(self.get_ttl_for_source(parentNode, src))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_doubling_time(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        duration = annot["doubling-time-value"]
        comment = annot.get("doubling-time-note")
        sources = annot.get("source-list") or [] 
        triples.append(cl_IRI, ns.cello.doublingTimeComment, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.DoublingTimeComment)
        triples.append(annot_BN, ns.cello.duration, ns.xsd.string(duration))
        if comment is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(annot_BN, sources))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_msi(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        value = annot["msi-value"]
        comment = annot.get("microsatellite-instability-note")
        sources = annot.get("source-list") or [] 
        triples.append(cl_IRI, ns.cello.microsatelliteInstability, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.MicrosatelliteInstability)
        triples.append(annot_BN, ns.cello.msiValue, ns.xsd.string(value))
        if comment is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_ttl_for_sources(annot_BN, sources))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_mab_isotype(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        heavy = annot["heavy-chain"]
        light = annot.get("light-chain")
        sources = annot.get("source-list") or []
        triples.append(cl_IRI, ns.cello.mabIsotype, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.MabIsotype)
        triples.append(annot_BN, ns.cello.antibodyHeavyChain, ns.xsd.string(heavy))
        if light is not None: triples.append(annot_BN, ns.cello.antibodyLightChain, ns.xsd.string(light))
        triples.extend(self.get_ttl_for_sources(annot_BN, sources))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_mab_target(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        clazz = ns.CHEBI.ChemicalEntity # default when we have no xref

        # we might get a simple string in annot (the name of the antigen)
        if type(annot) == str:
            triples.append(cl_IRI, ns.cello.mabTarget, annot_BN)
            triples.append(annot_BN, ns.rdf.type, clazz)
            triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(annot))
            return triples

        # or more often we get a dict object
        comment = annot.get("monoclonal-antibody-target-note")
        # we might get just a comment and a name
        name = annot.get("value")
        # or the name is in the xref
        xref = annot.get("xref")
        if xref is not None:
            name = self.get_xref_label(xref)
            xref_IRI = self.get_xref_IRI(xref)
            db = self.get_xref_db(xref)
            if db in [ "UniProtKB", "FPbase" ]: 
                clazz = ns.CHEBI.Protein
            elif db == "ChEBI":
                clazz = ns.CHEBI.ChemicalEntity
            else:
                raise DataError("Monoclonal antibody target", "Unexpected xref database: " + db)

        triples.append(cl_IRI, ns.cello.mabTarget, annot_BN)
        triples.append(annot_BN, ns.rdf.type, clazz)
        triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(name))
        if comment is not None:
            triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        if xref is not None:
            triples.append(annot_BN, ns.cello.xref, xref_IRI)

        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_resistance(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.resistance, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.CHEBI.ChemicalEntity)
        # we might get a simple string in annot (the name of the chemical)
        if type(annot) == str:
            triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(annot))
        # or more often we get a dict object
        else:
            xref = annot.get("xref")
            name = self.get_xref_label(xref)
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(annot_BN, ns.cello.xref, xref_IRI)
            triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(name))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_transformant(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.transformant, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.CHEBI.ChemicalEntity)

        # we might get a simple string in annot (the name of the chemical)
        if type(cc) == str:
            triples.append(inst_BN, ns.rdfs.label, ns.xsd.string(cc))
        # or more often we get a dict object
        else:
            comment = cc.get("transformant-note") # optional
            term = cc.get("xref") # optional too
            inst_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.transformant, inst_BN)
            triples.append(inst_BN, ns.rdf.type, ns.CHEBI.ChemicalEntity)
            if term is not None:
                triples.append(inst_BN, ns.cello.xref, self.get_xref_IRI(term))
                label = self.get_xref_label(term)
                triples.append(inst_BN, ns.rdfs.label, ns.xsd.string(label))
            else:
                label = cc["value"] 
                triples.append(inst_BN, ns.rdfs.label, ns.xsd.string(label))
            if comment is not None: 
                triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_str_observation_list(self, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        obs_dict = dict()

        # all_src_key_set = set()
        # for src in annot["source-list"]:
        #     all_src_key_set.add(self.get_key_for_source(src))

        mrk_src_key_dict = dict()

        for marker in annot["marker-list"]:
            marker_id = marker["id"]
            mrk_src_key_dict[marker_id] = set()
            for marker_data in marker["marker-data-list"]:
                dat_src_key_set = set()
                for src in marker_data.get("source-list") or []:
                    dat_src_key_set.add(self.get_key_for_source(src))
                mrk_src_key_dict[marker_id].update(dat_src_key_set)
                alleles = list()
                if marker_id == "Amelogenin":
                    #print(">>>marker_data", marker_data)
                    alleles.append("X") if "X" in marker_data["marker-alleles"] else alleles.append("Not_X") # make undetected AMELX explicit
                    alleles.append("Y") if "Y" in marker_data["marker-alleles"] else alleles.append("Not_Y") # make undetected AMELY explicit
                else:
                    #print(">>>marker", marker)
                    for allele in marker_data["marker-alleles"].split(","):
                        if allele == "Not_detected": continue # we ignore other undetected markers (non-Amelogenin)
                        alleles.append(allele)
                for allele in alleles:
                    key = "".join([marker_id,allele])
                    if key not in obs_dict: 
                        obs_dict[key] = {"marker_id": marker_id, "allele": allele, "conflict": False, "srckey_set": set(), "obs_source_list": list()}
                    rec = obs_dict[key]
                    #print(">>>rec", rec)
                    rec["srckey_set"].update(dat_src_key_set)
                    rec["obs_source_list"].extend(marker_data.get("source-list") or [])
        for obs in obs_dict.values():
            if obs["srckey_set"] != set() and obs["srckey_set"] != mrk_src_key_dict[obs["marker_id"]]:
                obs["conflict"] = True
        return list(obs_dict.values())


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_str_marker_instance(self, marker_BN, id):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        triples.append(marker_BN, ns.rdf.type, ns.cello.Marker)
        triples.append(marker_BN, ns.cello.markerId, ns.xsd.string(id))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_str_allele_instance(self, allele_BN, repeat_number):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        triples.append(allele_BN, ns.rdf.type, ns.cello.STR_Allele)
        triples.append(allele_BN, ns.cello.repeatNumber, ns.xsd.string(repeat_number))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_short_tandem_repeat(self, cl_IRI, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()

        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.shortTandemRepeatProfile, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.ShortTandemRepeatProfile)
        sources = annot["source-list"]
        triples.extend(self.get_ttl_for_sources(annot_BN, sources))

        for obs in self.get_str_observation_list(annot):
            #print(">>>obs", cl_IRI, obs)
            marker_id = obs["marker_id"]
            allele = obs["allele"]
            sources = obs["obs_source_list"]
            conflict = obs["conflict"]
            obs_BN = self.get_blank_node()
            triples.append(annot_BN, ns.cello.includesObservation, obs_BN)
            triples.append(obs_BN, ns.rdf.type, ns.schema.Observation)
            triples.append(obs_BN, ns.rdfs.label, ns.xsd.string(f"Observation of {marker_id}"))
            marker_BN = self.get_blank_node()
            if marker_id == "Amelogenin":
                gene_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.hasTarget, gene_BN)
                chr = "X" if allele in  ["X", "Not_X"] else "Y" 
                triples.extend(self.get_ttl_for_amelogenin_gene_instance(gene_BN, chr))
                detected = not "Not" in allele
                triples.append(obs_BN, ns.cello.detectedTarget, ns.xsd.boolean(detected))
                triples.append(obs_BN, ns.cello.conflicting, ns.xsd.boolean(conflict))
            else:
                marker_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.hasTarget, marker_BN)
                triples.extend(self.get_ttl_for_str_marker_instance(marker_BN, marker_id))
                allele_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.detectedAllele, allele_BN)
                triples.extend(self.get_ttl_for_str_allele_instance(allele_BN, allele))
                triples.append(obs_BN, ns.cello.conflicting, ns.xsd.boolean(conflict))
            if conflict:
                triples.extend(self.get_ttl_for_sources(obs_BN, sources))
   
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_disease(self, cl_IRI, cvterm):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.fromIndividualWithDisease, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Disease)
        name = self.get_xref_label(cvterm)
        xref_IRI = self.get_xref_IRI(cvterm)
        triples.append(annot_BN, ns.cello.xref, xref_IRI)
        triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(name))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_species(self, cl_IRI, xref):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.fromIndividualBelongingToSpecies, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Species)
        name = self.get_xref_label(xref)
        xref_IRI = self.get_xref_IRI(xref)
        triples.append(annot_BN, ns.cello.xref, xref_IRI)
        triples.append(annot_BN, ns.rdfs.label, ns.xsd.string(name))
        return triples
