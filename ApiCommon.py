import datetime
import os
import re

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
def is_valid_url(url):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # loose validation, enough for virtuoso to accept it as a 
    # valid IRI or URL when it is wrapped in < >
    for ch in ["<", ">", "\""]:
        if ch in url: return False
    return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def is_valid_url_strict(url):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # UNUSED
    # many URLs are invalid according to this function based on W3 specs
    # in practice, most of invalid URLs detected here are accepted by virtuoso and work when used in a browser
    url_regex = re.compile(r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$')
    return bool(url_regex.match(url))


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
    
    
