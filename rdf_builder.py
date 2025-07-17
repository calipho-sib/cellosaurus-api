import uuid
import unicodedata
from namespace_registry import NamespaceRegistry
from ApiCommon import log_it, split_string, is_valid_url
from organizations import Organization
from terminologies import Term, Terminologies, Terminology
from databases import Database, Databases, get_db_category_IRI
from sexes import Sex, get_sex_IRI
from msi_status import MsiStatus, get_Msi_Status_IRI
from namespace_term import Term as NsTerm
from personname import PersonName

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
    def __init__(self, known_orgs, ns: NamespaceRegistry): 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.ns = ns
        self.known_orgs = known_orgs

        self.protein_words = { 
            "albumin", "allergen", "chain", "collagen", "crystallin", "hemagglutinin", 
            "histone", "mucin", "peptidoglycan", "tubulin", "vitellogenin", "actin",
            "idiotypic",  "discoidin", "fibrin", "gliadin", "neuraminidase", "tuberculin",  # anti-idiotypic
            "interferon", "laminin", "phosphatase", "polymerase", "receptor",
            "CD0", "CD1", "CD2", "CD3", "CD4", "CD5", "CD6", "CD7", "CD8", "CD9", "keratin", 
            "cytokeratin", "proteoglycan"
        }
        # add potential plural forms of protein words
        plurals = set()
        for w in self.protein_words: plurals.add(w + "s") 
        self.protein_words.update(plurals)       

        self.chem_words = { 
            "acetylglucosamine", "arabinogalactan", "ganglioside", "glycan", "glycolipid", 
            "pectin", "polysaccharide", "rhamnogalacturonan", "xylan", "xyloglucan","carbohydrate", 
            "disialoganglioside", "glycosphingolipid", "oligosaccharide",                    # originals: lipo-oligosaccharide
            "lipopolysaccharide", "galactan", "oligosaccharide", "nlc4cer"                   # originals: nLc4Cer                    
                      }
        # add potential plural forms of chem words
        plurals = set()
        for w in self.chem_words: plurals.add(w + "s") 
        self.chem_words.update(plurals)       

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

        self.hla_hgnc_ac = {
            "HLA-DRA": "HGNC:4947",
            "HLA-DRB2": "HGNC:4950",
            "HLA-DRB1": "HGNC:4948",
            "HLA-A": "HGNC:4931",
            "HLA-DPB1": "HGNC:4940",
            "HLA-C": "HGNC:4933",
            "HLA-B": "HGNC:4932",
            "HLA-DQB1": "HGNC:4944",
            "HLA-DRB3": "HGNC:4951",
            "HLA-DRB4": "HGNC:4952",
            "HLA-DRB5": "HGNC:4953",
            "HLA-DQA1": "HGNC:4942",
            "HLA-DPA1": "HGNC:4938",
            "HLA-DRB6": "HGNC:4954",
            "HLA-DRB9": "HGNC:4957",
        }
        
        # genome editing method labels => class
        # labels MUST be those found in cellosaurus data
        self.gem_ni = {
            "Not specified": ns.cello.GenomeModificationMethodNOS,
            "CRISPR/Cas9": ns.cello.CrisprCas9,
            "X-ray": ns.cello.XRay,
            "Gamma radiation": ns.cello.GammaRadiation,
            "Transfection": ns.cello.Transfection,
            "Mutagenesis": ns.cello.Mutagenesis,
            "siRNA knockdown": ns.cello.SiRNAKnockdown,
            "TALEN": ns.cello.TALEN,
            "ZFN": ns.cello.ZFN,
            "Gene trap": ns.cello.GeneTrap,
            "Transduction": ns.cello.Transduction,
            "BAC homologous recombination": ns.cello.BacHomologousRecombination,
            "Cre/loxP": ns.cello.CreLoxp,
            "CRISPR/Cas12a": ns.cello.CrisprCas12a,
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
            "Protein trap": ns.cello.ProteinTrap,
            "Prime editing": ns.cello.PrimeEditing,
            "Promoterless gene targeting": ns.cello.PromoterlessGeneTargeting,
            "Recombinant Adeno-Associated Virus": ns.cello.RecombinantAdenoAssociatedVirus,
            "Recombinase-mediated cassette exchange": ns.cello.RMCE,
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

        # cell line labels => class
        # labels MUST be those found in cellosaurus data
        self.clcat_clazz = {
            "Cancer cell line": ns.cello.CancerCellLine,
            "Conditionally immortalized cell line": ns.cello.ConditionallyImmortalizedCellLine,
            "Embryonic stem cell": ns.cello.EmbryonicStemCell,
            "Factor-dependent cell line": ns.cello.FactorDependentCellLine,
            "Finite cell line": ns.cello.FiniteCellLine,
            "Hybrid cell line": ns.cello.HybridCellLine,
            "Hybridoma": ns.cello.Hybridoma,
            "Induced pluripotent stem cell": ns.cello.InducedPluripotentStemCell,
            "Somatic stem cell": ns.cello.SomaticStemCell,
            "Spontaneously immortalized cell line": ns.cello.SpontaneouslyImmortalizedCellLine,
            "Stromal cell line": ns.cello.StromalCellLine,
            "Telomerase immortalized cell line": ns.cello.TelomeraseImmortalizedCellLine,
            "Transformed cell line": ns.cello.TransformedCellLine,
            "Cell line": ns.cello.CellLine,
            "Undefined cell line type": ns.cello.UndefinedCellLineType 
        }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def looks_like_a_protein(self, raw_str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        str = raw_str.replace("(","").replace(")","").replace(".","").replace("-"," ").replace("/"," ").replace(","," ")
        words = str.split(" ")
        for word in words: 
            if word.lower() in self.protein_words: return True
            if "protein" in word: return True   # protein, glycoprotein, lipoprotein
            if "Ig" in word: return True        # IgA, IgG, etc
            if "MHC" in word: return True
        return False


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def looks_like_a_chemical(self, raw_str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        str = raw_str.replace("(","").replace(")","").replace(".","").replace("-"," ").replace("/"," ").replace(","," ")
        words = str.split(" ")
        for word in words:
            if word.lower() in self.chem_words: return True
            if "LPS" in word: return True
            if "DNA" in word: return True
        if "nucleic acid" in str: return True
        return False


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_blank_node(self):
    # -- - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return "_:BN" + uuid.uuid4().hex


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for item in self.ns.namespaces:
            lines.append(item.getTtlPrefixDeclaration())
        return "\n".join(lines) + "\n"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_sparql_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        for item in self.ns.namespaces:
            lines.append(item.getSparqlPrefixDeclaration())
        return "\n".join(lines) + "\n"





    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_pub_IRI(self, refOrPub):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        dbac = refOrPub.get("resource-internal-ref")    # exists in reference-list items
        if dbac is None: dbac = refOrPub["internal-id"] # exists in publication-list items
        (db,ac) = dbac.split("=")
        return self.ns.pub.IRI(db,ac)


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
    def get_xref_term_IRI(self, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        return xref.get("iri")



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
        return self.ns.xref.IRI(db,ac, props)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_amelogenin_gene_xref_IRI(self, chr):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ac = "HGNC:461" if chr == "X" else "HGNC:462"
        db = "HGNC"
        cat = "Organism-specific databases"
        lbl = "AMEL" + chr
        #url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:{ac}"
        url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{ac}"  # now "HGNC:" is part of the accession (ac)
        dis = ""
        props = f"cat={cat}|lbl={lbl}|dis={dis}|url={url}"
        return self.ns.xref.IRI(db,ac, props)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_hla_gene_xref_IRI(self, our_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ac = self.hla_hgnc_ac.get(our_label)
        if ac is None:
            log_it("ERROR", f"unexpected HLA Gene label '{our_label}'")
            ac = self.ns.cello.HLAGene # default, most generic
        db = "HGNC"
        cat = "Organism-specific databases"
        #url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:{ac}"
        url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{ac}"  # now "HGNC:" is part of the accession (ac)
        dis = ""
        lbl = our_label 
        props = f"cat={cat}|lbl={lbl}|dis={dis}|url={url}"
        return self.ns.xref.IRI(db,ac, props)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_materialized_triples_for_prop(self, parent_node, prop, xsd_label, no_rdfs_label=False):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # Helper function for the materialization of triples entailed by triple in function params
        # Note: the function handles rdfs:label sub props and skos:notation sub props

        # TODO - to be decided / or as an option in another graph...
        # Could be extended to handle dcterms:identifier and dcterms:title sub props or fully 
        # generalized so that all entailed triples related to the usage a prop 
        # having super props be generated.
        # Some mechanism could be used to generate triples instance rdf_type superclass(es) triples
        # The triples could be generated from here of later in the process with a simple SPARQL construct...

        ns = self.ns

        # this dictionary decides which properties are generated according to the prop chosen
        materialization_rule = {
            ns.rdfs.label : { ns.rdfs.label },
            ns.cello.name : { ns.rdfs.label, ns.cello.name },
            ns.skos.prefLabel : { ns.rdfs.label, ns.cello.name, ns.skos.prefLabel },
            ns.skos.altLabel : { ns.rdfs.label, ns.cello.name, ns.skos.altLabel },
            ns.skos.hiddenLabel : { ns.rdfs.label, ns.cello.name, ns.skos.hiddenLabel },
            ns.cello.registeredName : { ns.rdfs.label, ns.cello.name, ns.cello.registeredName },
            ns.cello.recommendedName : { ns.rdfs.label, ns.cello.name, ns.skos.prefLabel, ns.cello.recommendedName },
            ns.cello.alternativeName : { ns.rdfs.label, ns.cello.name, ns.skos.altLabel, ns.cello.alternativeName },
            ns.cello.misspellingName : { ns.rdfs.label, ns.cello.name, ns.skos.hiddenLabel, ns.cello.misspellingName },
            ns.skos.notation : { ns.skos.notation },
            ns.cello.hgvs : { ns.skos.notation, ns.cello.hgvs }
        }

        triples = TripleList()
        for p in materialization_rule[prop]: 
            if no_rdfs_label == True and p == ns.rdfs.label: continue # skip generation of triple with rdfs:label
            triples.append(parent_node, p, xsd_label)
        if len(triples.lines)==0: print(f"ERROR, generated no triples for prop: {prop} and xsd_label: {xsd_label}")
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_amelogenin_gene_instance(self, gene_BN, chr):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
        triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(f"AMEL{chr}")))
        xref_IRI = self.get_amelogenin_gene_xref_IRI(chr)
        triples.append(gene_BN, ns.cello.isIdentifiedByXref, xref_IRI)
        return triples
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_hla_gene_instance(self, gene_BN, label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        triples.append(gene_BN, ns.rdf.type, ns.cello.HLAGene)
        triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(label)))   
        xref_IRI = self.get_hla_gene_xref_IRI(label)
        triples.append(gene_BN, ns.cello.isIdentifiedByXref, xref_IRI)
        return triples
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_local_gem_class(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        localClass = ns.cello.GenomeModificationMethod
        obigemClass = ns.OBI.GeneticTransformation # parent class
        members = list()
        for k in self.gem_ni: members.append(self.gem_ni[k])
        members_str = " ".join(members)
        member_lines = "\n      ".join(split_string(members_str, 90))
        text = f"""

# Define genome modification method class as a list of members (owl:oneOf)

{localClass} a owl:Class ;
    rdfs:label "Genome modification method" ;
    rdfs:subClassOf {obigemClass} ;
    owl:oneOf (
      {member_lines}
    ) .
"""
        return text.split("\n")


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_gem_individual(self, ni_term: NsTerm):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        
        for clazz in ni_term.props.get("rdf:type"):
            triples.append(ni_term.iri, ns.rdf.type, clazz)

        label = ni_term.get_label_str()
        xsd_label = ns.xsd.string(label)
        triples.extend(self.get_materialized_triples_for_prop(ni_term.iri, ns.cello.name, xsd_label))

        comment_set = ni_term.props.get("rdfs:comment")
        if comment_set is not None and len(comment_set)>0:
            xsd_comment = next(iter(comment_set))
            triples.append(ni_term, "rdfs:comment", xsd_comment)

        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(ni_term.iri, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_gem_IRI(self, our_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        ni = self.gem_ni.get(our_label)
        if ni is None:
            log_it("ERROR", f"unexpected genome editing method '{our_label}'")
            return ns.cello.GenomeModificationMethodNOS # default
        return ni


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_cl_category_class_IRI(self, category_label):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        clazz = self.clcat_clazz.get(category_label)
        if clazz is None:
            log_it("ERROR", f"unexpected cell line category '{category_label}'")
            clazz = ns.cello.CellLine # default, most generic
        return clazz


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ref_class_IRI(self, ref_data):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
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
        return self.ns.xref.dbac_dict



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_sex(self, sex: Sex):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        sex_IRI = get_sex_IRI(sex.label, ns)
        # as a named individual of type :Sex
        triples.append(sex_IRI, ns.rdf.type, ns.cello.Sex)
        triples.append(sex_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.extend(self.get_materialized_triples_for_prop(sex_IRI, ns.cello.name, ns.xsd.string(sex.label))) # onto NI
        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(sex_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_msi_status(self, status: MsiStatus):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        status_IRI = get_Msi_Status_IRI(status.label, ns)
        # as a named individual of type MicrosatelliteInstabilityStatus
        triples.append(status_IRI, ns.rdf.type, ns.cello.MicrosatelliteInstabilityStatus)
        triples.append(status_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.extend(self.get_materialized_triples_for_prop(status_IRI, ns.cello.name, ns.xsd.string(status.label))) # onto NI
        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(status_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)
    


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cello_terminology_individual(self, termi):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # Note: some databases are also declared as terminologies
        triples = TripleList()
        termi_IRI = self.get_terminology_or_database_IRI(termi.abbrev)
        triples.append(termi_IRI, ns.rdf.type, ns.cello.CelloConceptScheme)
        triples.append(termi_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.extend(self.get_materialized_triples_for_prop(termi_IRI, ns.cello.alternativeName, ns.xsd.string(termi.name), no_rdfs_label=True)) # onto NI (long name is the alternative one)        
        triples.extend(self.get_materialized_triples_for_prop(termi_IRI, ns.cello.recommendedName, ns.xsd.string(termi.abbrev))) # onto NI (short name is the recommended one)        
        triples.append(termi_IRI, ns.cello.version, ns.xsd.string(termi.version))
        triples.append(termi_IRI, ns.rdfs.seeAlso, "<" + termi.url + ">")
        url = ns.cello.url
        if url.endswith("#"): url = url[:-1]
        triples.append(termi_IRI, ns.rdfs.isDefinedBy, "<" + url + ">")
        return "".join(triples.lines)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cello_database_individual(self, db: Database):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        # Note1 : some databases are also declared as terminologies
        # Note2 : in UniProt, a database is an instance of class up:Database
        #       : in cello, we define a database as an instance of cello:Database subclass
        #       : and as a NamedIndividual
        triples = TripleList()
        db_IRI = self.get_terminology_or_database_IRI(db.rdf_id)
        triples.append(db_IRI, ns.rdf.type, get_db_category_IRI(db.cat, ns))
        triples.append(db_IRI, ns.rdf.type, ns.owl.NamedIndividual)
        triples.extend(self.get_materialized_triples_for_prop(db_IRI, ns.cello.alternativeName, ns.xsd.string(db.name), no_rdfs_label=True)) # db NI (long name is the alternative one)        
        triples.extend(self.get_materialized_triples_for_prop(db_IRI, ns.cello.recommendedName, ns.xsd.string(db.abbrev))) # db NI (short name is the recommended one)        
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
        ns = self.ns
        triples = TripleList()
        # term IRI is built like xref IRI
        # note that sometimes an IRI is both a :Xref and a:Concept 
        db = term.scheme
        ac = term.id
        xr_IRI = ns.xref.IRI(db, ac, None, store=False)
        triples.append(xr_IRI, ns.rdf.type, ns.skos.Concept)
        triples.append(xr_IRI, ns.skos.inScheme, self.get_terminology_or_database_IRI(term.scheme))
        no_accent_label = self.remove_accents(term.prefLabel)
        triples.extend(self.get_materialized_triples_for_prop(xr_IRI, ns.skos.prefLabel, ns.xsd.string(no_accent_label)))        
        triples.extend(self.get_materialized_triples_for_prop(xr_IRI, ns.skos.notation, ns.xsd.string(term.id)))
        for alt in term.altLabelList:
            no_accent_label = self.remove_accents(alt)
            triples.extend(self.get_materialized_triples_for_prop(xr_IRI, ns.skos.altLabel, ns.xsd.string(no_accent_label)))
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
        ns = self.ns
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
        triples.append(xr_IRI, ns.cello.internalId, ns.xsd.string(xref_key))
        triples.append(xr_IRI, ns.cello.accession, ns.xsd.string(ac))
        triples.append(xr_IRI, ns.cello.database,  self.get_terminology_or_database_IRI(ns.xref.cleanDb(db))) 

        # we usually expect one item in the set associated to each key of prop_dict
        # if we get more than one item, we take the first as the prop value
        if "lbl" in prop_dict:
            for value in prop_dict["lbl"]: break
            triples.extend(self.get_materialized_triples_for_prop(xr_IRI, ns.cello.name, ns.xsd.string(value)))       
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
        return self.ns.orga.nccc_dict

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_org_merged_with_known_org(self, org: Organization):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # if we just have a name, try to merge with a known org 
        # defined in cellosaurus_institutions.cv and cellosaurus_xrefs.txt
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
        ns = self.ns
        # build an org object from data collected from annotations
        (name, shortname, city, country, contact) = data.split("|")
        if shortname == "": shortname = None
        if city == "": city = None
        if country == "": country = None
        if contact == "": contact = None
        org = Organization(name=name, shortname=shortname, city=city, country=country, contact=contact)

        # build the triples and return them
        triples = TripleList()

        orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store = False)
        triples.append(orga_IRI, ns.rdf.type, ns.schema.Organization)

        # if we have a shortname, it becomes the recommended name and name becomes the alternative name
        if org.shortname is not None and len(org.shortname)>0:
            triples.extend(self.get_materialized_triples_for_prop(orga_IRI, ns.cello.recommendedName, ns.xsd.string(org.shortname)))    # shortname => rec name
            triples.extend(self.get_materialized_triples_for_prop(orga_IRI, ns.cello.alternativeName, ns.xsd.string(org.name)))         # long name => alt name
        # if we have no shortname, name becomes the recommended name
        else:
            triples.extend(self.get_materialized_triples_for_prop(orga_IRI, ns.cello.recommendedName, ns.xsd.string(org.name)))         # long name => rec name
        
        if org.city is not None and len(org.city)>0:
            triples.append(orga_IRI, ns.cello.city, ns.xsd.string(org.city))

        if org.country is not None and len(org.country)>0:
            triples.append(orga_IRI, ns.cello.country, ns.xsd.string(org.country))

        if org.contact is not None and len(org.contact)>0:
            persons = org.contact.split(" & ")
            if len(persons) > 1: 
                log_it("DEBUG", "found multiple persons with ' & ' for org", data) 
            else:
                persons = org.contact.split(" and ")
                if len(persons) > 1: 
                    log_it("DEBUG", "found multiple persons with ' and ' for org", data) 
    
            for name in persons:
                p_BN = self.get_blank_node()
                triples.append(p_BN, ns.rdf.type, ns.schema.Person)
                triples.append(p_BN, ns.cello.isMemberOf, orga_IRI)
                triples.extend(self.get_triples_for_person_name_from_new_format(p_BN, name))

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
        ns = self.ns
        triples = TripleList()
        ref_data = ref_obj["publication"]    
        ref_IRI = self.get_pub_IRI(ref_data)

        # class: article, thesis, patent, ... (mandatory)
        ref_class = self.get_ref_class_IRI(ref_data)
        triples.append(ref_IRI, ns.rdf.type, ref_class)

        # internal id (mandatory) for debug purpose
        ref_id = ref_data["internal-id"]
        triples.append(ref_IRI, ns.cello.internalId, ns.xsd.string(ref_id))    

        # authors (mandatory)
        for p in ref_data["author-list"]:
            p_type = p.get("type")
            p_name = p["name"]
            if p_type == "consortium":
                orga_IRI = ns.orga.IRI(p_name, None, None, None, None)
                triples.append(ref_IRI, ns.cello.creator, orga_IRI)
            else:
                p_BN = self.get_blank_node()
                triples.append(ref_IRI, ns.cello.creator, p_BN)
                triples.append(p_BN, ns.rdf.type, ns.schema.Person)
                triples.extend(self.get_triples_for_person_name_from_json(p_BN, p))

        # title (mandatory)
        ttl = ref_data["title"]
        triples.append(ref_IRI, ns.cello.title, ns.xsd.string(ttl))

        # date (mandatory)
        dt = ref_data["date"]
        year = dt[-4:]
        triples.append(ref_IRI, ns.cello.publicationYear, ns.xsd.string(year))
        if len(dt) > 4:
            if len(dt) != 11: raise DataError("Publication", "Unexpecting date format in " + ref_id)
            day = dt[0:2]
            month = self.mmm2mm[dt[3:6]]
            #print("mydate",year,month,day)
            triples.append(ref_IRI, ns.cello.publicationDate, ns.xsd.date("-".join([year, month, day])))

        # xref-list (mandatory), we create a xref and a direct link to the url via cello:seeAlsoXref
        for xref in ref_data["xref-list"]:
            accession = xref["accession"]
            if self.get_xref_db(xref) == "PubMed": triples.append(ref_IRI, ns.cello.pmid, ns.xsd.string(accession))
            elif self.get_xref_db(xref) == "DOI": triples.append(ref_IRI, ns.cello.doi, ns.xsd.string3(accession))
            elif self.get_xref_db(xref) == "PMCID": triples.append(ref_IRI, ns.cello.pmcId, ns.xsd.string(accession))
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(ref_IRI, ns.cello.seeAlsoXref, xref_IRI)
            url = "". join(["<", self.encode_url(xref["url"]), ">"])
            triples.append(ref_IRI, ns.rdfs.seeAlso, url )


        # first page, last page, volume, journal (optional)
        p1 = ref_data.get("first-page")
        if p1 is not None: triples.append(ref_IRI, ns.cello.startingPage, ns.xsd.string(p1))
        p2 = ref_data.get("last-page")
        if p2 is not None: triples.append(ref_IRI, ns.cello.endingPage, ns.xsd.string(p2))
        vol = ref_data.get("volume")
        if vol is not None: triples.append(ref_IRI, ns.cello.volume, ns.xsd.string(vol))
        jou = ref_data.get("journal-name")
        if jou is not None: triples.append(ref_IRI, ns.cello.iso4JournalTitleAbbreviation, ns.xsd.string(jou))
        
        # city, country, institution and publisher
        city = ref_data.get("city")
        country = ref_data.get("country")
        institu = ref_data.get("institution")
        if institu is not None:
            orga_IRI = ns.orga.IRI(institu, None, city, country, None)
            triples.append(ref_IRI, ns.cello.publisher, orga_IRI)        
        publisher = ref_data.get("publisher")
        if publisher is not None:
            orga_IRI = ns.orga.IRI(publisher, None, city, country, None)
            triples.append(ref_IRI, ns.cello.publisher, orga_IRI)

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
            p_BN = self.get_blank_node()
            triples.append(ref_IRI, ns.cello.editor, p_BN)
            triples.append(p_BN, ns.rdf.type, ns.schema.Person)
            triples.extend(self.get_triples_for_person_name_from_json(p_BN, p))
        return("".join(triples.lines))


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_person_name_from_json(self, person_BN, person_obj):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns 
        triples = TripleList()
        p_name = person_obj["name"]
        triples.extend(self.get_materialized_triples_for_prop(person_BN, ns.cello.name, ns.xsd.string(p_name)))
        p_given = person_obj.get("first-names")
        p_family = person_obj.get("last-name")
        p_suffix = person_obj.get("name-suffix")
        if p_given is not None: triples.append(person_BN, ns.schema.givenName, ns.xsd.string(p_given))       # should never by None but only tested during XML generation
        if p_family is not None: triples.append(person_BN, ns.schema.familyName, ns.xsd.string(p_family))    # should never by None but only tested during XML generation
        if p_suffix is not None: triples.append(person_BN, ns.cello.nameSuffix, ns.xsd.string(p_suffix))     # is optional and rare
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_person_name_from_new_format(self, person_BN, name_in_new_format):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns 
        pn = PersonName(name_in_new_format)
        triples = TripleList()
        if pn.invalid:
            log_it("WARNING", "invalid person name format:", name_in_new_format)
            triples.extend(self.get_materialized_triples_for_prop(person_BN, ns.cello.name, ns.xsd.string(name_in_new_format)))
        else:
            triples.extend(self.get_materialized_triples_for_prop(person_BN, ns.cello.name, ns.xsd.string(pn.old_format)))
            triples.append(person_BN, ns.schema.givenName, ns.xsd.string(pn.firstnames))
            triples.append(person_BN, ns.schema.familyName, ns.xsd.string(pn.lastname))
            if pn.suffix is not None: triples.append(person_BN, ns.cello.nameSuffix, ns.xsd.string(pn.suffix))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_possibly_triples_for_xref_term_IRI(self, parent_node, xref):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # The method creates a list of triples.
        # The returned list might be empty or contain a single triple
        # depending on the existence of a term IRI in the xref
        triples = TripleList()
        term_IRI = self.get_xref_term_IRI(xref)
        if term_IRI: triples.append(parent_node, self.ns.cello.isIdentifiedByIRI, f"<{term_IRI}>")
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_cl(self, ac, cl_obj):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        cl_IRI = ns.cvcl.IRI(ac)
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
            pred = ns.cello.recommendedName if name_obj["type"] == "identifier" else ns.cello.alternativeName
            triples.extend(self.get_materialized_triples_for_prop(cl_IRI, pred, name))
        
        # fields: CC, registration
        for reg_obj in cl_data.get("registration-list") or []:
            
            name = ns.xsd.string(reg_obj["registration-number"])
            triples.extend(self.get_materialized_triples_for_prop(cl_IRI, ns.cello.registeredName, name))
            
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasRegistationRecord, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.RegistrationRecord)      
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.registeredName, name))
            org_name = reg_obj["registry"]
            org_IRI = ns.orga.IRI(org_name, "", "", "", "")
            triples.append(annot_BN, ns.cello.inRegister, org_IRI)
 
        # fields: CC, misspelling
        for msp_obj in cl_data.get("misspelling-list") or []:
            
            name = ns.xsd.string(msp_obj["misspelling-name"])
            triples.extend(self.get_materialized_triples_for_prop(cl_IRI, ns.cello.misspellingName, name))

            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasMisspellingRecord, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.MisspellingRecord)
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.misspellingName, name))
            note = msp_obj.get("misspelling-note")
            if note is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(note))
            for ref in msp_obj.get("reference-list") or []:
                triples.append(annot_BN, ns.cello.appearsIn, self.get_pub_IRI(ref))
            for xref in msp_obj.get("xref-list") or []:             
                triples.append(annot_BN, ns.cello.appearsIn, self.get_xref_IRI(xref))

        # fields: DR
        for xref in cl_data.get("xref-list") or []:
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(cl_IRI, ns.cello.seeAlsoXref, xref_IRI)
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(cl_IRI, xref))
            if self.get_xref_db(xref)=="Wikidata":
                # we use owl:sameAs because our cell lines and their equivalent in wikidata are instances (as opposed as classes)
                triples.append(cl_IRI, ns.owl.sameAs, ns.wd.IRI(xref["accession"])) 
            if self.get_xref_discontinued(xref):
                # also used for "CC   Discontinued: " lines       
                triples.extend(self.get_triples_for_cc_discontinued(cl_IRI, xref["database"], xref["accession"], xref_IRI)) 
                
        # fields: RX
        for rx in cl_data.get("reference-list") or []:
            triples.append(cl_IRI, ns.cello.references, self.get_pub_IRI(rx))
    
        # fields: WW
        for ww in cl_data.get("web-page-list") or []:
            # TODO: handle the 4 fields category, specifier, institution, not only url
            if type(ww) == str:
                ww_iri = str       # data_release < or = 51
            else:
                ww_iri = ww["url"] # data release > 51
            if is_valid_url(ww_iri):
                triples.append(cl_IRI, ns.rdfs.seeAlso, "".join(["<", ww_iri, ">"]))
            else:
                log_it("ERROR", f"Web page (WW) with Invalid IRI: {ww_iri}")

        
        # fields: SX
        sx = cl_data.get("sex")
        if sx is not None:
            triples.append(cl_IRI, ns.cello.derivedFromIndividualWithSex, get_sex_IRI(sx, ns))

        # fields: AG
        ag = cl_data.get("age")
        if ag is not None:
            triples.append(cl_IRI, ns.cello.derivedFromIndividualAtAge, ns.xsd.string(ag))

        # fields: OI
        for oi in cl_data.get("same-origin-as") or []:
            oi_iri = ns.cvcl.IRI(oi["accession"])
            triples.append(cl_IRI, ns.cello.derivedFromSameIndividualAs, oi_iri)

        # fields: HI
        for hi in cl_data.get("derived-from") or []:
            hi_iri = ns.cvcl.IRI(hi["accession"])
            triples.append(cl_IRI, ns.cello.hasParentCellLine, hi_iri)

        # fields: CH
        for ch in cl_data.get("child-list") or []:
            ch_iri = ns.cvcl.IRI(ch["accession"]["value"])
            triples.append(cl_IRI, ns.cello.hasChildCellLine, ch_iri)

        # fields: CA
        ca = cl_data["category"] # we expect one value for each cell line
        if ca is not None:
            triples.append(cl_IRI, ns.rdf.type, self.get_cl_category_class_IRI(ca))
        else:
            triples.append(cl_IRI, ns.rdf.type, ns.cello.CellLine)
            

        # fields DT, dtc, dtu, dtv
        triples.append(cl_IRI, ns.cello.created, ns.xsd.date(cl_data["created"]))
        triples.append(cl_IRI, ns.cello.modified, ns.xsd.date(cl_data["last-updated"]))
        triples.append(cl_IRI, ns.cello.version, ns.xsd.string(cl_data["entry-version"]))

        # fields: CC, genome-ancestry
        annot = cl_data.get("genome-ancestry")
        if annot is not None:
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasGenomeAncestry, annot_BN)
            triples.append(annot_BN, ns.rdf.type ,ns.cello.GenomeAncestry)
            # ref can be publi or organization, but only publi in real data
            src = annot.get("source")
            if src is not None: 
                triples.extend(self.get_triples_for_source(annot_BN, src))
            else:
                log_it("ERROR", f"reference of genome-ancestry source is null: {ac}")
            for pop in annot["population-list"]:
                pop_percent_BN = self.get_blank_node()
                triples.append(annot_BN, ns.cello.hasComponent, pop_percent_BN)
                triples.append(pop_percent_BN, ns.rdf.type, ns.cello.PopulationPercentage)
                pop_name = ns.xsd.string(pop["population-name"])
                pop_BN = self.get_blank_node()
                triples.append(pop_BN, ns.rdf.type, ns.cello.Population)
                triples.extend(self.get_materialized_triples_for_prop(pop_BN, ns.cello.name, pop_name))
                triples.append(pop_percent_BN, ns.cello.hasPopulation, pop_BN)
                percent = ns.xsd.float(pop["population-percentage"])
                triples.append(pop_percent_BN, ns.cello.percentage, percent)

        # fields: CC hla
        for annot in cl_data.get("hla-typing-list") or []:
            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasHLAtyping, annot_BN)
            triples.append(annot_BN, ns.rdf.type ,ns.cello.HLAtyping)
            src = annot.get("source")
            if src is not None: 
                triples.extend(self.get_triples_for_source(annot_BN, src))
            for gall in annot["hla-gene-alleles-list"]:
                gene_label = gall["gene"]
                for allele in gall["alleles"].split(","):
                    obs_BN = self.get_blank_node()
                    triples.append(annot_BN, ns.cello.includesObservation, obs_BN)                    
                    triples.append(obs_BN, ns.rdf.type, ns.schema.Observation)
                    gene_BN = self.get_blank_node()
                    triples.append(obs_BN, ns.cello.hasTarget, gene_BN)
                    triples.extend(self.get_triples_for_hla_gene_instance(gene_BN, gene_label))
                    allele_BN = self.get_blank_node()
                    allele_id = "*".join([gene_label, allele])
                    triples.append(obs_BN, ns.cello.detectedAllele, allele_BN)
                    triples.append(allele_BN, ns.rdf.type, ns.cello.HLA_Allele)
                    triples.append(allele_BN, ns.cello.alleleIdentifier, ns.xsd.string(allele_id))

        # fields: CC str, WARNING: str-list is not a list !!!
        annot = cl_data.get("str-list")
        if annot is not None:
            triples.extend(self.get_triples_for_short_tandem_repeat(cl_IRI, annot))

        # fields: di
        for annot in cl_data.get("disease-list") or []:
            triples.extend(self.get_triples_for_disease(cl_IRI, annot))

        # fields: ox
        for annot in cl_data.get("species-list") or []:
            triples.extend(self.get_triples_for_species(cl_IRI, annot))

        # field: breed
        breed_annot = cl_data.get("breed")
        if breed_annot is not None:
            triples.extend(self.get_triples_for_breed(cl_IRI, breed_annot))

        # fields: CC sequence-variation
        for annot in cl_data.get("sequence-variation-list") or []:
            triples.extend(self.get_triples_for_sequence_variation(cl_IRI, annot))

        # fields: derived-from-site
        for annot in cl_data.get("derived-from-site-list") or []:
            triples.extend(self.get_triples_for_derived_from_site(cl_IRI, annot))

        ct_annot = cl_data.get("cell-type")
        if ct_annot is not None:
            triples.extend(self.get_triples_for_cell_type(cl_IRI, ct_annot))

        # fields: CC doubling-time
        for annot in cl_data.get("doubling-time-list") or []:
            triples.extend(self.get_triples_for_doubling_time(cl_IRI, annot))

        # fields: doubling-time-range
        ct_annot = cl_data.get("doubling-time-range")
        if ct_annot is not None:
            triples.extend(self.get_triples_for_doubling_time_range(cl_IRI, ct_annot))

        # fields: CC transformant
        for annot in cl_data.get("transformant-list") or []:
            triples.extend(self.get_triples_for_transformant(cl_IRI, annot))

        # fields: CC msi
        for annot in cl_data.get("microsatellite-instability-list") or []:
            triples.extend(self.get_triples_for_msi(cl_IRI, annot))

        # fields: CC mab-isotype
        for annot in cl_data.get("monoclonal-antibody-isotype-list") or []:
            triples.extend(self.get_triples_for_mab_isotype(cl_IRI, annot))

        # fields: CC mab-target
        for annot in cl_data.get("monoclonal-antibody-target-list") or []:
            triples.extend(self.get_triples_for_mab_target(cl_IRI, annot))

        # fields: CC resistance
        for annot in cl_data.get("resistance-list") or []:
            triples.extend(self.get_triples_for_resistance(cl_IRI, annot))

        # fields: CC knockout
        for annot in cl_data.get("knockout-cell-list") or []:
            triples.extend(self.get_triples_for_cc_knockout_cell(cl_IRI, annot))

        # fields: CC integration
        for annot in cl_data.get("genetic-integration-list") or []:
            triples.extend(self.get_triples_for_cc_genetic_integration(cl_IRI, annot))

        # fields: CC omics
        for annot in cl_data.get("omics-list") or []:
            triples.extend(self.get_triples_for_cc_omics_info(cl_IRI, annot))

        # fields: CC from, ...
        for cc in cl_data.get("comment-list") or []:
            categ = cc["category"]
            if categ == "From": 
                triples.extend(self.get_triples_for_cc_from(cl_IRI, cc))
            elif categ == "Part of":
                triples.extend(self.get_triples_for_cc_part_of(cl_IRI, cc))            
            elif categ == "Group":
                triples.extend(self.get_triples_for_cc_in_group(cl_IRI, cc))
            elif categ == "Anecdotal":
                triples.extend(self.get_triples_for_cc_anecdotal(cl_IRI, cc))
            elif categ == "Biotechnology":
                triples.extend(self.get_triples_for_cc_biotechnology(cl_IRI, cc))
            elif categ == "Characteristics":
                triples.extend(self.get_triples_for_cc_characteristics(cl_IRI, cc))
            elif categ == "Caution":
                triples.extend(self.get_triples_for_cc_caution(cl_IRI, cc))
            elif categ == "Donor information":
                triples.extend(self.get_triples_for_cc_donor_info(cl_IRI, cc))
            elif categ == "Discontinued":
                provider, product_id = cc["value"].split("; ")
                triples.extend(self.get_triples_for_cc_discontinued(cl_IRI, provider, product_id)) # also used in DR lines
            elif categ == "Karyotypic information":
                triples.extend(self.get_triples_for_cc_karyotypic_info(cl_IRI, cc))
            elif categ == "Miscellaneous":
                triples.extend(self.get_triples_for_cc_miscellaneous_info(cl_IRI, cc))
            elif categ == "Problematic cell line":
                triples.extend(self.get_triples_for_cc_problematic_info(cl_IRI, cc))
            elif categ == "Senescence":
                triples.extend(self.get_triples_for_cc_senescence_info(cl_IRI, cc))
            elif categ == "Virology":
                triples.extend(self.get_triples_for_cc_virology_info(cl_IRI, cc))
            elif categ == "Population":
                triples.extend(self.get_triples_for_cc_population_info(cl_IRI, cc))

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
    def get_triples_for_sequence_variation(self, cl_IRI, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        try:
            triples = TripleList()

            annot_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasSequenceVariationInfo, annot_BN)
            triples.append(annot_BN, ns.rdf.type, ns.cello.SequenceVariationInfo)
            mut_type = annot.get("mutation-type")
            variationStatus = "Natural"
            if mut_type is not None and "edited" in mut_type: variationStatus = "Edited"
            if mut_type is not None and "corrected" in mut_type: variationStatus = "Corrected"
            triples.append(annot_BN, ns.cello.variationStatus, ns.xsd.string(variationStatus))
            var_sources = annot.get("source-list") or []
            triples.extend(self.get_triples_for_sources(annot_BN, var_sources))

            seqvar_BN = self.get_blank_node()
            triples.append(annot_BN, ns.cello.hasTarget, seqvar_BN)
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
            triples.extend(self.get_materialized_triples_for_prop(seqvar_BN, ns.cello.name, ns.xsd.string(label))) # TODO? remove first hgvs from label        
        
            if var_type=="Mutation" and mut_type.startswith("Simple"): 
                hgvs_list = self.extract_hgvs_list(label)
                if len(hgvs_list) not in [1,2]: log_it("WARNING", f"invalid hgvs in: {label}")
                for hgvs in hgvs_list: 
                    triples.extend(self.get_materialized_triples_for_prop(seqvar_BN, ns.cello.hgvs, ns.xsd.string(hgvs)))       
                    
            for xref in annot.get("xref-list"):
                db = xref["database"]
                if db in ["HGNC", "MGI", "RGD", "VGNC", "UniProtKB"]:
                    gene_BN = self.get_blank_node()
                    triples.append(seqvar_BN, ns.cello.ofGene, gene_BN)
                    triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
                    gene_label =  self.get_xref_label(xref)
                    if gene_label is not None and len(gene_label) > 0:
                        triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(gene_label)))       
                    triples.append(gene_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref)) # gene(s) related to the variation
                elif db in ["ClinVar", "dbSNP"]:
                    triples.append(seqvar_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref)) # reference of the variant description

            return triples

        except DataError as e:
            (typ,details) = e.args        
            cl_ac = cl_IRI.split(":")[1]
            log_it("ERROR", f"{typ} - {details} : {cl_ac}")
            return TripleList()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_sequence_variation_class(self, var_type, mut_type):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
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
            if mut_type.startswith("Simple"): return ns.cello.GeneMutation
            if mut_type.startswith("Repeat"): return ns.cello.RepeatExpansion
            if mut_type.startswith("Unexplicit"): return ns.cello.GeneMutation
            if mut_type == "None_reported": return ns.cello.GeneMutation
        elif var_type == "Gene fusion": return ns.cello.GeneFusion
        elif var_type == "Gene deletion": return ns.cello.GeneDeletion
        elif var_type == "Gene amplification":
            if mut_type == "Triplication": return ns.cello.GeneTriplication
            if mut_type == "Duplication": return ns.cello.GeneDuplication
            if mut_type == "Quadruplication": return ns.cello.GeneQuadruplication
            if mut_type == "Extensive": return ns.cello.GeneExtensiveAmplification
            if mut_type == "None_reported": return ns.cello.GeneAmplification # not in data but we never know    
        raise DataError("SequenceVariation", f"Unexpected variation-type / mutation-type combination: {var_type} / {mut_type}")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_from(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        value = cc["value"]
        elems = value.split("; ")
        contact=elems.pop(0) if len(elems) == 4 else ""
        if len(elems) != 3: 
            cl_ac = cl_IRI.split(":")[1]
            log_it("ERROR", f"expected 3-4 tokens in CC From comment '{value}' : {cl_ac}")
            return triples
        orga_IRI = ns.orga.IRI(elems[0], "", elems[1], elems[2], contact)
        triples.append(cl_IRI, ns.cello.establishedBy, orga_IRI)
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_part_of(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        label = cc["value"]
        triples.append(cl_IRI, ns.cello.inCollection, ns.xsd.string(label))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_in_group(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        label = cc["value"]
        triples.append(cl_IRI, ns.cello.inGroup, ns.xsd.string(label))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_breed(self, cl_IRI, breed):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.comesFomIndividualBelongingToBreed, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Breed)
        if type(breed) == str:
            label = breed
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(label)))
            
        else:
            label = breed["value"]
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(label)))
            for xref in breed.get("xref-list") or []:
                triples.append(annot_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref))
                triples.extend(self.get_possibly_triples_for_xref_term_IRI(annot_BN, xref))

        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_characteristics(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasCharacteristicsComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.CharacteristicsComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_caution(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasCautionComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.CautionComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_biotechnology(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasBiotechnologyComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.BiotechnologyComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_anecdotal(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasAnecdotalComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.AnecdotalComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_donor_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasDonorInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.DonorInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))

        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_karyotypic_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasKaryotypicInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.KaryotypicInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_miscellaneous_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasMiscellaneousInfoComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.MiscellaneousInfoComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_problematic_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasProblematicCellLineComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.ProblematicCellLineComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_senescence_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasSenescenceComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.SenescenceComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_virology_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        comment = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasVirologyComment, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.VirologyComment)
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(inst_BN, cc.get("source-list") or []))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_genetic_integration(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        method = cc.get("method")
        note = cc.get("genetic-integration-note")
        xref = cc.get("xref")
        nameonly = cc.get("value")
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasGeneticIntegration, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.GeneticIntegration)
        triples.append(inst_BN, ns.cello.hasGenomeModificationMethod, self.get_gem_IRI(method))
        if note is not None: 
            triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(note))
        gene_BN = self.get_blank_node()
        triples.append(inst_BN, ns.cello.ofGene, gene_BN)
        triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
        if nameonly is not None:
            triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(nameonly)))
        else:
            triples.append(gene_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref))
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(gene_BN, xref))
            gene_name =  self.get_xref_label(xref)
            if gene_name is not None and len(gene_name)>0:
                triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(gene_name)))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_knockout_cell(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        method = cc.get("method")
        comment = cc.get("knockout-cell-note") # optional
        xref = cc.get("xref")
        if method is None or xref is None:
            log_it("WARNING", f"missing method or gene xref in knockout comment in {cl_IRI}")
        else:
            inst_BN = self.get_blank_node()
            triples.append(cl_IRI, ns.cello.hasGeneKnockout, inst_BN)
            triples.append(inst_BN, ns.rdf.type, ns.cello.GeneKnockout)
            triples.append(inst_BN, ns.cello.hasGenomeModificationMethod, self.get_gem_IRI(method))
            gene_BN = self.get_blank_node()
            triples.append(inst_BN, ns.cello.ofGene, gene_BN)
            triples.append(gene_BN, ns.rdf.type, ns.cello.Gene)
            triples.append(gene_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref))
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(gene_BN, xref))
            gene_name =  self.get_xref_label(xref)
            if gene_name is not None and len(gene_name)>0:
                triples.extend(self.get_materialized_triples_for_prop(gene_BN, ns.cello.name, ns.xsd.string(gene_name)))
            if comment is not None: 
                triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_omics_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        branch = cc["branch"]
        value = cc.get("value")
        comment = branch
        if value is not None and len(value) > 0: comment = "; ".join([branch, value])
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasOmicsInfo, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.OmicsInfo)
        triples.append(inst_BN, ns.schema.category, ns.xsd.string(branch))
        triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_population_info(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        nameOrNames = cc["value"]
        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.derivedFromIndividualBelongingToPopulation, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.Population)
        triples.extend(self.get_materialized_triples_for_prop(inst_BN, ns.cello.name, ns.xsd.string(nameOrNames)))
        return triples



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_derived_from_site(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        site_BN = self.get_blank_node()
        note = annot.get("site-note")
        site = annot["site"]
        site_type = site["site-type"]
        label = site["value"]
        triples.append(cl_IRI, ns.cello.derivedFromSite, site_BN)
        triples.append(site_BN, ns.rdf.type, ns.cello.AnatomicalEntity)
        triples.append(site_BN, ns.cello.siteType, ns.xsd.string(site_type))
        triples.extend(self.get_materialized_triples_for_prop(site_BN, ns.cello.name, ns.xsd.string(label)))
        if note is not None:
            triples.append(site_BN, ns.rdfs.comment, ns.xsd.string(note)) 
        for xref in site.get("xref-list") or []: 
            triples.append(site_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(xref))
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(site_BN, xref))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cell_type(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        ct_BN = self.get_blank_node()
        if isinstance(annot, str):  # when we have free text only without a xref
            label, cv = (annot, None)
        else:
            label, cv = (annot["value"], annot.get("xref"))
        triples.append(cl_IRI, ns.cello.derivedFromCellType, ct_BN)
        triples.append(ct_BN, ns.rdf.type, ns.cello.CellType)
        triples.extend(self.get_materialized_triples_for_prop(ct_BN, ns.cello.name, ns.xsd.string(label)) )   
        if cv is not None: 
            triples.append(ct_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(cv))
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(ct_BN, cv))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_cc_discontinued(self, cl_IRI, provider, product_id, xref_IRI=None):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasDiscontinuationRecord, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.DiscontinuationRecord)
        org = Organization(provider, "", "", "", "")
        org = self.get_org_merged_with_known_org(org)
        orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store=True)
        triples.append(annot_BN, ns.cello.hasProvider, orga_IRI)
        triples.append(annot_BN, ns.cello.productId, ns.xsd.string(product_id))
        if xref_IRI is not None:
            triples.append(annot_BN, ns.cello.seeAlsoXref, xref_IRI)
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_source(self, parentNode, src):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        src_BN = self.get_blank_node()
        triples.append(parentNode, ns.cello.hasSource, src_BN)
        triples.append(src_BN, ns.rdf.type, ns.cello.Source)
        if type(src) == dict:
            lbl = src.get("value")
            if lbl is not None:
                triples.extend(self.get_materialized_triples_for_prop(src_BN, ns.cello.name, ns.xsd.string(lbl)))
            inst = src.get("institution")
            if inst is not None:
                # build an org object from field 'institution' and get 
                # optional params from known orgs 
                # BEFORE we build the IRI and store the params 
                org = Organization(inst, "", "", "", "")
                org = self.get_org_merged_with_known_org(org)
                orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store=True)
                triples.append(src_BN, ns.cello.originatesFrom, orga_IRI)
            xref = src.get("xref")
            if xref is not None:
                triples.append(src_BN, ns.cello.originatesFrom, self.get_xref_IRI(xref))
                triples.extend(self.get_possibly_triples_for_xref_term_IRI(src_BN, xref))
            ref =src.get("reference")
            if ref is not None: 
                triples.append(src_BN, ns.cello.originatesFrom, self.get_pub_IRI(ref))
        elif type(src) == str:
            #print("string/src", src)
            if src == "Direct_author_submission" or src.startswith("from inference of"):
                triples.extend(self.get_materialized_triples_for_prop(src_BN, ns.cello.name, ns.xsd.string(src)))
            else:
                # build an org object from label 'src' and get 
                # optional params from known orgs 
                # BEFORE we build the IRI and store the params 
                org = Organization(src, "", "", "", "")
                org = self.get_org_merged_with_known_org(org)
                orga_IRI = ns.orga.IRI(org.name, org.shortname, org.city, org.country, org.contact, store=True)
                triples.append(src_BN, ns.cello.originatesFrom, orga_IRI)
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
    def get_triples_for_sources(self, parentNode, sources):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        triples = TripleList()
        for src in sources or []:
            triples.extend(self.get_triples_for_source(parentNode, src))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_doubling_time(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        duration = annot["doubling-time-value"]
        comment = annot.get("doubling-time-note")
        sources = annot.get("source-list") or [] 
        triples.append(cl_IRI, ns.cello.hasDoublingTime, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.DoublingTime)
        triples.append(annot_BN, ns.cello.duration, ns.xsd.string(duration))
        if comment is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(annot_BN, sources))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_doubling_time_range(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        min = annot["min"]
        max = annot["max"]
        unit = annot["unit"]
        if unit == "hour": unit = "HUR" # ISO 4217 code for hour
        triples.append(cl_IRI, ns.cello.hasDoublingTimeRange, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.DoublingTimeRange)
        triples.append(annot_BN, ns.schema.minValue, ns.xsd.integer(min))
        triples.append(annot_BN, ns.schema.maxValue, ns.xsd.integer(max))
        triples.append(annot_BN, ns.schema.unitCode, ns.xsd.string(unit))
        return triples



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_msi(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        value = annot["msi-value"]
        value_IRI = get_Msi_Status_IRI(value, ns)
        comment = annot.get("microsatellite-instability-note")
        sources = annot.get("source-list") or [] 
        triples.append(cl_IRI, ns.cello.hasMicrosatelliteInstability, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.MicrosatelliteInstability)
        triples.append(annot_BN, ns.cello.hasMicrosatelliteInstabilityStatus, value_IRI)
        if comment is not None: triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        triples.extend(self.get_triples_for_sources(annot_BN, sources))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_mab_isotype(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        heavy = annot["heavy-chain"]
        light = annot.get("light-chain")
        if light is None:
            if heavy == "Not specified":
                light = "Not specified"
            else:
                light = "Not determined"
        sources = annot.get("source-list") or []
        for h in heavy.split("+"):
            for l in light.split("+"):
                annot_BN = self.get_blank_node()
                triples.append(cl_IRI, ns.cello.hasMoAbIsotype, annot_BN)
                triples.append(annot_BN, ns.rdf.type, ns.cello.MoAbIsotype)
                igh_BN = self.get_blank_node()
                triples.append(annot_BN, ns.cello.hasAntibodyHeavyChain, igh_BN)
                triples.append(igh_BN, ns.rdf.type, ns.cello.ImmunoglobulinHeavyChain)
                triples.extend(self.get_materialized_triples_for_prop(igh_BN, ns.cello.name, ns.xsd.string(h)))
                igl_BN = self.get_blank_node()
                triples.append(annot_BN, ns.cello.hasAntibodyLightChain, igl_BN)
                triples.append(igl_BN, ns.rdf.type, ns.cello.ImmunoglobulinLightChain)
                triples.extend(self.get_materialized_triples_for_prop(igl_BN, ns.cello.name, ns.xsd.string(l)))
                triples.extend(self.get_triples_for_sources(annot_BN, sources))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_mab_target(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        clazz = ns.cello.ChemicalEntity # init to some default

        # we might get a simple string in annot (the name of the antigen)
        if type(annot) == str:
            triples.append(cl_IRI, ns.cello.hasMoAbTarget, annot_BN)
            if self.looks_like_a_protein(annot): 
                clazz = ns.cello.Protein
            elif self.looks_like_a_chemical(annot):
                # keep default: ChemicalEntity
                pass
            else:
                # keep default: ChemicalEntity
                log_it("DEBUG", f"Unspecified MoAbTarget in {cl_IRI}: {annot}" )    
            triples.append(annot_BN, ns.rdf.type, clazz)
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(annot)))
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
                clazz = ns.cello.Protein
            elif db == "ChEBI":
                clazz = ns.cello.ChemicalEntity
            else:
                raise DataError("Monoclonal antibody target", "Unexpected xref database: " + db)

        triples.append(cl_IRI, ns.cello.hasMoAbTarget, annot_BN)
        triples.append(annot_BN, ns.rdf.type, clazz)
        triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(name)))
        if comment is not None:
            triples.append(annot_BN, ns.rdfs.comment, ns.xsd.string(comment))
        if xref is not None:
            triples.append(annot_BN, ns.cello.isIdentifiedByXref, xref_IRI)
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(annot_BN, xref))

        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_resistance(self, cl_IRI, annot):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasResistance, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.ChemicalEntity)
        # we might get a simple string in annot (the name of the chemical)
        if type(annot) == str:
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(annot)))
        # or more often we get a dict object
        else:
            xref = annot.get("xref")
            name = self.get_xref_label(xref)
            xref_IRI = self.get_xref_IRI(xref)
            triples.append(annot_BN, ns.cello.isIdentifiedByXref, xref_IRI)
            triples.extend(self.get_possibly_triples_for_xref_term_IRI(annot_BN, xref))
            triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(name)))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_transformant(self, cl_IRI, cc):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()

        inst_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.transformedBy, inst_BN)
        triples.append(inst_BN, ns.rdf.type, ns.cello.ChemicalEntity)

        # we might get a simple string in annot (the name of the chemical)
        if type(cc) == str:
            triples.extend(self.get_materialized_triples_for_prop(inst_BN, ns.cello.name, ns.xsd.string(cc)))
        # or more often we get a dict object
        else:
            term = cc.get("xref")                   # optional too
            if term is not None:
                triples.append(inst_BN, ns.cello.isIdentifiedByXref, self.get_xref_IRI(term))
                triples.extend(self.get_possibly_triples_for_xref_term_IRI(inst_BN, term))
                triples.extend(self.get_materialized_triples_for_prop(inst_BN, ns.cello.name, ns.xsd.string(self.get_xref_label(term))))
            else:
                triples.extend(self.get_materialized_triples_for_prop(inst_BN, ns.cello.name, ns.xsd.string(cc["value"])))
            comment = cc.get("transformant-note")   # optional
            if comment is not None: 
                triples.append(inst_BN, ns.rdfs.comment, ns.xsd.string(comment))
        return triples



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_str_observation_list(self, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        obs_dict = dict()

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
                    alleles.append("X") if "X" in marker_data["marker-alleles"] else alleles.append("Not_X") # make undetected AMELX explicit
                    alleles.append("Y") if "Y" in marker_data["marker-alleles"] else alleles.append("Not_Y") # make undetected AMELY explicit
                else:
                    for allele in marker_data["marker-alleles"].split(","):
                        if allele == "Not_detected": continue # we ignore other undetected markers (non-Amelogenin)
                        alleles.append(allele)
                for allele in alleles:
                    key = "".join([marker_id,allele])
                    if key not in obs_dict: 
                        obs_dict[key] = {"marker_id": marker_id, "allele": allele, "conflict": False, "srckey_set": set(), "obs_source_list": list()}
                    rec = obs_dict[key]
                    rec["srckey_set"].update(dat_src_key_set)
                    rec["obs_source_list"].extend(marker_data.get("source-list") or [])
        for obs in obs_dict.values():
            if obs["srckey_set"] != set() and obs["srckey_set"] != mrk_src_key_dict[obs["marker_id"]]:
                obs["conflict"] = True
        return list(obs_dict.values())


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_str_marker_instance(self, marker_BN, id):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        triples.append(marker_BN, ns.rdf.type, ns.cello.Marker)
        triples.append(marker_BN, ns.cello.markerId, ns.xsd.string(id))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_str_allele_instance(self, allele_BN, repeat_number):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        triples.append(allele_BN, ns.rdf.type, ns.cello.STR_Allele)
        triples.append(allele_BN, ns.cello.repeatNumber, ns.xsd.string(repeat_number))
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_short_tandem_repeat(self, cl_IRI, annot):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.hasShortTandemRepeatProfile, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.ShortTandemRepeatProfile)
        sources = annot["source-list"]
        triples.extend(self.get_triples_for_sources(annot_BN, sources))

        for obs in self.get_str_observation_list(annot):
            #print(">>>obs", cl_IRI, obs)
            marker_id = obs["marker_id"]
            allele = obs["allele"]
            sources = obs["obs_source_list"]
            conflict = obs["conflict"]
            obs_BN = self.get_blank_node()
            triples.append(annot_BN, ns.cello.includesObservation, obs_BN)
            triples.append(obs_BN, ns.rdf.type, ns.schema.Observation)
            triples.extend(self.get_materialized_triples_for_prop(obs_BN, ns.cello.name, ns.xsd.string(f"Observation of {marker_id}")))
            marker_BN = self.get_blank_node()
            if marker_id == "Amelogenin":
                gene_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.hasTarget, gene_BN)
                chr = "X" if allele in  ["X", "Not_X"] else "Y" 
                triples.extend(self.get_triples_for_amelogenin_gene_instance(gene_BN, chr))
                detected = not "Not" in allele
                triples.append(obs_BN, ns.cello.detectedTarget, ns.xsd.boolean(detected))
                triples.append(obs_BN, ns.cello.conflicting, ns.xsd.boolean(conflict))
            else:
                marker_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.hasTarget, marker_BN)
                triples.extend(self.get_triples_for_str_marker_instance(marker_BN, marker_id))
                allele_BN = self.get_blank_node()
                triples.append(obs_BN, ns.cello.detectedAllele, allele_BN)
                triples.extend(self.get_triples_for_str_allele_instance(allele_BN, allele))
                triples.append(obs_BN, ns.cello.conflicting, ns.xsd.boolean(conflict))
            if conflict:
                triples.extend(self.get_triples_for_sources(obs_BN, sources))
   
        return triples


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_disease(self, cl_IRI, cvterm):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.derivedFromIndividualWithDisease, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Disease)
        name = self.get_xref_label(cvterm)
        xref_IRI = self.get_xref_IRI(cvterm)
        triples.append(annot_BN, ns.cello.isIdentifiedByXref, xref_IRI)
        triples.extend(self.get_possibly_triples_for_xref_term_IRI(annot_BN, cvterm))
        triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(name)))
        return triples

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_triples_for_species(self, cl_IRI, xref):    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ns = self.ns
        triples = TripleList()
        annot_BN = self.get_blank_node()
        triples.append(cl_IRI, ns.cello.derivedFromIndividualBelongingToSpecies, annot_BN)
        triples.append(annot_BN, ns.rdf.type, ns.cello.Species)
        name = self.get_xref_label(xref)
        xref_IRI = self.get_xref_IRI(xref)
        triples.append(annot_BN, ns.cello.isIdentifiedByXref, xref_IRI)
        triples.extend(self.get_possibly_triples_for_xref_term_IRI(annot_BN, xref))
        triples.extend(self.get_materialized_triples_for_prop(annot_BN, ns.cello.name, ns.xsd.string(name)))
        return triples
