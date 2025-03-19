import os
import sys
import datetime
from optparse import OptionParser
import json
from SPARQLWrapper import SPARQLWrapper, JSON


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def log_it(*things, duration_since=None):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    t1 = datetime.datetime.now()
    now = t1.isoformat().replace('T',' ')[:23]
    pid = "[" + str(os.getpid()) + "]"
    if duration_since is not None:
        duration = round((t1 - duration_since).total_seconds(),3)
        print(now, pid, *things, "duration", duration, flush=True)
    else:
        print(now, pid, *things, flush=True)



#-------------------------------------------------
class EndpointClient:
#-------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, server_url):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.server_url = server_url
        self.endpoint = SPARQLWrapper(server_url)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def run_query(self, query):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        t0 = datetime.datetime.now()
        try:
            self.endpoint.setQuery(query)
            self.endpoint.setMethod("POST")
            self.endpoint.setReturnFormat(JSON)
            response = self.endpoint.query().convert()
            duration = round((datetime.datetime.now()-t0).total_seconds(),3)
            response["duration"] = duration
            response["rows"] = len(response.get("results").get("bindings"))
            response["success"] = True
            return response
        except Exception as e:
            typ, msg, _ = sys.exc_info()
            duration = round((datetime.datetime.now()-t0).total_seconds(),3)
            return {"success" : False, "duration" : duration, "rows": 0, "error_type": typ.__name__, "error_msg": str(msg).replace('\\n','\n')}



#-------------------------------------------------
class DataModelBuilder:
#-------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, sparql_service):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.url2pfx = dict()
        self.pfx2url = dict()
        self.client = EndpointClient(sparql_service)

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

        self.prefix_query ="""
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            select ?pfx ?url where {
            ?onto a owl:Ontology .
            ?onto sh:declare ?declaration .
            ?declaration sh:prefix ?pfx; sh:namespace ?url.
            }
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
        url = self.pfx2url[pfx]
        return "".join([url, id])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def load_prefixes(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        response = self.client.run_query(self.prefix_query)
        if not response.get("success"):
            log_it(f"ERROR while running query for getting prefixes {tag}", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        for row in rows:            
            pfx = self.get_short_IRI(row["pfx"]["value"])
            url = self.get_short_IRI(row["url"]["value"])
            self.pfx2url[pfx] = url
            self.url2pfx[url] = pfx

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

        self.load_prefixes()
        self.load_def_for_entities(self.class_def_query, "class", entities)
        self.load_def_for_entities(self.prop_def_query, "prop", entities)
        self.load_use_for_class_entities(entities)
        self.load_use_for_prop_entities(entities)

        data = dict()
        data["entities"] = entities
        data["pfx2url"] = self.pfx2url
        f_out = open(jsonfile, "w", encoding="utf-8")
        json.dump(data, f_out, indent=2, ensure_ascii=False)
        f_out.close()



#-------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------
    optparser = OptionParser(usage="python datamodel_builder.py [--crlf] sparql_service_url output_file")
    optparser.add_option("-c", "--crlf",
        action="store_true", dest="with_crlf", default=False,
        help="When set, output file line sep is CR/LF instead of LF")
    (options, args) = optparser.parse_args()
    with_crlf = options.with_crlf
    if len(args) != 2:
        print("ERROR, usage is: python datamodel_builder.py [--crlf] sparql_service_url output_file")    
        sys.exit(1)

    builder = DataModelBuilder(sparql_service=args[0])
    builder.retrieve_and_save_model(jsonfile=args[1])

