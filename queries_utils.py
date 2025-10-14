from api_platform import ApiPlatform
from namespace_registry import NamespaceRegistry
from sparql_client import EndpointClient
from optparse import OptionParser
import sys



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Query:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.id = None
        self.label = None
        self.keywords = list()
        self.prefixes = list()
        self.sparql = list()
        self.services = list()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __str__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = list()
        lines.append(f"Query({self.id},")
        lines.append(f"  {self.label},")
        lines.append(f"  {self.keywords},")
        for line in self.sparql:
            lines.append("  " + line)
        lines.append(")")
        return "\n".join(lines)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_prefixed_sparql(self, ns_reg: NamespaceRegistry):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        lines = []
        q.set_necessary_sparql_prefixes(ns_reg)
        for pfx in self.prefixes: lines.append(pfx) 
        for spa in self.sparql:   lines.append(spa)       
        return "\n".join(lines)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def set_necessary_sparql_prefixes(self, ns_reg: NamespaceRegistry):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.prefixed = list()
        for ns in ns_reg.namespaces:
            pattern = f"{ns.pfx}:"
            for sparql_line in self.sparql:
                if pattern in sparql_line:
                    self.prefixes.append(f"PREFIX {ns.pfx}: <{ns.url}>")
                    break



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_ttl_for_sparql_endpoint(self, ns_reg: NamespaceRegistry):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        #
        # Output example:
        # cello:Query_002 a sh:SPARQLExecutable ;
        # rdfs:comment "Count of publication citations" ; 
        # sh:select "select (count(*) as ?cnt) where { ?cl rdf:type / rdfs:subClassOf cello:Publication . }" ; 
        # .
        #
        lines = list()
        sparql_endpoint = ns_reg.platform.get_public_sparql_service_IRI()
        lines.append(f"cello:Query_{self.id} a sh:SPARQLExecutable, sh:SPARQLSelectExecutable ;")
        lines.append(f"    sh:prefixes _:sparql_examples_prefixes ;")
        lines.append(f"    rdfs:comment \"\"\"{self.label}\"\"\"@en ; ")
        quoted_list = list()
        for k in self.keywords: quoted_list.append("".join(["\"", k, "\""]))
        quoted_keywords = " , ".join(quoted_list)
        lines.append(f"    schema:keywords {quoted_keywords} ; ")
        lines.append(f"    schema:target <{sparql_endpoint}> ; ")
        for s in self.services:
            lines.append(f"    spex:federatesWith <{s}> ;")
        lines.append(f"    sh:select \"\"\"")
        self.set_necessary_sparql_prefixes(ns_reg)
        for line in self.prefixes: lines.append(f"{line}")
        for line in self.sparql: lines.append(f"{line}")
        lines.append(f"    \"\"\"")
        lines.append(f"    .")
        return "\n".join(lines)




    def get_ttl_for_github():
        pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class QueryFileReader:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
        f_in = open("./queries/query-list.txt", "r")
        isFirstId = True
        query: Query = Query()
        self.query_list = list[Query]()
        while True:
            line = f_in.readline()
            if line == '': break
            line = line.rstrip()
            if line == '': continue
            if line.startswith("##"): continue
            if line.startswith("ID: "):
                if not isFirstId: self.query_list.append(query)
                query = Query()
                query.id = line[4:].lstrip()
                isFirstId = False
            elif line.startswith("LB: "):
                query.label = line[4:].lstrip()
            elif line.startswith("KW: "):
                for k in line[4:].lstrip().split(","):
                    query.keywords.append(k.strip())
            else:
                query.sparql.append(line)
                if "service" in line.lower():
                    p1 = line.index("<")
                    p2 = line.index(">")
                    service =line[p1+1:p2]
                    query.services.append(service)

        self.query_list.append(query)
        f_in.close()


#-------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------

    optparser = OptionParser(usage="python queries_utils.py [--crlf] sparql_service_url")
    optparser.add_option("-c", "--crlf",
        action="store_true", dest="with_crlf", default=False,
        help="When set, output file line sep is CR/LF instead of LF")
    (options, args) = optparser.parse_args()
    with_crlf = options.with_crlf
    if len(args) != 1:
        print("ERROR, usage is: python queries_utils.py [--crlf] sparql_service_url")    
        sys.exit(1)

    sparql_service = args[0]
    platform = ApiPlatform("prod")
    ns_reg = NamespaceRegistry(platform)
    client = EndpointClient(server_url=sparql_service, ns_reg=ns_reg)

    reader = QueryFileReader()

    for q in reader.query_list:
        descr = q.get_ttl_for_sparql_endpoint(ns_reg)
        print(f"\n-------- Query id {q.id} --------\n")
        print(descr)

    sys.exit()
    sep = "\t"
    elems = ["status", "rows", "t[s]", "id", "label"]
    print(sep.join(elems))
    for q in reader.query_list:
        sparql_lines = q.get_prefixed_sparql(ns_reg)
        response = client.run_query(sparql_lines)
        rows = response.get("rows") or 0
        duration = response.get("duration") or 0.0
        status = "OK" if response.get("success") else "ER"
        elems = [status, str(rows), str(duration), q.id, q.label]
        print(sep.join(elems))
    print("end")
    