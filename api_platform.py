from ApiCommon import log_it

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class PlatformError(Exception): 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    pass

# - - - - - - - - - - - - - - - - - - - - - - - - 
class ApiPlatform:
# - - - - - - - - - - - - - - - - - - - - - - - - 


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, key):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        # the value of platform_key must be set from elsewhere:
        # - in main.py by reading ENV variable
        # - in cellapi_builder.py by a script argument
        # expected values are: local, test, prod
        if key.lower() not in ["local", "test", "prod"]: raise PlatformError(f"Invalid platform key: {key}")

        self.platform_key = key.lower()

        self.platform_dict = {
            # ---------------------------------
            # WARNING: no final "/", please !
            # ---------------------------------
            "local": {
                "base_IRI": "http://localhost/rdf",
                "help_IRI": "http://localhost:8082",                        # http://localhost:8082/ontology.ttl thanks to main.app.mount())
                "public_sparql_IRI": "http://localhost/sparql/service",
                "private_sparql_IRI" : "http://localhost:8890/sparql",
                "builder_sparql_IRI" : "http://localhost:8890/sparql"     
            },
            "test": {
                "base_IRI": "https://www.mix-id1.cellosaurus.org/rdf",
                "help_IRI": "https://test-api.cellosaurus.org",
                "public_sparql_IRI": "https://test-sparql.cellosaurus.org/sparql",
                "private_sparql_IRI" : "http://localhost:8890/sparql",
                "builder_sparql_IRI" : "http://localhost:8890/sparql"
            },
            "prod": {
                "base_IRI": "https://purl.expasy.org/cellosaurus/rdf",
                "help_IRI": "https://api.cellosaurus.org",
                "public_sparql_IRI": "https://sparql.cellosaurus.org/sparql",
                "private_sparql_IRI" : "http://localhost:8890/sparql",
                "builder_sparql_IRI" : "http://localhost:8890/sparql"
            }
        }


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_rdf_graph_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # no final "/", please !
        # CAREFUL if you change this:
        # to be sync'ed with ./scripts/load_ttl_files.sh
        return "https://www.cellosaurus.org/rdf/graphs/main"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_onto_preferred_prefix(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # used as a descripor of the ontology in its ttl file
        return "cello"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_rdf_base_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # used as a base for all IRIs for cello, xref, 
        # org and cvcl namespaces  
        return self.platform_dict[self.platform_key]["base_IRI"]


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_help_base_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # used as a base for all IRIs for cello, xref, 
        # org and cvcl namespaces  
        return self.platform_dict[self.platform_key]["help_IRI"]


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_builder_sparql_service_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # it is the URL of the sparql service used during ontology building
        # for determining term domains and ranges !!!
        # used on building sparql-editor related pages
        return self.platform_dict[self.platform_key]["builder_sparql_IRI"]


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_public_sparql_service_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # it is the public URL of the sparql service !!!
        # used on building sparql-editor related pages
        return self.platform_dict[self.platform_key]["public_sparql_IRI"]


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_private_sparql_service_IRI(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # it is the private URL of the sparql service !!!
        # internal use for API only
        return self.platform_dict[self.platform_key]["private_sparql_IRI"]


