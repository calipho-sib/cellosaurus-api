The Cellosaurus is a comprehensive knowledge resource on cell lines used in biomedical research, encompassing both vertebrate and invertebrate species. It provides detailed information for over 140,000 cell lines, including recommended names, synonyms, unique accession numbers, species of origin, and structured comments. The database contains crucial details such as contamination status, genetic modifications, disease associations, STR profiles, and cell line categorization.

Delivering a RDF version of the Cellosaurus is an important step towards FAIRification and making it available from our [SPARQL endpoint]($public_sparql_URL) is key to Linked Open Data (LOD) perspective and for improving interoperability in particular thanks to federated queries.

The OWL Cellosaurus ontology was developed to serve as the semantic model for all the diverse information contained in the Cellosaurus  RDF.
Two key principles guided its construction:

  * Anchorage and reuse. A common vocabulary is essential for RDF to allow good interoperability so reusing terms defined in standard ontologies was a priority.
  * Practicalities. Readability and documentation are important for us humans. Local equivalent classes and / or properties with human readable IRIs or subproperties with documented domains and ranges were defined in order to take advantage of the [SPARQL-editor](/sparql-editor) (autocompletion functionality) and of the [widoco](https://github.com/dgarijo/Widoco) documentation tool which generated this page.

The [EMBL-EBI Ontology Lookup Service](https://www.ebi.ac.uk/ols4/) (OLS) was the main tool used to search for existing terms relevant to our ontology.

In addition to their formal OWL definition, some of our classes and properties are also described using the SKOS ontology. It adds some very informative links between our concepts and those from other ontologies for both humans and search algorithms. The SKOS links when available also appear in this widoco documentation in the _has relation_ section of the terms.
