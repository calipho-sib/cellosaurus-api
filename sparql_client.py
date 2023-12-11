from SPARQLWrapper import SPARQLWrapper, JSON
import json
import sys
import datetime
from namespace import NamespaceRegistry as ns_reg

# see https://github.com/RDFLib/sparqlwrapper/tree/master


class EndpointClient:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, server_url):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.server_url = server_url
        self.endpoint = SPARQLWrapper(server_url)
        self.prefixes = dict()
        for ns in ns_reg.namespaces:
            self.prefixes[ns.prefix() + ":"] = ns.baseurl()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_graph_stats(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        query = """
            SELECT ?graph (COUNT(*) as ?tripleCount)
            WHERE { GRAPH ?graph { ?s ?p ?o } }
            GROUP BY ?graph
        """
        return self.run_query(query)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def query_from_file(self, file_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        with open(file_name,"r") as f: query = f.read()
        response = self.run_query(query)
        response["query_file"] = file_name 
        return response
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term_query(self, pattern, flags=""):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        elems = list()            
        elems.append("select ?c as ?concept_IRI ?label_prop (str(?lbl) as ?lbl) where {")
        if "a" in flags: 
            elems.append("  values ?label_prop { skos:prefLabel skos:altLabel } .")
        else:
            elems.append("  values ?label_prop { skos:prefLabel } .")

        elems.append("  ?c a skos:Concept .")
        elems.append("  ?c ?label_prop ?lbl .")
        if "r" in flags:
            if "i" in flags:
                elems.append(f"""  FILTER (regex(str(?lbl), "(?i){pattern}", "i")) """)
            else:
                elems.append(f"""  FILTER (regex(str(?lbl), "{pattern}")) """)
        else:
            if "i" in flags:
                pattern = pattern.lower()
                elems.append(f"""  FILTER (lcase(str(?lbl)) = "{pattern}") """)
            else:
                elems.append(f"""  FILTER (?lbl = "{pattern}"^^xsd:string) """)
        elems.append("}")
        elems.append("limit 10000")
        query = "\n".join(elems)
        print(query)
        return query


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term_parent_query(self, concept_id, path_modifier):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        elems = list()
        for ns in ns_reg.namespaces: elems.append(ns.getSparqlPrefixDeclaration())
        elems.append("select ?term_IRI (str(?t_lbl) as ?term_lbl) ?parent_IRI (str(?p_lbl) as ?parent_lbl) where {")
        elems.append("  values ?term_IRI { sibilc:" + concept_id + " } .")
        if path_modifier is None:
            modifier = ""
        elif path_modifier in "*+?":
            modifier = path_modifier
        else:
            modifier = "{" + path_modifier + "}"

        elems.append("  ?term_IRI :more_specific_than" + modifier + " ?parent_IRI .")
        elems.append("  ?parent_IRI skos:prefLabel ?p_lbl .")
        elems.append("  ?term_IRI skos:prefLabel ?t_lbl .")
        elems.append("}")
        elems.append("limit 100")
        query = "\n".join(elems)
        print(query)
        return query

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def term_children_query(self, concept_id, path_modifier):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        elems = list()
        for ns in ns_reg.namespaces: elems.append(ns.getSparqlPrefixDeclaration())
        elems.append("select ?term_IRI (str(?t_lbl) as ?term_lbl) ?child_IRI (str(?c_lbl) as ?child_lbl) where {")
        elems.append("  values ?term_IRI { sibilc:" + concept_id + " } .")
        if path_modifier is None:
            modifier = ""
        elif path_modifier in "*+?":
            modifier = path_modifier
        else:
            modifier = "{" + path_modifier + "}"
        elems.append("  ?child_IRI :more_specific_than" + modifier + " ?term_IRI .")
        elems.append("  ?child_IRI skos:prefLabel ?c_lbl .")
        elems.append("  ?term_IRI skos:prefLabel ?t_lbl .")
        elems.append("}")
        elems.append("limit 100")
        query = "\n".join(elems)
        print(query)
        return query


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
 
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def apply_prefixes(self, uri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for (k,v) in self.prefixes.items():
            if colval.startswith(v):
                return k + colval[(len(v)):]
        return uri

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def show_usage_and_die(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        print("\nUsage is:\n\n")
        print("python " + sys.argv[0] + " prefixes")
        print("python " + sys.argv[0] + " query <sparql_query_file_name>")
        print("python " + sys.argv[0] + " term <pattern> [flags]")
        print("python " + sys.argv[0] + " parents_of <concept_id> <path_modifier>")
        print("python " + sys.argv[0] + " children_of <concept_id> <path_modifier>")
        print("\nwith:\n")
        print("pattern       : regex pattern with/without special chars like ^$.*")
        print("flags         : optional, i.e: air")
        print("  a : also search alternative labels")
        print("  i : case insensitive")
        print("  r : regex syntax activated")
        print("concept_id    : i.e: MESH_D018884")
        print("path_modifier : optional, parent relation level(s), i.e:")
        print("  ,3  : parents connected through a chain of up to 3 links")
        print("  2,4 : parents connected through a chain of 2 to 4 links")
        print("  '*' : parents connected through a chain of any length (incl. length=0)")
        print("  ?   : parents connected through a single link or none")
        print("  +   : parents connected through a chain of one link or more")
        print("\n")
        sys.exit(1)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
if __name__ == '__main__' :
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

    client = EndpointClient("http://localhost:8890/sparql")


    if len(sys.argv) < 2: client.show_usage_and_die()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    if sys.argv[1]== "prefixes":
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for ns in ns_reg.namespaces: 
            print(ns.getSparqlPrefixDeclaration())
        sys.exit()

    if len(sys.argv) < 2: client.show_usage_and_die()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    if sys.argv[1]== "term":
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        pattern = sys.argv[2]
        flags = sys.argv[3] if len(sys.argv)>3 else ""
        query = client.term_query(pattern, flags)
        response = client.run_query(query)
        response["query_template"] = "term query"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    elif sys.argv[1]== "parents_of":
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        concept_id = sys.argv[2]
        path_modifier = sys.argv[3] if len(sys.argv) > 3 else None
        query = client.term_parent_query(concept_id, path_modifier)
        response = client.run_query(query)
        response["query_template"] = "parents of term query"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    elif sys.argv[1]== "children_of":
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        concept_id = sys.argv[2]
        path_modifier = sys.argv[3] if len(sys.argv) > 3 else None
        query = client.term_children_query(concept_id, path_modifier)
        response = client.run_query(query)
        response["query_template"] = "parents of term query"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    elif sys.argv[1]=="query":
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        query_file_name = sys.argv[2]
        response = client.query_from_file(query_file_name)



    if response.get("success"):

        col_names = response.get("head").get("vars")
        print("HEAD\t" + "\t".join(col_names))
        rows = response.get("results").get("bindings")
        for row in rows:
            cols = list()
            for cn in col_names:
                col = row.get(cn)
                colval = col.get("value")
                if col.get("type") == "uri": colval = client.apply_prefixes(colval)
                cols.append(colval)
            print("ROWS\t" +"\t".join(cols))
        
    else:
        print("ERROR", response.get("error_type"))
        print(response.get("error_msg"))
    
    print("META\tquery_file\t", response.get("query_file"))
    print("META\tquery_template\t", response.get("query_template"))
    print("META\tsuccess\t", response.get("success"))
    print("META\tduration[s]\t", response.get("duration"))
    print("META\tcount\t", response.get("rows"))
    print("END")