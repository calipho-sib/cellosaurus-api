
**Links with other ontologies**

Most of the classes and properties defined within the Cellosaurus ontology (prefix cello:) are derived from existing terms defined in general purpose or domain specific OWL ontologies. In this version (revision 1.0):

* Out of 131 classes, 126 are rdfs:subClassOf+ or / and owl:equivalentClass of an external term.

* Out of 108 properties, 90 are rdfs:subPropertyOf+ or / and owl:equivalentProperty of an external term.


More details about the subsuming / equivalency term relationships are available in the SPARQL query examples at [sparql-editor](/sparql-editor).

Since Cellosaurus is an extensive description of cell lines, multiple ontologies were required to cover its conceptual field, among which :

* [IAO is_about](http://purl.obolibrary.org/ontology/IAO_0000136) to define [cello:hasAnnotation](#hasAnnotation) as its inverse property (owl:inverseOf)

* [IAO DataItem](http://purl.obolibrary.org/ontology/IAO_0000027) as a superclass of several topic comments in conjunction with EDAM concepts topic and has_topic. See for example [cello:DonorInfoComment](#DonorInfoComment)

* [BFO has_part](http://purl.obolibrary.org/obo/BFO_0000051) as a super property for [cello:hasAntibodyLightChain](#hasAntibodyLightChain) and others

* Multiple [schema.org concepts](https://schema.org/) concepts for person, organization, location, and observation entities

* Some [dcterms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-2) properties are used as super properties for many of our terms, see [dcterms:source](#httppurlorgdctermssource) and [dcterms:identifier](#httppurlorgdctermsidentifier).

* For publication citations, our terms are mostly derived from dcterms and from [FaBiO](http://purl.org/spar/fabio) which extends dcterms and provides with a classification of bibliographic entities and more attributes.

* We use [OBI Genetic transformation](http://purl.obolibrary.org/obo/OBI_0600043) as a superclass for [cello:GenomeModificationMethod](#GenomeModificationMethod) subclasses and [OBI Genetic characteristics information](http://purl.obolibrary.org/obo/OBI_0001404) and other OBI terms to root and organize  multiple cell line annotations types as seen [here](#httppurlobolibraryorgoboOBI_0001404)

* Root biological concepts like disease, gene, marker, sequence variations from [NCIt](https://ncithesaurus.nci.nih.gov) are used as subsuming or equivalent to our terms. See for example [cello:Sequencevariation](#SequenceVariation)

* [UBERON](https://obophenotype.github.io/uberon/) and [CL](https://obophenotype.github.io/cell-ontology/) which describe anatomical terms and cell types respectively.

* [ChEBI](https://www.ebi.ac.uk/chebi/) serves as a root to define chemical compounds and [cello:Protein](#Protein)

* [cello:CellLine](#CellLine) sub-classes have an owl:equivalentClass in [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) and 5 cell line properties have owl:equivalentProperty as well. Note that every cell line of Cellosaurus is also described in Wikidata. The content of Wikidata regarding cellosaurus cell lines is synchronized with a bot running on each new Cellosaurus release. 

* [skos](https://www.w3.org/2004/02/skos/) terms are used to define local [concept schemes](#CelloConceptScheme) and to link related concepts within concept schemes. It is also used to add informal semantic links between terms across ontologies, for example between [cello:PrivaDocentThesis](#PrivaDocentThesis) and [up:ThesisCitation](https://purl.uniprot.org/html/index-en.html#Thesis_Citation). Note that skos properties linking our terms to other ontology terms are displayed in the _has relation_ section of the term.

**Cross-references**

[Xref](#Xref) instances are widely used in Cellosaurus. They have their own namespace and IRIs. A cross-reference instance provides information about its database, its identifier within the database (accession) and an URL pointing to a Web page. It may also come with an optional _rdfs:label_ property or _discontinued_ property depending on the context.

The most common use cases are:

* with [cello:seeAlsoXref](#seeAlsoXref) property to propose additional information about a cell line

* with [cello:originatesFrom](#originatesFrom) property for indicate the origin of a source of information

* with [cello:isIdentifiedByXref](#isIdentifiedByXref) property where it plays the role of an identifier 
for some instance of Gene, Species, Anatomical, Chemical or other kind of entity. 

**Concept schemes and concepts**

Sub-classes of [cello:Database](#Database) may have instances (named individuals) which also belong to [cello:CelloConceptScheme](#CelloConceptScheme), see for example [db:ORDO](#httplocalhostrdfdbORDO). 

This occurs when the cross-references of a database can also be seen as concepts linked to each other to form a hierachy of concepts, that is an ontology. 

Such cross-references are also declared as instances of [skos:Concept](#httpwwww3org200402skoscoreConcept) and linked to each other within their CelloConceptScheme with [cello:more_specific_than](#more_specific_than) properties. 

For any cross-reference used in Cellosaurus to somehow describe a cell line and which belongs to either db:CL, db:ChEBI, db:NCBI_TaxID, db:NCIt, db:ORDO, db:RS, db:UBERON, or db:VBO, we provide with:

* all the parent concepts up to the root concept in the original ontology

* the hierarchical structure with property _cello:more_specific_than_ properties linking concepts

Making the hierarchy of concepts available within Cellosaurus makes it possible to build SPARQL queries using a criterion like 

> ?any_concept cello:more_specific_than* ?some_concept . 

See also SPARQL query examples at [sparql-editor](/sparql-editor) 

**Names for instances**

The instances of many classes have names. And to give a thing a name we use many different properties: rdfs:label, skos:prefLabel, cello:recommendedName, cello:alternativeName, cello:registeredName, etc. used in different contexts. 

All these properties have a specific function but sometimes you just don't know whether the name you have in mind is a recommended or an alternative name or whatever. To solve this problem, we provide a so-called materialization of triples that can be inferred from the hierarchy of naming properties.

As an example, if you're looking for 'He-La' cell line ('He-La' is an cello:alternativeName of cvcl:CVCL_0030), you can simply use the cello:name property in the basic graph pattern:

> select ... where {
>   ?cl cello:name 'He-La'^^xsd:string .
> }

This is because cello:alternativeName is defined as a rdfs:subPropertyOf cello:name

See also the usage of name properties for instances of each class in SPARQL query examples at [sparql-editor](/sparql-editor). 

**Named individuals**

The ontology defines a number of so-called named individuals (owl:NamedIndividual). They belong to a few classes:

* [cello:CelloConceptScheme](#CelloConceptScheme) class and [cello:Database](#Database) sub-classes are populated with named individuals, example [db:ATCC](#httplocalhostrdfdbATCC)

* [cello:GenomeModificationMethod](#GenomeModificationMethod) class and its sub-classes are populated with named individuals, example: [cello:CrisprCas9](#CrisprCas9)

* [Sex](#Sex) class is defined as a set of named individuals, example [cello:MixedSex](#MixedSex).

**Main namespaces**

| Prefix     | IRI        | Name |
|------------|------------|------|
| cello:     | $cello_url | Cellosaurus ontology classes and properties |
| cvcl:      | $cvcl_url  | Cellosaurus cell line instances |
| orga:      | $orga_url  | Cellosaurus organization instances |
| db:        | $db_url    | Cellosaurus online database and concept scheme named individuals |
| xref:      | $xref_url  | Cellosaurus cross-reference and concept instances |
| BFO:       | http://purl.obolibrary.org/obo/BFO_ | Basic Formal Ontology |
| CHEBI:     | http://purl.obolibrary.org/obo/CHEBI_ | Chemical Entities of Biological Interest |
| EDAM:      | http://edamontology.org/ | The ontology of data analysis and management |
| IAO:       | http://purl.org/ontology/IAO_ | Information Artifact Ontology |
| fabio:     | http://purl.org/spar/fabio/ | FaBiO, the FRBR-aligned Bibliographic Ontology |
| dcterms:   | http://purl.org/dc/terms/ | DCMI Metadata Terms |
| NCIt:      | http://purl.obolibrary.org/obo/NCIT_ | NCI Thesaurus OBO Edition |
| OBI:       | http://purl.obolibrary.org/obo/OBI_ | Ontology for Biomedical Investigations |
| owl:       | http://www.w3.org/2002/07/owl# | The OWL 2 Schema vocabulary  |
| rdf:       | http://www.w3.org/1999/02/22-rdf-syntax-ns# | The RDF Concepts Vocabulary |
| rdfs:      | http://www.w3.org/2000/01/rdf-schema# | The RDF Schema vocabulary |
| schema:    | https://schema.org/ | Schemas for structured data on the Internet |
| skos:      | http://www.w3.org/2004/02/skos/core# | Simple Knowledge Organization System |
| wd:        | http://www.wikidata.org/entity/ | Wikidata entities |









