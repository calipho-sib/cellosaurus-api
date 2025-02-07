import datetime
import os

SERIAL_DIR = "./serial/"

RI_FILE = SERIAL_DIR + "ri.bin"
CL_IDX_FILE = SERIAL_DIR + "cl-idx.bin"
CL_XML_FILE = SERIAL_DIR + "cl-xml.bin"
CL_JSO_FILE = SERIAL_DIR + "cl-jso.bin"
CL_TXT_FILE = SERIAL_DIR + "cl-txt.bin"

RF_IDX_FILE = SERIAL_DIR + "rf-idx.bin"
RF_XML_FILE = SERIAL_DIR + "rf-xml.bin"
RF_JSO_FILE = SERIAL_DIR + "rf-jso.bin"
RF_TXT_FILE = SERIAL_DIR + "rf-txt.bin"

FLDDEF_FILE = "./fields_def.txt"

# used in main.py and in fields_utils.py
CELLAPI_VERSION="1.0.4"

platform_key = "local"
#platform_key = "test"
#platform_key = "prod"

platform_dict = {
    # ---------------------------------
    # WARNING: no final "/", please !
    # ---------------------------------
    "local": {
        "base_IRI": "http://localhost/rdf",
        #"help_IRI": "http://localhost:8082/static/sparql/doc",     # http://localhost:8082/static/sparql/doc/ontology.ttl 
        "help_IRI": "http://localhost:8082",                        # http://localhost:8082/ontology.ttl thanks to main.app.mount())
        "sparql_IRI": "http://localhost/sparql/service"
    },
    "test": {
        "base_IRI": "https://www.mix-id1.cellosaurus.org/rdf",
        #"help_IRI": "https://test-sparql.cellosaurus.org/sparql/doc",
        "help_IRI": "https://test-api.cellosaurus.org",
        "sparql_IRI": "https://test-sparql.cellosaurus.org/sparql"
    },
    "prod": {
        "base_IRI": "https://purl.expasy.org/cellosaurus/rdf",
        "help_IRI": "https://api.cellosaurus.org",
        "sparql_IRI": "https://sparql.cellosaurus.org/sparql"
        #"sparql_IRI": "https://sparql.cellosaurus.org/sparql/service"
    }
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def split_string(text, max_length=80):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    result = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind(' ')
        if split_index == -1:
            # If no space found, split at max_length
            split_index = max_length
        result.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        result.append(text)
    return result


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


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_rdf_graph_IRI():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # no final "/", please !
    # CAREFUL if you change this:
    # to be sync'ed with ./scripts/load_ttl_files.sh
    return "https://www.cellosaurus.org/rdf/graphs/main"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_onto_preferred_prefix():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # used as a descripor of the ontology in its ttl file
    return "cello"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_rdf_base_IRI():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # used as a base for all IRIs for cello, xref, 
    # org and cvcl namespaces  
    return platform_dict[platform_key]["base_IRI"]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_help_base_IRI():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # used as a base for all IRIs for cello, xref, 
    # org and cvcl namespaces  
    return platform_dict[platform_key]["help_IRI"]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_sparql_service_IRI():
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # it is the public URL of the sparql service !!!
    # not the sparql page path !
    # used on building sparql-editor related pages
    return platform_dict[platform_key]["sparql_IRI"]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def check_structure_IRI(iri):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    for ch in ["<", ">", "\""]:
        if ch in iri: return False
    return True

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_properties(env):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    props = dict()
    prop_file='cellapi_httpserver.config.' + env
    f_in = open(prop_file, 'r')
    while True:
        line = f_in.readline()
        if line == '': break
        if line[0:1] == '#' : continue
        if '=' in line:
            nv = line.split('=')
            name = nv[0].strip()
            # the value may contain "=" as well
            value = '='.join(nv[1:])
            value = value.strip()
            props[name]=value
    f_in.close()
    return props

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_search_result_txt_header_as_lines(meta):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    lines = list()
    for k in meta["query"]: 
        value = meta["query"][k]
        if not isinstance(value,str): value = str(value)
        lines.append("##   query." + k + ": " + value)
    value =  meta["fields"]
    if isinstance(value,list): value = ",".join(value)
    elif value is None: value = "(None)"
    lines.append("##   query.fields: " + value)
    lines.append("##   query.format: "  + meta["format"])
    lines.append("##   QTime: "  + str(meta["QTime"]))
    lines.append("##   response.numFound: " + str(meta["numFound"]) )
    lines.append("\n")
    return lines


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_search_result_txt_header(meta):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    return "\n".join(get_search_result_txt_header_as_lines(meta))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def get_format_from_headers(headers):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    value_str = None
    for k in headers.keys():
        if k.lower() == "accept":
            value_str = headers.get(k)
            break
    if value_str is None: return None

    value_list = value_str.split(",")
    for item in value_list:
        value = item.split(";")[0].strip()   # we don't care of the q value
        if value == "application/json": return "json"    
        elif value == "application/xml": return "xml"
        elif value == "text/plain": return "txt"
        elif value == "text/tab-separated-values": return "tsv"

        elif value == "text/html": return "html"                 # for RDF description of entities, see enum RdfFormat
        elif value == "text/turtle": return "ttl"                # for RDF description of entities, see enum RdfFormat
        elif value == "application/rdf+xml": return "rdf"        # for RDF description of entities, see enum RdfFormat
        elif value == "application/n-triples": return "n3"       # for RDF description of entities, see enum RdfFormat
        elif value == "application/ld+json": return "jsonld"     # for RDF description of entities, see enum RdfFormat

    return None
    
    
