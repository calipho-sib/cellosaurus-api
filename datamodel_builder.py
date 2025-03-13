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


        self.class_def_query = """
            # CAUTION: we remove subjects that are blank nodes !

            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            select * where {
            {   select distinct ?subj where {
                values ?kind { owl:Class }
                ?subj a ?kind .
                filter (! strstarts(str(?subj), str(owl:)) && ! isBlank(?subj))
                }
            }
            ?subj ?prop ?obj .
            }
            order by ?subj ?prop ?obj
        """
        
        self.prop_def_query = """
            # CAUTION: blank nodes in range & domain objects

            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            select ?subj ?prop ?obj where {
                {   select distinct ?subj where {
                    values ?kind { rdf:Property owl:DatatypeProperty owl:ObjectProperty owl:AnnotationProperty owl:OntologyProperty }
                    ?subj a ?kind .
                    filter (! strstarts(str(?subj), str(owl:)) && ! strstarts(str(?subj), str(rdfs:)))
                    }
                }
                ?subj ?prop ?obj .
            }
            order by ?subj ?prop ?obj        
        """

        self.class_use_query = """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select ?subject_class ?property ?object_type (count(*) as ?triple_count) where {
            values ?subject_class { <$class_long_IRI> }
            ?s a ?subject_class .
            ?s ?property ?o .
            optional {?o a ?o_class }
            bind(coalesce(?o_class, datatype(?o), xsd:anyURI) as ?object_type)
            }
            group by ?subject_class ?property ?object_type
            order by ?subject_class ?property ?object_type        
        """

        self.prop_use_query = """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select ?property ?tag ?node_type (count(*) as ?triple_count) where {
            values ?property { <$prop_long_IRI> }
            {
                ?_ ?property ?o .
                optional {?o a ?o_class }
                bind(coalesce(?o_class, datatype(?o), xsd:anyURI) as ?node_type)
                bind('range' as ?tag)
            } union {
                ?s ?property ?_ .
                optional {?s a ?s_class }
                bind(coalesce(?s_class, datatype(?s), xsd:anyURI) as ?node_type)
                bind('domain' as ?tag)
            } union {
                ?_s ?property ?_o .
                bind(xsd:integer as ?node_type)
                bind('count' as ?tag)
            }
            }
            group by ?property ?tag ?node_type
            order by ?property ?tag ?node_type
        """

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_short_IRI(self, long_iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for url in self.url2pfx:
            if long_iri.startswith(url):
                pfx = self.url2pfx[url]
                id = long_iri[len(url):]
                return ":".join([pfx, id ])
        return long_iri


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_long_IRI(self, prefixed_iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        pfx, id = prefixed_iri.split(":")
        url = self.ns.pfx2ns[pfx].url
        return "".join([url, id])



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def load_use_for_prop_entities(self, entities):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for entity_key in entities:
            entity = entities[entity_key]
            if entity["tag"] != "prop" : continue
            long_IRI = self.get_long_IRI(entity_key)
            query = self.prop_use_query.replace("$prop_long_IRI", long_IRI)
            log_it("INFO", f"querying for usage of {entity_key}")
            response = self.client.run_query(query)
            if not response.get("success"):
                log_it(f"ERROR while running query for usage of entitites prop", response.get("error_type"))
                log_it(response.get("error_msg"))
                sys.exit(2)
            rows = response.get("results").get("bindings")
            for row in rows:            
                prop = self.get_short_IRI(row["property"]["value"])
                tag = self.get_short_IRI(row["tag"]["value"])
                node_type = self.get_short_IRI(row["node_type"]["value"])
                count = row["triple_count"]["value"]
                if tag == "count": entities[prop]["count"] = int(count)
                statement = " | ".join([prop, tag, node_type, count])
                entities[prop]["usage"].append(statement)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def load_use_for_class_entities(self, entities):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for entity_key in entities:
            entity = entities[entity_key]
            if entity["tag"] != "class" : continue
            long_IRI = self.get_long_IRI(entity_key)
            query = self.class_use_query.replace("$class_long_IRI", long_IRI)
            log_it("INFO", f"querying for usage of {entity_key}")
            response = self.client.run_query(query)
            if not response.get("success"):
                log_it(f"ERROR while running query for usage of entitites class", response.get("error_type"))
                log_it(response.get("error_msg"))
                sys.exit(2)
            rows = response.get("results").get("bindings")
            for row in rows:            
                count = row["triple_count"]["value"]
                subj = self.get_short_IRI(row["subject_class"]["value"])
                prop = self.get_short_IRI(row["property"]["value"])
                obj = self.get_short_IRI(row["object_type"]["value"])
                if prop == "rdf:type" and subj == entity_key: entities[subj]["count"] = int(count)
                statement = " | ".join([subj, prop, obj, count])
                entities[subj]["usage"].append(statement)
                if obj in entities:
                    statement = " | ".join([subj, prop, obj, count])
                    entities[obj]["usage"].append(statement)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def load_def_for_entities(self, query, tag, entities):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        response = self.client.run_query(query)
        if not response.get("success"):
            log_it(f"ERROR while running query for definition of entities {tag}", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        relations = list()
        for row in rows:            
            subj = self.get_short_IRI(row["subj"]["value"])
            prop = self.get_short_IRI(row["prop"]["value"])
            obj = self.get_short_IRI(row["obj"]["value"])
            relations.append( { "subj": subj, "prop": prop, "obj": obj } )
            if subj not in entities: entities[subj] = { "tag": tag , "count": 0, "definition": list(), "usage" : list() }
        for rel in relations:
            subj = rel["subj"]
            prop = rel["prop"]
            obj = rel["obj"]
            statement = " | ".join([subj, prop, obj])
            entities[subj]["definition"].append(statement)
            if obj in entities:
                statement = " | ".join([subj, prop, obj])
                entities[obj]["definition"].append(statement)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def retrieve_and_save_model(self, jsonfile):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        entities = dict()
        
        self.load_def_for_entities(self.class_def_query, "class", entities)
        self.load_def_for_entities(self.prop_def_query, "prop", entities)
        self.load_use_for_class_entities(entities)
        self.load_use_for_prop_entities(entities)

        data = dict()
        data["entities"] = entities
        f_out = open(jsonfile, "w", encoding="utf-8")
        json.dump(data, f_out, indent=2, ensure_ascii=False)
        f_out.close()



#-------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------
    builder = DataModelBuilder(ApiPlatform("prod"))
    builder.retrieve_and_save_model("test.json")
