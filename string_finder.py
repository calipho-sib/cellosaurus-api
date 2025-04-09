import os
import sys
import datetime
from optparse import OptionParser
from SPARQLWrapper import SPARQLWrapper, JSON
from lxml import etree


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
class StringFinder:
#-------------------------------------------------

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self, sparql_service):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        self.url2pfx = dict()
        self.pfx2url = dict()
        self.client = EndpointClient(sparql_service)

        self.get_props_query = """
            select distinct ?prop where { ?s ?prop ?o . }
        """

        self.check_string_range_query = """
            select ?s ?prop ?datatype ?example where {
            values ?prop { $prop_iri }
            ?s ?prop ?example .
            bind(datatype(?example) as ?datatype)
            }
            limit 1
        """
        
        self.get_classes_in_domain_query = """
            select distinct ?classInDomain where {
            values ?prop { $prop_iri }
            ?s ?prop ?_ .
            ?s a ?classInDomain .
            }
        """

        self.get_strings_query = """
            select  ?classInDomain ?instance ?prop ?value where {
            values ( ?classInDomain ?prop ) { ( $class_iri $prop_iri ) }
            ?instance a ?classInDomain .
            ?instance ?prop ?value .
            }
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
            log_it(f"ERROR while running query for getting prefixes", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        for row in rows:            
            pfx = self.get_short_IRI(row["pfx"]["value"])
            url = self.get_short_IRI(row["url"]["value"])
            self.pfx2url[pfx] = url
            self.url2pfx[url] = pfx


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_detailed_records(self, prop_iri, class_iri, limit=None):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if prop_iri.startswith("http"): return [] # we skip props for which we have no prefix
        prop_long_iri = "".join([ "<", self.get_long_IRI(prop_iri), ">" ])
        class_long_iri = "".join([ "<", self.get_long_IRI(class_iri), ">" ])
        query = self.get_strings_query.replace("$prop_iri", prop_long_iri).replace("$class_iri", class_long_iri)
        if limit is not None: query += "\nLIMIT " + str(limit)
        response = self.client.run_query(query)
        if not response.get("success"):
            log_it(f"ERROR while running query to get detailed record for class {class_iri} and property {prop_iri}", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        records = list()
        for row in rows:
            instance_iri = self.get_short_IRI(row["instance"]["value"])
            str_value = row["value"]["value"]
            records.append(" || ".join([class_iri, instance_iri, prop_iri, str_value]))
        return records


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_classes_in_domain(self, prop_iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if prop_iri.startswith("http"): return [] # we skip props for which we have no prefix

        prop_long_iri = "".join([ "<", self.get_long_IRI(prop_iri), ">" ])
        query = self.get_classes_in_domain_query.replace("$prop_iri", prop_long_iri)
        response = self.client.run_query(query)
        if not response.get("success"):
            log_it(f"ERROR while running query to get classes in domain of property {prop_iri}", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        classes = list()
        for row in rows:
            classes.append(self.get_short_IRI(row["classInDomain"]["value"]))
        return classes

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def has_string_range(self, prop_iri):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if prop_iri.startswith("http"): return False # we skip props for which we have no prefix

        prop_long_iri = "".join([ "<", self.get_long_IRI(prop_iri), ">" ])
        query = self.check_string_range_query.replace("$prop_iri", prop_long_iri)
        response = self.client.run_query(query)
        if not response.get("success"):
            log_it(f"ERROR while running query to check range of property {prop_iri}", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        if len(rows)==0: return False
        dt_var = rows[0].get("datatype") # NOTE: can be unbound !
        if dt_var is None: return False 
        dt_value = self.get_short_IRI(dt_var["value"])
        return dt_value == "xsd:string"


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_props(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        props = list()
        query = self.get_props_query        
        log_it("INFO", f"querying to get property list")
        response = self.client.run_query(query)
        if not response.get("success"):
            log_it(f"ERROR while running query for getting property list", response.get("error_type"))
            log_it(response.get("error_msg"))
            sys.exit(2)
        rows = response.get("results").get("bindings")
        for row in rows:            
            prop = self.get_short_IRI(row["prop"]["value"])
            props.append(prop)
        return props


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def get_solr_doc(self, record, id):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        (cl, inst, prop, label) = record.split(" || ")
        doc_node = etree.Element("doc")
        
        fld = etree.SubElement(doc_node, "field")
        fld.set("name", "doc_id")
        fld.text = str(id)

        fld = etree.SubElement(doc_node, "field")
        fld.set("name", "cl")
        fld.text = cl

        fld = etree.SubElement(doc_node, "field")
        fld.set("name", "inst")
        fld.text = inst

        fld = etree.SubElement(doc_node, "field")
        fld.set("name", "prop")
        fld.text = prop

        fld = etree.SubElement(doc_node, "field")
        fld.set("name", "label")
        fld.text = label

        return doc_node



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def do_it(self, output_file, sample_only=False):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        f_out = open(output_file, "wb")
        f_out.write(bytes("<add>\n", "utf-8"))
        self.load_prefixes()
        log_it("INFO", f"querying list of properties...")
        props = self.get_props()
        log_it("INFO", f"retrieved {len(props)} properties")
        prop_num = 0
        prop_cnt = len(props)
        rec_num = 0
        for p in props:
            prop_num += 1
            has_string_range = self.has_string_range(p)
            if not has_string_range: 
                log_it("INFO", f"Property {p} has not a xsd:string range, skipping it")
                continue
            log_it("INFO", f"querying list of classes in domain of property {p} {prop_num}/{prop_cnt}...")
            classes_in_domain = self.get_classes_in_domain(p)
            log_it("INFO", f"retrieved {len(classes_in_domain)} classes in domain of property {p} {prop_num}/{prop_cnt}")
            for cl in classes_in_domain:
                log_it("INFO", f"querying detailed record for class {cl} and property {p} {prop_num}/{prop_cnt}...")
                records = self.get_detailed_records(p, cl, limit=1000 if sample_only else None)
                log_it("INFO", f"retrieved {len(records)} detailed record for class {cl} and property {p} {prop_num}/{prop_cnt}")
                if len(records) > 100000:
                    log_it("WARNING", f"More than 100000 records for class {cl} and property {p}...")                
                for rec in records:
                    rec_num += 1
                    doc = self.get_solr_doc(rec, rec_num)
                    data_bytes = etree.tostring(doc, encoding="utf-8", pretty_print=True)
                    f_out.write(data_bytes)

        f_out.write(bytes("</add>\n", "utf-8"))
        f_out.close()
        log_it("INFO", "end")



#-------------------------------------------------
if __name__ == '__main__':
#-------------------------------------------------
    optparser = OptionParser(usage="python string_finder.py [--crlf] sparql_service_url output_file")
    # optparser.add_option("-c", "--crlf",
    #     action="store_true", dest="with_crlf", default=False,
    #     help="When set, output file line sep is CR/LF instead of LF")
    optparser.add_option("-s", "--sample",
        action="store_true", dest="sample", default=False,
        help="When set, output file contains just a sample of data")
    (options, args) = optparser.parse_args()
    if len(args) != 2:
        print("ERROR, usage is: python string_finder.py [--sample] [--crlf] sparql_service_url output_file")    
        sys.exit(1)

    builder = StringFinder(sparql_service=args[0])
    builder.do_it(output_file=args[1],sample_only=options.sample)

