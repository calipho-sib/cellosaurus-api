import sys
from api_platform import ApiPlatform
from namespace_registry import NamespaceRegistry
from sparql_client import EndpointClient
from ApiCommon import log_it
import json


#-------------------------------------------------
class DataModelBuilder:
#-------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, platform: ApiPlatform):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.platform = platform
        self.ns = NamespaceRegistry(platform)
        self.url2pfx = dict()
        for space in self.ns.namespaces:
            self.url2pfx[space.url] = space.pfx
        self.client = EndpointClient(platform.get_builder_sparql_service_IRI(), self.ns)
        self.model_query = """
            select ?subject_class ?property ?object_type (count(*) as ?triple_count) where {
            GRAPH <https://www.cellosaurus.org/rdf/graphs/main> {
                ?s ?property ?o .
                ?s a ?subject_class .
                optional {?o a ?o_class }
                bind(coalesce(?o_class, datatype(?o), 'IRI') as ?object_type)
            }}
            group by ?subject_class ?property ?object_type
            order by ?subject_class ?property ?object_type
        """

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def apply_prefixes(self, iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for url in self.url2pfx:
            if iri.startswith(url):
                pfx = self.url2pfx[url]
                id = iri[len(url):]
                return ":".join([pfx, id ])
        return iri


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def retrieve_and_save_model(self, jsonfile):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        response = self.client.run_query(self.model_query)
        if not response.get("success"):
            log_it("ERROR", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        typical_triples = list()
        for row in rows:
            triple = dict()
            triple["subject_class"] = self.apply_prefixes(row["subject_class"]["value"])
            triple["property"] = self.apply_prefixes(row["property"]["value"])
            triple["object_type"] = self.apply_prefixes(row["object_type"]["value"])
            triple["triple_count"] = int(row["triple_count"]["value"])
            typical_triples.append( triple )
        data = { "model" : typical_triples }
        f_out = open(jsonfile, "w", encoding="utf-8")
        json.dump(data, f_out, indent=2, ensure_ascii=False)
        f_out.close()


#-------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------
    builder = DataModelBuilder(ApiPlatform("prod"))
    builder.retrieve_and_save_model("test.json")
