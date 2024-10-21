import sys
import codecs
import os
#import glob
import json
import gc
import pickle
#import re
from optparse import OptionParser
from datetime import datetime
from lxml import etree
from io import StringIO, BytesIO
import random
from copy import deepcopy
import requests
import subprocess

import ApiCommon
from ApiCommon import log_it
from fields_utils import FldDef
from namespace_registry import NamespaceRegistry as ns_reg

from rdf_builder import RdfBuilder
from organizations import KnownOrganizations, Organization

from terminologies import Terminologies, Terminology
from ontology_builder import OntologyBuilder
from databases import Database, Databases
from ge_methods import GenomeModificationMethods, GeMethod
from cl_categories import CellLineCategories, CellLineCategory
from sexes import Sexes, Sex

# called dynamically
from ncbi_taxid_parser import NcbiTaxid_Parser
from chebi_parser import Chebi_Parser
from cl_parser import Cl_Parser
from uberon_parser import Uberon_Parser
from ncit_parser import Ncit_Parser
from ordo_parser import Ordo_Parser
from vbo_parser import Vbo_Parser
from rs_parser import Rs_Parser

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_solr_search_url(verbose=False):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    value = os.getenv("CELLAPI_SOLR_SEARCH_URL","http://localhost:8983/solr/pamcore1/select")
    if verbose:
        log_it("INFO:", "reading / getting default for env variable", "CELLAPI_SOLR_SEARCH_URL", value)
    return value


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_all_solr_params(fldDef, query="id:HeLa", fields="ac", sort="score desc", start=0, rows=1000):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    solr_q = fldDef.normalize_solr_q(query)
    solr_fl = "" if fields is None  or len(fields.strip())==0 else fldDef.normalize_solr_fl(fields)
    solr_sort = "score desc" if sort is None or len(sort.strip())==0 else fldDef.normalize_solr_sort(sort)
    params = {
        "fl":solr_fl, 
        "indent": True, 
        "q.op": "AND", 
        "q": solr_q ,
        "start": str(start), 
        "rows": str(rows), 
        "defType": "edismax",
        "sort": solr_sort,
        "wt" : "json",
        "qf": "ac^16 id^16 sy^8 text",   # acas dr rx ww cc str di ox hi oi sx ag ca dt ch text",
        "pf": "ac^160 id^160 sy^80 text" # acas dr rx ww cc str di ox hi oi sx ag ca dt ch text"        
    }

    return params

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_json_object(el):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    obj = build_jsonable_object(el)
    return {el.tag: obj}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def seen_as_list(tag):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # case 1: should be renamed to str-profile in the future for more clarity
    if tag == "str-list" : return False
    # case 2: general case
    if tag.endswith("-list") : return True
    # case 3: special cases
    if tag in ["same-origin-as", "site", "derived-from"]: return True
    # case 4: default
    return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_items_prop_name(tag):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if tag == "site": return "xref-list"
    return "items"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def build_jsonable_object(el):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # create object, add attributes and text node as obj properties
    obj = dict()
    if el.text is not None:
        txt = el.text.strip()
        if len(txt) > 0: obj["value"]=txt
    for attr in el.keys():
        obj[attr]=el.get(attr)
    # an author-list contains a choice of persons and consortia, the element tag is turned into the attribute "type"
    if el.tag in ["person", "consortium"]:
        obj["type"] = el.tag

    # XML elements containing a list of sub elements are expected to names ending with '-list'
    # But as always there are some exceptions... which are handled in seen_as_list()
    if seen_as_list(el.tag):
        # Recursively add child objects in items list
        items_prop = get_items_prop_name(el.tag)
        obj[items_prop]= list()
        for child_el in el:
            # - - - - - -  - with object name encapsulation - - - - - - - (change 1)
            #child_obj = dict()
            #child_obj[child_el.tag]=build_jsonable_object(child_el)
            # - - - - - - - - - - - -  or without - - - - - - - - - - - -
            child_obj = build_jsonable_object(child_el)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            obj[items_prop].append(child_obj)
            # Simplify list having only an "items" property (almost all the cases except for el "site")
        if len(obj)==1 and "items" in obj: return obj["items"]

    else:

        # Recursively add child objects in object properties
        for child_el in el:
            obj[child_el.tag]=build_jsonable_object(child_el)
        # Simplify object having only a "value" property - - - - - - - - (change 2)
        if len(obj)==1 and "value" in obj: return obj["value"]
    return obj




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def wait_for_input(msg):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print(msg)
    for line in sys.stdin: break;

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_txt_cell_line(f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    lines = list()
    while True:
        line = f_in.readline()
        if line == "": return None           # <-- end of file
        lines.append(line)
        if line[0:2] == "//": return lines   # <-- end of record


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_txt_ref(f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    lines = list()
    while True:
        line = f_in.readline()
        if line == "": return None           # <-- end of file
        if line[0:2] == "**": continue       # <-- ignore comments in the header
        lines.append(line)
        if line[0:2] == "//": return lines   # <-- end of record

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def save_txt_refs(input_file):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    t0 = datetime.now()
    output_file = ApiCommon.RF_TXT_FILE
    log_it("INFO:", "Start saving txt references in", output_file)
    rf_dict = dict()
    f_in  = open(input_file, "r")
    f_out = open(output_file, "wb")

    no = 0
    while True:
        # read cell line record as a list of lines
        lines = read_txt_ref(f_in)
        if lines == None: break
        no += 1
        if no % 10000 == 0: log_it("INFO:", "Saving reference", no)

        # build record as bytes and write them
        pos = f_out.tell()
        rec = "".join(lines)
        bytes = rec.encode("utf-8")
        f_out.write(bytes)
        size = len(bytes)

        # find reference identifier(s)
        ids = list()
        for line in lines:
            if line[0:5] == "RX   ":
                tmp_list = line[5:].strip().split("; ")
                for id in tmp_list:
                    clean_id = id.strip()
                    if clean_id.endswith(";") : clean_id = clean_id[:-1]
                    clean_id = clean_id.strip()
                    if len(clean_id) > 0: ids.append(clean_id)
                break
        if len(ids) == 0:
            log_it("ERROR: no ids for record", rec)
            sys.exit()

        # save info for index
        for id in ids: rf_dict[id] = { "txt_pos": pos, "txt_size": size }


    log_it("INFO:", "Saving reference", no)
    f_in.close()
    f_out.close()
    log_it("INFO:", "Saved txt reference, count:" , len(rf_dict), duration_since=t0)
    return rf_dict





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def save_txt_cell_lines(input_file):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    t0 = datetime.now()
    output_file = ApiCommon.CL_TXT_FILE
    log_it("INFO:", "Start saving txt cell_lines in", output_file)
    cl_dict = dict()
    f_in  = open(input_file, "r")
    f_out = open(output_file, "wb")

    # skip header
    while True:
        if "__________" in f_in.readline(): break

    no = 0
    while True:
        # read cell line record as a list of lines
        lines = read_txt_cell_line(f_in)
        if lines == None: break
        no += 1
        if no % 10000 == 0: log_it("INFO:", "Saving cell line", no)

        # build record as bytes and write them
        pos = f_out.tell()
        rec = "".join(lines)
        bytes = rec.encode("utf-8")
        f_out.write(bytes)
        size = len(bytes)

        # find accession value
        ac = None
        for line in lines:
            if line[0:5] == "AC   ":
                ac = line[5:].strip()
                break
        if ac == None:
            log_it("ERROR: no AC for record", rec)
            sys.exit()

        # save info for index
        cl_dict[ac] = { "txt_pos": pos, "txt_size": size }


    log_it("INFO:", "Saving cell line", no)
    f_in.close()
    f_out.close()
    log_it("INFO:", "Saved txt cell lines, count:" , len(cl_dict), duration_since=t0)
    return cl_dict

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def save_xml_cell_lines(bigxml_root):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    t0 = datetime.now()
    filename = ApiCommon.CL_XML_FILE
    log_it("INFO:", "Start saving xml cell_lines in", filename)
    # find list of cell line elements
    el_list = bigxml_root.xpath("/Cellosaurus/cell-line-list/cell-line/accession-list/accession[@type='primary']")
    log_it("INFO:",  "Found cell line primary accessions, count:" , len(el_list))
    # build cell line dictionary key = cvcl, value=(file_offset,obj_size)
    f_out = open(filename, "wb")
    cl_dict = dict()
    children_dict = dict()
    no=0
    for el in el_list:

        no+=1
        if no % 10000 == 0: log_it("INFO:", "Saving cell line", no)

        # write record get its position and size in file
        cl = el.getparent().getparent()
        ac = el.text.strip()
        id = cl.xpath("./name-list/name[@type='identifier']")[0].text.strip()
        cl_bytes = etree.tostring(cl, encoding='utf-8')
        pos = f_out.tell()
        size = f_out.write(cl_bytes)

        # add dictionary item with pos, size in file and ref list for this cell line
        ref_list = cl.xpath("./reference-list/reference")
        iref_list = list()
        for ref in ref_list:
            iref_list.append(ref.get("resource-internal-ref"))
        rec = { "xml_pos": pos, "xml_size": size, "ref_list": iref_list }
        cl_dict[ac] = rec

        # update parent cell line dictionary entry by adding current cl as a child
        parent_list = cl.xpath("./derived-from/xref")
        for parent in parent_list:
            parent_ac = parent.get("accession")
            if parent_ac not in children_dict: children_dict[parent_ac] = list()
            children_dict[parent_ac].append({"ac": ac, "id": id})
        #if no>10: break

    log_it("INFO:", "Saving cell line", no)
    f_out.close()

    # update cl dictionary with parent child info
    for ac in cl_dict:
        rec = cl_dict[ac]
        if ac in children_dict:
            rec["child_list"] = children_dict[ac]
        else:
            rec["child_list"] = list()

    log_it("INFO:", "Saved xml cell lines, count:" , len(cl_dict), duration_since=t0)
    return cl_dict


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def save_xml_references(bigxml_root):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    filename = ApiCommon.RF_XML_FILE
    t0 = datetime.now()
    log_it("INFO:", "Start saving xml references in", filename)
    ref_list = bigxml_root.xpath("/Cellosaurus/publication-list/publication")
    log_it("INFO:", "Found publication elements, count:" , len(ref_list))
    f_out = open(filename, "wb")
    ref_dict = dict()
    no=0
    for ref in ref_list:
        no+=1
        id = ref.get("internal-id")
        ref_bytes = etree.tostring(ref, encoding='utf-8')
        pos = f_out.tell()
        size = f_out.write(ref_bytes)
        if no % 10000 == 0: log_it("INFO:", "Saving reference", no)
        rec = { "xml_pos": pos, "xml_size": size }
        ref_dict[id]=rec
        #if no>10: break
    log_it("INFO:", "Saving reference", no)
    f_out.close()
    delta = datetime.now() - t0
    log_it("INFO:", "Saved xml references, count:" , len(cl_dict), duration_since=t0)
    return ref_dict


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_release_info(bigxml_root):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    t0 = datetime.now()
    log_it("INFO:", "Start extracting release stats from xml")
    node = bigxml_root.xpath("/Cellosaurus/header/release")[0] # there is one and only one such element
    version = node.get("version")
    updated= node.get("updated")
    nb_cell_lines = node.get("nb-cell-lines")
    nb_publications = node.get("nb-publications")
    log_it("INFO:", version, updated, nb_cell_lines, nb_publications)
    log_it("INFO:", "Extracting release stats done")
    release_info = {"version": version, "updated": updated, "nb-cell-lines":nb_cell_lines, "nb-publications": nb_publications}
    return release_info

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def save_pickle(obj, filename):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    t0 = datetime.now()
    log_it("INFO:", "Start saving object in", filename)
    f_out = open(filename, 'wb')
    pickle.dump(obj, f_out, protocol=3) # pickle.HIGHEST_PROTOCOL is 3 for python 3.6, 4 for python 3.8
    f_out.close()
    delta = datetime.now() - t0
    log_it("INFO:", "Saved object in", filename, duration_since=t0)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def check_xml_references(cl_dict, ref_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    count = 0
    for cl_key in cl_dict:
        cl = cl_dict[cl_key]
        for ref_id in cl["ref_list"]:
            count += 1
            if ref_id not in ref_dict:
                log_it("ERROR: in", cl_key, "Unknown reference", ref_id )
    log_it("INFO:", "Reference check count", count)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def load_pickle(filename):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    log_it("INFO:", "Start loading object from", filename)
    t0 = datetime.now()
    f_in = open(filename, 'rb')
    obj = pickle.load(f_in)
    f_in.close()
    delta = datetime.now() - t0
    log_it("INFO:", "Loaded object from", filename, duration_since=t0)
    return obj

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def load_and_parse_xml(filename):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    log_it("INFO:", "reading", filename, "...")
    parser = etree.XMLParser(remove_blank_text=True)
    root_node = etree.parse(filename, parser).getroot()
    log_it("INFO:", "xml parsed")
    return root_node

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_txt_cell_line(ac, cl_dict, cl_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cl_index = cl_dict[ac]
    cl_f_in.seek(cl_index["txt_pos"])
    bytes = cl_f_in.read(cl_index["txt_size"])
    rec = bytes.decode("utf-8")
    rec = rec.strip()[0:-2]                         # uggly removal of final //
    rec += get_txt_cell_children(ac, cl_dict)
    rec += "//\n"                                   # re-appending of //
    return rec

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_txt_cell_children(ac, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    rec = ""
    cl_index = cl_dict[ac]
    for child in cl_index["child_list"]:
        line = "CH   " + child["ac"] + " ! " + child["id"] + "\n"
        rec += line
    return rec


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def filter_lines_by_prefixes(data, prefixes):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if prefixes is None: return data

    result = ""
    line_list = data.split("\n")
    for line in line_list:
        for pf in prefixes:
            if line.startswith(pf):
                result += line + "\n"
                break
    return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_tsv_multi_cell(ac_list, fields, fldDef, cl_dict, cl_txt_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    # if no fields are defined we want them all
    if fields is None or fields=="":
        fld_list = fldDef.keys()
    else:
        fld_list = fields if isinstance(fields,list) else fields.split(",")

    fld_list = [fld.lower().strip() for fld in fld_list]

    # build tsv header with field names
    result = "\t".join(fld_list) + '\n' 
    
    # collect cell line records
    for ac in ac_list:
        cl_text = get_txt_cell_line(ac, cl_dict, cl_txt_f_in)
        fld_dic = get_cell_line_fld_dic_from_text(cl_text, fld_list, fldDef)
        first_fld = True
        for fld in fld_list:
            value = fld_dic.get(fld) or ""
            if first_fld:
                first_fld = False
                result += value
            else:
                result += "\t" + value
        result += "\n"
    return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_txt_multi_cell(ac_list, prefixes, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    result = ""
    rf_ids = set()
    # collect cell line records
    for ac in ac_list:
        #log_it("ac", ac)
        cl = get_txt_cell_line(ac, cl_dict, cl_txt_f_in)
        cl = filter_lines_by_prefixes(cl, prefixes)
        #log_it(">>> cl: ",cl)
        #log_it("------")
        if len(cl)>0 and prefixes is not None: cl += "//\n"
        result += cl
        cl_index = cl_dict[ac]
        for ref_id in cl_index["ref_list"]: rf_ids.add(ref_id)
    for rf_id in rf_ids:
        rf = get_txt_reference(rf_id, rf_dict, rf_txt_f_in)
        if rf is not None:
            rf = filter_lines_by_prefixes(rf, prefixes)
            if len(rf)>0 and prefixes is not None: rf += "//\n"
            result += rf
    return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_multi_cell(ac_list, xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    trg_root = etree.Element("Cellosaurus")
    trg_cl_root = etree.SubElement(trg_root, "cell-line-list")
    rf_ids = set()
    # get list of cell line nodes and build set of referred publications
    for ac in ac_list:
        cl = get_xml_cell_line(ac, cl_dict, cl_xml_f_in)
        tmp_node = etree.Element("tmp")
        append_filtered_xml(tmp_node, cl, xpaths)
        cl_node = tmp_node.find("cell-line")
        if cl_node is not None: trg_cl_root.append(cl_node)
        cl_index = cl_dict[ac]
        for ref_id in cl_index["ref_list"]: rf_ids.add(ref_id)
    # get list of referred publications nodes
    trg_rf_root = etree.Element("publication-list")
    for rf_id in rf_ids:
        rf = get_xml_reference(rf_id, rf_dict, rf_xml_f_in)
        tmp_node = etree.Element("tmp")
        append_filtered_xml(tmp_node, rf, xpaths)
        rf_node = tmp_node.find("publication")
        if rf_node is not None: trg_rf_root.append(rf_node)
    if len(trg_rf_root)>0: trg_root.append(trg_rf_root)
    return trg_root

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def append_filtered_xml(trg_xml_root, some_xml_root, path_list):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if path_list is None:
        trg_xml_root.append(some_xml_root)
        return
    for path in path_list:
        nodes = some_xml_root.xpath(path)
        if len(nodes)>0:
            # the '' before first / is irrelevant
            # e.g: /cell-line/xref-list/xref/property-list/property[@name="Discontinued"]/../..
            path_items = path.split("/")[1:]           
            # ->:  "cell-line" "xref-list" "xref" "property-list" "property[@name="Discontinued"]" ".." ".."
            # find parent elements of nodes we retrieved from xpath expression:
            # a) remove and count '..' path elements from the right side (if any)
            # e.g: ".." ".." in "cell-line" "xref-list" "xref" "property-list" "property[@name="Discontinued"]" ".." ".."
            back_num = 0
            while path_items[-1]=='..': 
                back_num += 1
                path_items.pop()
            # b) remove elements of the xpath expression used as a selection criterion that are children of the nodes retrieved
            # e.g:  "property-list" "property[@name="Discontinued"]" in "cell-line" "xref-list" "xref" "property-list" "property[@name="Discontinued"]"
            if back_num != 0: path_items = path_items[0: - back_num]
            # c) finally remove the tag of the nodes we retrieved from the xpath expression
            parent_tags = path_items[0:-1]
            current_parent = trg_xml_root
            # now create an xml element for each parent of the nodes we retrieved
            for tag in parent_tags:
                node = current_parent.find(tag)
                if node is None: node = etree.SubElement(current_parent, tag)
                current_parent = node
            last_item = path_items[-1]
            # add retrieved attribute or element nodes as children of closest parent element
            if last_item.startswith("attribute"):      # i.e. attribute::category
                attr_name = last_item.split(":")[2]
                attr_value = nodes[0]                  # we get an attribute value in nodes[0]
                current_parent.attrib[attr_name]=attr_value
            else:
                for n in nodes:                        # we get real nodes in nodes
                    current_parent.append(deepcopy(n))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_txt_multi_cell_children(ac_list, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    rec = ""
    for ac in ac_list:
        rec += "AC   " + ac + "\n"
        rec += get_txt_cell_children(ac, cl_dict)
        rec += "//\n"
    return rec

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_txt_reference(rf_id, rf_dict, rf_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if rf_id not in rf_dict:
        log_it("ERROR: reference not found", rf_id)
        return None
    rf_index = rf_dict[rf_id]
    rf_f_in.seek(rf_index["txt_pos"])
    bytes = rf_f_in.read(rf_index["txt_size"])
    ref = bytes.decode("utf-8")
    return ref


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_tsv_cell_children(ac, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cl_index = cl_dict[ac]
    rec = ""
    for child in cl_index["child_list"]:
        rec += ac + "\t" + child["ac"] + "\t" + child["id"] + "\n"        # tsv data
    return rec

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_tsv_multi_cell_children(ac_list, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    result = "parent_AC\tchild_AC\tchild_ID\n"                            # tsv header
    for ac in ac_list:
        result += get_tsv_cell_children(ac, cl_dict)
    return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_cell_line(ac, cl_dict, cl_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cl_index = cl_dict[ac]
    cl_f_in.seek(cl_index["xml_pos"])
    bytes = cl_f_in.read(cl_index["xml_size"])
    tree = etree.parse(BytesIO(bytes))
    # get cell line xml element
    cl = tree.getroot()
    children_node = get_xml_cell_children(ac, cl_dict)
    if children_node != None: cl.append(children_node)
    return cl

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_cell_children(ac, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cl_index = cl_dict[ac]
    child_list = cl_index["child_list"]
    #if len(child_list)==0: return None
    children_node = etree.Element("child-list")
    for child in child_list:
        child_el = etree.SubElement(children_node, "child")
        ac_el = etree.SubElement(child_el, "accession", type = "primary" )
        ac_el.text = child["ac"]
        id_el = etree.SubElement(child_el, "name", type = "identifier" )
        id_el.text = child["id"]
    return children_node

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_multi_cell_children(ac_list, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    main_node = etree.Element("Cellosaurus")
    cll_node = etree.SubElement(main_node, "cell-line-list")
    for ac in ac_list:
        cl_node = etree.SubElement(cll_node, "cell-line")
        al_node = etree.SubElement(cl_node, "accession-list")
        ac_node = etree.SubElement(al_node, "accession", type="primary")
        ac_node.text = ac
        ch_node = get_xml_cell_children(ac, cl_dict)
        if ch_node != None: cl_node.append(ch_node)
    return main_node



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_json_multi_cell_children(ac_list, cl_dict):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    node = get_xml_multi_cell_children(ac_list, cl_dict)
    obj = get_json_object(node)
    return obj

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_xml_reference(rf_id, rf_dict, rf_f_in):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    rf_index = rf_dict[rf_id]
    rf_f_in.seek(rf_index["xml_pos"])
    bytes = rf_f_in.read(rf_index["xml_size"])
    tree = etree.parse(BytesIO(bytes))
    return tree.getroot()


# builds a string from a xml element (and sub elements) based on text, attrib ans tail
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_solr_field_value(node):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    value = recursive_solr_field_value(node,"")
    value = value.replace('\n',' ').replace('\t',' ')
    value = " ".join(value.split())
    return value

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def recursive_solr_field_value(node, value):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    result = value
    for k in node.attrib:
        result += k + "=" + node.get(k) + "; "
    if node.text is not None:
        result += node.text + " "
    for sub_node in node:
        result += recursive_solr_field_value(sub_node, value) + " "  
    if node.tail is not None:
        result += node.tail + " "
    return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_values_from_xpath(node, xp):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    values = list()
    if xp.startswith("attribute::"):
        attr_name = xp.split(":")[2]
        value = node.get(attr_name)
        if value is not None: values.append(value)
        
    else:
        for n in node.xpath(xp):
            value = get_solr_field_value(n)
            if len(value) >= 0: values.append(value)
    return values

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cell_line_solr_xml_doc_from_node(node, fldDef):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    doc_node = etree.Element("doc")
    cl_node = node.xpath("./cell-line-list/cell-line")[0]
    pu_node_list = node.xpath("./publication-list/publication")
    
    for k in fldDef.keys():
        fname = k.replace('-','_').lower()
        for xp in fldDef.get_xpaths(k):
            if xp.startswith("/publication"): 
                rel_xp = xp.replace("/publication/","")
                for pu_node in pu_node_list:
                    values = get_values_from_xpath(pu_node, rel_xp)
                    for value in values:
                        fld = etree.SubElement(doc_node, "field")
                        fld.set("name", fname)
                        fld.text = value
                        
            elif xp.startswith("/cell-line"): 
                rel_xp = xp.replace("/cell-line/","")
                values = get_values_from_xpath(cl_node, rel_xp)
                for value in values:
                    fld = etree.SubElement(doc_node, "field")
                    fld.set("name", fname)
                    fld.text = value
                
    return doc_node

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def merge_consecutive_prefix(lines, prefix):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    merged_line = ""
    new_lines = list()
    for line in lines:
        if line.startswith(prefix):
            merged_line += line[5:].strip() + " "
        else:
            if len(merged_line) > 0:
                merged_line = prefix + "   " + merged_line.strip()
                new_lines.append(merged_line)
                merged_line = ""
            new_lines.append(line)
            
    return new_lines            
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cell_line_fld_dic_from_text(cl_text, fld_list, fldDef):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    result = dict()
    lines = cl_text.split("\n")
    lines = merge_consecutive_prefix(lines, "RA")
    lines = merge_consecutive_prefix(lines, "RT")
    for fld in fld_list:
        for line in lines:
            for pr in fldDef.get_prefixes(fld):
                if line.startswith(pr):
                    if fld in ["dtc","dtu","dtv"]:
                        value = get_field_from_dt_line(line, fld)
                    else:
                        value = line[len(pr):]
                        if value.startswith(":"): value = value[1:]
                        value = value.strip()
                    if fld in result:
                        result[fld] += "|" + value
                    else:
                        result[fld] = value
    return result


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cell_line_solr_xml_doc_from_text(text, fldDef):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    doc_node = etree.Element("doc")
    
    lines = text.split("\n")
    lines = merge_consecutive_prefix(lines, "RA")
    lines = merge_consecutive_prefix(lines, "RT")

    for k in fldDef.keys(): 
        fname = k.replace('-','_').lower()
        for line in lines:
            for pr in fldDef.get_prefixes(k):
                if line.startswith(pr):         
                    
                    # special handler for date fields and long field of lines with prefix DT
                    if fname in ["dtc","dtu","dtv"]:
                        fld = etree.SubElement(doc_node, "field")
                        fld.set("name", fname)
                        fld.text = get_field_from_dt_line(line, fname)
                        
                    # special case for sy, idsy: we want to split multiple values in line
                    elif pr == "SY": #   fname in ["sy", "idsy"]:
                        sy_list = line[len(pr):].strip().split("; ")
                        for sy in sy_list:
                            fld = etree.SubElement(doc_node, "field")
                            fld.set("name", fname)
                            fld.text = sy
                        
                    # normal handler
                    else:
                        fld = etree.SubElement(doc_node, "field")
                        fld.set("name", fname)
                        value = line[len(pr):]
                        if value.startswith(":"): value = value[1:]
                        value = value.strip()
                        fld.text = value
                        # we need the additional field ac_str which is the unique key for solr
                        if fname == "ac":
                            fld = etree.SubElement(doc_node, "field")
                            fld.set("name", "ac_str")
                            fld.text = value                        
    return doc_node

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_field_from_dt_line(line, fname):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  
    # example of DT line:
    # DT   Created: 23-09-21; Last updated: 16-12-21; Version: 2
    items = line.split("; ")
    if fname == "dtc" and len(items)==3:
        (dd,mm,yy) = items[0].split(": ")[1].split("-")
        return "20" + yy + "-" + mm + "-" + dd
    elif fname == "dtu" and len(items)==3:
        (dd,mm,yy) = items[1].split(": ")[1].split("-")
        return "20" + yy + "-" + mm + "-" + dd
    elif fname == "dtv" and len(items)==3:
        version = items[2].split(": ")[1]
        return version
    return None

# - - - - - - - - - - - - - - 
def get_clid_dic(fldDef):
# - - - - - - - - - - - - - - 
    # called by main at init time
    # for subsequent efficient /fsearch 
    t0 = datetime.now()
    log_it("INFO:", "Building clid_dict...")
    url = get_solr_search_url()
    params = get_all_solr_params(fldDef, query="*:*", fields="ac,id,ox", sort="id asc", start=0, rows=1000000)
    headers = { "Accept": "application/json" }
    response = requests.get(url, params=params, headers=headers)
    obj = response.json()
    if response.status_code != 200:
        error_msg = ""
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        log_it("ERROR:", "code:", response.status_code, error_msg )
        log_it("ERROR:", "while building clid_dict, exiting !", duration_since=t0)
        sys.exit(1)
    clid_dict = dict()
    items = obj["response"]["docs"]
    for item in items:
        fields = [item["ac"], item["id"]] # order for elisabeth ?
        oxs = list()
        for ox in item["ox"]:
            _, label = ox.split(" ! ")
            oxs.append(label) 
        fields.append(" / ".join(oxs))
        line = "\t".join(fields)     
        clid_dict[item["id"]] = line
    log_it("INFO:", "clid_dict size:", len(clid_dict), duration_since=t0)
    return clid_dict

# - - - - - - - - - - - - - - - - - - - - 
def save_virtuoso_isql_setup_file(output_file):
# - - - - - - - - - - - - - - - - - - - - 
    lines = []
    lines.append("""grant select on "DB.DBA.SPARQL_SINV_2" to "SPARQL";""")
    lines.append("""grant execute on "DB.DBA.SPARQL_SINV_IMP" to "SPARQL";""")
    lines.append("""GRANT SPARQL_SPONGE TO "SPARQL";""")
    lines.append("""GRANT EXECUTE ON DB.DBA.L_O_LOOK TO "SPARQL";""")
    for ns in ns_reg.namespaces:
        lines.append(ns.getSQLforVirtuoso())
    f_out = open(output_file, "w")
    for line in lines: f_out.write(line + "\n")
    f_out.close()


# ===========================================================================================
if __name__ == "__main__":
# ===========================================================================================
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) < 1: sys.exit("Invalid arg1, expected BUILD, SOLR, RDF, LOAD_RDF, ONTO or TEST")

    if args[0] not in [ "BUILD", "SOLR", "RDF", "LOAD_RDF", "ONTO", "TEST" ]: 
        sys.exit("Invalid arg1, expected BUILD, SOLR, RDF, LOAD_RDF, ONTO or TEST")

    input_dir = "data_in/"
    if input_dir[-1] != "/" : input_dir + "/"

    # -------------------------------------------------------
    if args[0]=="RDF":
    # -------------------------------------------------------

        # be aware that
        # here we use api data and indexes created when args0="BUILD"
    
        known_orgs = KnownOrganizations()
        known_orgs.loadInstitutions(input_dir + "institution_list")
        known_orgs.loadOnlineResources(input_dir + "cellosaurus_xrefs.txt")

        terminologies = Terminologies()

        rb = RdfBuilder(known_orgs)

        cl_dict = load_pickle(ApiCommon.CL_IDX_FILE)
        rf_dict = load_pickle(ApiCommon.RF_IDX_FILE)
        cl_txt_f_in = open(ApiCommon.CL_TXT_FILE,"rb")
        rf_txt_f_in = open(ApiCommon.RF_TXT_FILE,"rb")
        cl_xml_f_in = open(ApiCommon.CL_XML_FILE,"rb")
        rf_xml_f_in = open(ApiCommon.RF_XML_FILE,"rb")
        fldDef = FldDef(ApiCommon.FLDDEF_FILE)

        out_dir = "rdf_data/"
        # create or clean output dir
        if not os.path.exists(out_dir): os.mkdir(out_dir)
        os.system("rm " + out_dir + "*")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create RDF for cell-line data
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_cell_lines.ttl", "wb")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        item_cnt = 0
        log_it("INFO:", f"serializing cl: {item_cnt} / {len(cl_dict)}")
        for ac in cl_dict:
            item_cnt += 1
            #if item_cnt > 20000: break
            if item_cnt % 10000 == 0: log_it("INFO:", f"serializing cl: {item_cnt} / {len(cl_dict)}")
            cl_xml = get_xml_cell_line(ac, cl_dict, cl_xml_f_in)
            cl_obj = get_json_object(cl_xml)
            file_out.write(  bytes(rb.get_ttl_for_cl(ac, cl_obj) , "utf-8" ) )
        file_out.close()
        log_it("INFO:", f"serialized cl: {item_cnt} / {len(cl_dict)}")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create RDF for publications
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        ref_out = open(out_dir + "data_refs.ttl", "wb")
        ref_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        item_cnt = 0
        log_it("INFO:", f"serializing refs: {item_cnt} / {len(rf_dict)}")
        for rf_id in rf_dict:
            item_cnt += 1
            if item_cnt % 10000 == 0: log_it("INFO:", f"serializing refs: {item_cnt} / {len(rf_dict)}")
            rf_xml = get_xml_reference(rf_id, rf_dict, rf_xml_f_in)
            rf_obj = get_json_object(rf_xml)
            ref_out.write( bytes(rb.get_ttl_for_ref(rf_obj), "utf-8") ) 
        ref_out.close()
        log_it("INFO:", f"serialized refs: {item_cnt} / {len(rf_dict)}")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # extract cited terms from xrefs, infer parent terms from cited terms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        cited_terms = dict()
        xr_dict = rb.get_xref_dict()
        item_cnt = 0
        log_it("INFO:", f"extracting terms from xrefs: {item_cnt} / {len(xr_dict)}")
        for k in xr_dict:
            item_cnt += 1
            if item_cnt % 10000 == 0: log_it("INFO:", f"looking up xrefs: {item_cnt} / {len(xr_dict)}")
            db, ac = k.split("=")
            termi = terminologies.get(db)
            if termi is not None:
                if db not in cited_terms: cited_terms[db] = set()
                cited_terms[db].add(ac)
        log_it("INFO:", f"looked up xrefs: {item_cnt} / {len(xr_dict)}")


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # get relevant set of terms to be RDFized and serialize them
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        for k in terminologies.termi_dict:
            termi: Terminology = terminologies.get(k)
            log_it("INFO:", f"Serializing terminology {k} ...")
            file_out = open(out_dir + "data_" + termi.abbrev + ".ttl", "wb")
            file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
            parser = getattr(__import__("__main__"), termi.parser_name)(k)
            # we get version from parser, will be used in RDF defining terminologies as NamedIndividual
            termi.version = parser.get_termi_version() 
            cited_set = cited_terms.get(k) or set()
            log_it("INFO:", "Cited_set", k, len(cited_set))
            relevant_id_set = set()
            for id in cited_set:
                term = parser.get_term(id)
                if term is None:
                    log_it("ERROR:", f"Cited term/concept {id} not found in {k} terminology")
                else:
                    parent_list = parser.get_with_parent_list(id)
                    relevant_id_set.update(parent_list)
            relevant_term_dic = dict()
            for id in relevant_id_set:
                term = parser.get_term(id)
                if term is None:
                    log_it("ERROR:", f"Parent term/concept {id} not found in {k} terminology")
                else:
                    file_out.write( bytes(rb.get_ttl_for_term(term), "utf-8") ) 
            file_out.close()
            log_it("INFO:", f"Serialized terminology {k}: {len(relevant_id_set)} relevant concepts")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create RDF for xrefs
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_xrefs.ttl", "wb")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        xr_dict = rb.get_xref_dict()
        item_cnt = 0
        log_it("INFO:", f"serializing xrefs: {item_cnt} / {len(xr_dict)}")
        for k in xr_dict:
            item_cnt += 1
            if item_cnt % 10000 == 0: log_it("INFO:", f"serializing xrefs: {item_cnt} / {len(xr_dict)}")
            db,ac = k.split("=")
            file_out.write( bytes(rb.get_ttl_for_xref_key(k), "utf-8") ) 
        file_out.close()
        log_it("INFO:", f"serialized xrefs: {item_cnt} / {len(xr_dict)}")


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create RDF for organizations
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_orgs.ttl", "wb")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        orga_dict = rb.get_orga_dict()
        item_cnt = 0
        log_it("INFO:", f"serializing orgs: {item_cnt} / {len(orga_dict)}")
        for data_key in sorted(orga_dict):
            item_cnt += 1
            if item_cnt % 10000 == 0: log_it("INFO:", f"serializing orgs: {item_cnt} / {len(orga_dict)}")
            count = orga_dict[data_key]
            file_out.write( bytes(rb.get_ttl_for_orga(data_key, count), "utf-8") ) 
        file_out.close()
        log_it("INFO:", f"serialized orgs: {item_cnt} / {len(orga_dict)}")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create OWL definitions for terminologies
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_terminologies.ttl", "wb")
        log_it("INFO:", f"serializing OWL for terminologies")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        for k in terminologies.termi_dict:
            termi: Terminology = terminologies.get(k)
            file_out.write(bytes(rb.get_ttl_for_cello_terminology_individual(termi) + "\n", "utf-8"))
        file_out.close()
        log_it("INFO:", f"serialized OWL for terminologies")


        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create OWL definitions for Database individuals
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_databases.ttl", "wb")
        log_it("INFO:", f"serializing OWL for database individuals")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        databases = Databases()                        
        for k in databases.keys():
            db: Database = databases.get(k)
            file_out.write(bytes(rb.get_ttl_for_cello_database_individual(db) + "\n", "utf-8"))
        file_out.close()
        log_it("INFO:", f"serialized OWL for database individuals")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # create OWL definitions for other named subclasses and individuals
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        file_out = open(out_dir + "data_other_entities.ttl", "wb")
        log_it("INFO:", f"1) serializing OWL for sexes")
        file_out.write(bytes(rb.get_ttl_prefixes() + "\n", "utf-8"))
        sexes = Sexes()
        for k in sexes.keys():
            s = sexes.get(k)
            file_out.write(bytes(rb.get_ttl_for_sex(s) + "\n", "utf-8"))                        
        file_out.close()
        log_it("INFO:", f"serialized OWL definitions for other entities")

        log_it("INFO:", "end")


    # -------------------------------------------------------
    if args[0]=="LOAD_RDF":
    # -------------------------------------------------------
        if args[1].lower() == "data":
            setup_file = './scripts/virtuoso_setup.sql'
            save_virtuoso_isql_setup_file(setup_file)
            log_it("INFO", "Created", setup_file )
            result = subprocess.run(['bash', './scripts/reload_rdf_data.sh'], capture_output=True, text=True)
            log_it("LOADED data, status", result.stdout)
        elif args[1].lower() == "onto":
            result = subprocess.run(['bash', './scripts/reload_rdf_onto.sh'], capture_output=True, text=True)
            log_it("INFO", "LOADED (onto)logy, status", result.stdout)
        elif args[1].lower() == "void":
            result = subprocess.run(['bash', './scripts/reload_rdf_void.sh'], capture_output=True, text=True)
            log_it("INFO", "LOADED void metadata, status", result.stdout)
        else:
            log_it("Invalid argument after LOAD, expected data, onto or void")
            sys.exit(10)

    # -------------------------------------------------------
    if args[0]=="ONTO":
    # -------------------------------------------------------

        # create OWL cellosaurus ontology
        # NOTE: property range & domain info is inferred from RDF data
        # so you need to first generate RDF, lpoad the files and then only
        # use this task to build the ontology and load

        version = "1.0"
        if len(args)>1: version = args[1]

        out_dir = "rdf_data/"
        file_out = open(out_dir + "ontology.ttl", "wb")
        log_it("INFO:", f"serializing OWL cellosaurus ontology")
        builder = OntologyBuilder()
        lines = builder.get_onto_pretty_ttl_lines(version)
        count = 0
        for line in lines:
            count += 1
            if count % 500 == 0: log_it(f"writing line {count} / {len(lines)}")
            file_out.write(bytes(line + "\n", "utf-8"))
        log_it("INFO", f"writing line {count} / {len(lines)}")
        log_it("INFO:", f"serialized OWL cellosaurus ontology")


    # -------------------------------------------------------
    if args[0]=="SOLR":
    # -------------------------------------------------------

        # be aware that
        # here we use api data and indexes created when args0="BUILD"
    
        cl_dict = load_pickle(ApiCommon.CL_IDX_FILE)
        rf_dict = load_pickle(ApiCommon.RF_IDX_FILE)
        cl_txt_f_in = open(ApiCommon.CL_TXT_FILE,"rb")
        rf_txt_f_in = open(ApiCommon.RF_TXT_FILE,"rb")
        cl_xml_f_in = open(ApiCommon.CL_XML_FILE,"rb")
        rf_xml_f_in = open(ApiCommon.RF_XML_FILE,"rb")
        fldDef = FldDef(ApiCommon.FLDDEF_FILE)

        out_dir = "solr_data/"
        # create or clean output dir
        if not os.path.exists(out_dir): os.mkdir(out_dir)
        os.system("rm " + out_dir + "*")

        max_doc = 10000000    # enough for 10 millions cell lines, set small value for debugging
        #max_doc = 20
        
        doc_per_file = 2000

        num_doc = 0
        file_index = 0
        for ac in cl_dict:
            num_doc += 1
            if num_doc > max_doc: break            

            if num_doc % doc_per_file == 1:
                file_index += 1
                output_file = out_dir + "data" + str(file_index) + ".xml"
                f_out = open(output_file, "wb")
                f_out.write(bytes("<add>\n","utf-8"))

            data = get_txt_multi_cell([ac], None, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in)
            doc = get_cell_line_solr_xml_doc_from_text(data, fldDef)
            data_bytes = etree.tostring(doc, encoding="utf-8", pretty_print=True)
            f_out.write(data_bytes)

            if num_doc % doc_per_file == 0:
                log_it("INFO:", "wrote " + output_file)
                f_out.write(bytes("</add>\n",'utf-8'))
                f_out.close()

        if not f_out.closed:
            f_out.write(bytes("</add>\n",'utf-8'))
            f_out.close()
        log_it("INFO:", "wrote " + output_file)
        log_it("INFO:", "wrote cell lines solr documents, count", len(cl_dict))
        log_it("INFO:", "end")
                    

    # -------------------------------------------------------
    elif args[0]=="BUILD":
    # -------------------------------------------------------

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # TXT stuff
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cl_txt_input_file = input_dir + "cellosaurus.txt"
        cl_txt_dict = save_txt_cell_lines(cl_txt_input_file)
        rf_txt_input_file = input_dir + "cellosaurus_refs.txt"
        rf_txt_dict = save_txt_refs(rf_txt_input_file)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # XML stuff
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xml_input_file = input_dir + "cellosaurus.xml"
        xml_root = load_and_parse_xml(xml_input_file)
        release_info = get_xml_release_info(xml_root)
        cl_dict = save_xml_cell_lines(xml_root)
        rf_dict = save_xml_references(xml_root)
        check_xml_references(cl_dict, rf_dict)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # merge TXT and XML indexes and save them
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for ac in cl_txt_dict:
            target = cl_dict[ac]
            source = cl_txt_dict[ac]
            target["txt_pos"] = source["txt_pos"]
            target["txt_size"] = source["txt_size"]

        for id in rf_txt_dict:
            if id not in rf_dict: continue
            target = rf_dict[id]
            source = rf_txt_dict[id]
            target["txt_pos"] = source["txt_pos"]
            target["txt_size"] = source["txt_size"]

        save_pickle(release_info, ApiCommon.RI_FILE)
        save_pickle(cl_dict, ApiCommon.CL_IDX_FILE)
        save_pickle(rf_dict, ApiCommon.RF_IDX_FILE)

    # -------------------------------------------------------
    elif args[0]=="TEST":
    # -------------------------------------------------------

        release_info = load_pickle(ApiCommon.RI_FILE)
        cl_dict = load_pickle(ApiCommon.CL_IDX_FILE)
        rf_dict = load_pickle(ApiCommon.RF_IDX_FILE)
        cl_txt_f_in = open(ApiCommon.CL_TXT_FILE,"rb")
        rf_txt_f_in = open(ApiCommon.RF_TXT_FILE,"rb")
        cl_xml_f_in = open(ApiCommon.CL_XML_FILE,"rb")
        rf_xml_f_in = open(ApiCommon.RF_XML_FILE,"rb")

        t0 = datetime.now()

        rec_count = 0

    # -------------------------------------------------------
        if args[1]=="json":
    # -------------------------------------------------------
    #            <toto-list><toto>toto1</toto><toto>toto2</toto></toto-list>

            xmlstr="""
                <root>
                    <family reputation="bad">Dalton
                        <member-list complete="false">
                            <member>jack</member>
                            <member status="chief">jo</member>
                        </member-list>
                        <gun-list>
                            <gun>rifle</gun>
                            <gun>kalash</gun>
                        </gun-list>
                        <bank-attack-list year="1999" />
                    </family>
                    
                </root>"""
            node = etree.fromstring(xmlstr)
            obj = get_json_object(node)
            str = json.dumps(obj, indent=2, sort_keys=True)
            #json.dumps(node, indent=2, sort_keys=True)
            print(str)
            sys.exit()

    # -------------------------------------------------------
        if args[1]=="release_info":
    # -------------------------------------------------------
            log_it("INFO:", release_info)
            delta = datetime.now() -t0

    # -------------------------------------------------------
        elif args[1]=="txt":
    # -------------------------------------------------------
            cl_records = list()
            rf_ids = set()
            for ac in args[2:]:
                cl = get_txt_cell_line(ac, cl_dict, cl_txt_f_in)
                cl_records.append(cl)
                cl_index = cl_dict[ac]
                for ref_id in cl_index["ref_list"]: rf_ids.add(ref_id)
            # now display result
            rf_records = list()
            for rf_id in rf_ids:
                rf = get_txt_reference(rf_id, rf_dict, rf_txt_f_in)
                if rf is not None: rf_records.append(rf)

            delta = datetime.now() -t0
            rec_count = len(cl_records)
            for rec in cl_records: print(rec + "-------------")
            for rec in rf_records: print(rec + "-------------")

    # -------------------------------------------------------
        elif args[1]=="xml":
    # -------------------------------------------------------
            cl_nodes = list()
            rf_ids = set()
            # get list of cell line nodes and build set of referred publications
            for ac in args[2:]:
                cl = get_xml_cell_line(ac, cl_dict, cl_xml_f_in)
                cl_nodes.append(cl)
                cl_index = cl_dict[ac]
                for ref_id in cl_index["ref_list"]: rf_ids.add(ref_id)
            rf_nodes = list()
            # get list of referred publications nodes
            for rf_id in rf_ids:
                 rf = get_xml_reference(rf_id, rf_dict, rf_xml_f_in)
                 rf_nodes.append(rf)
            # build final xml
            main_node = etree.Element("Cellosaurus")
            cll_node = etree.SubElement(main_node, "cell-line-list")
            for cl_node in cl_nodes: cll_node.append(cl_node)
            pul_node = etree.SubElement(main_node, "publication-list")
            for rf_node in rf_nodes: pul_node.append(rf_node)
            # now display result
            delta = datetime.now() -t0
            rec_count = len(cl_nodes)
            print(etree.tostring(main_node, encoding="utf-8", pretty_print=True).decode('utf-8'))

    # -------------------------------------------------------
        elif args[1]=="children":
    # -------------------------------------------------------
            ac_list = args[2:]
            output  = "--- tsv ---\n"
            output += get_tsv_multi_cell_children(ac_list, cl_dict)
            output += "--- txt ---\n"
            output += get_txt_multi_cell_children(ac_list, cl_dict)
            output += "--- xml ---\n"
            node = get_xml_multi_cell_children(ac_list, cl_dict)
            output += etree.tostring(node, encoding="utf-8", pretty_print=True).decode('utf-8')
            output += "--- json ---\n"
            obj = get_json_multi_cell_children(ac_list, cl_dict)
            output += json.dumps(obj, indent=2, sort_keys=True)

            rec_count = len(ac_list)
            delta = datetime.now() - t0
            print(output)

    # -------------------------------------------------------
        print("Retrieved " + str(rec_count) + " record(s)", "duration [ms] :", delta.total_seconds()*1000 )

        cl_txt_f_in.close()
        rf_txt_f_in.close()
        cl_xml_f_in.close()
        rf_xml_f_in.close()

        sys.exit()

        cl_index = cl_dict[ac]
        print("xml_pos", cl_index["xml_pos"], "xml_size", cl_index["xml_size"])
        print("txt_pos", cl_index["txt_pos"], "txt_size", cl_index["txt_size"])
        print("len(ref_list)", len(cl_index["ref_list"]), "len(child_list)", len(cl_index["child_list"]))
        print("Ref list")
        for ref in cl_index["ref_list"]: print(ref)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Access to data via XML files and dictionaries
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # get main cell line record by seeking xml file
        f_in = open(ApiCommon.CL_XML_FILE,"rb")
        f_in.seek(cl_index["xml_pos"])
        bytes = f_in.read(cl_index["xml_size"])
        tree = etree.parse(BytesIO(bytes))
        cl = tree.getroot()
        print(etree.tostring(cl, encoding="utf-8", pretty_print=True).decode('utf-8'))
        f_in.close()

        # get references of cell line by seeking xml file
        f_in = open(ApiCommon.RF_XML_FILE,"rb")
        for id in cl_index["ref_list"]:
            rf_index = rf_dict[id]
            f_in.seek(rf_index["xml_pos"])
            bytes = f_in.read(rf_index["xml_size"])
            tree = etree.parse(BytesIO(bytes))
            rf = tree.getroot()
            print(etree.tostring(rf, encoding="utf-8", pretty_print=True).decode('utf-8'))
        f_in.close()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Access to data via TXT files and dictionaries
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        f_in = open(ApiCommon.CL_TXT_FILE,"rb")
        f_in.seek(cl_index["txt_pos"])
        bytes = f_in.read(cl_index["txt_size"])
        rec = bytes.decode("utf-8")
        print(rec)
        f_in.close()

        # get references of cell line by seeking txt file
        f_in = open(ApiCommon.RF_TXT_FILE,"rb")
        for id in cl_index["ref_list"]:
            rf_index = rf_dict[id]
            f_in.seek(rf_index["txt_pos"])
            bytes = f_in.read(rf_index["txt_size"])
            ref = bytes.decode("utf-8")
            print(ref)
        f_in.close()

        # get children list
        print("child list:")
        for child in cl_index["child_list"]:
            print(child)
        print("END child list")



    # # - - - - - - - - - - - - - - - - - - - - - - - -
    # # random access to xml elements stored in file
    # # - - - - - - - - - - - - - - - - - - - - - - - -
    # access_count = 100
    # t0 = datetime.now()
    # f_in = open("xml.serialized","rb")
    # cl_list = list()
    # for k in cl_dict: cl_list.append(k)
    # for n in range(1,access_count):
    #     idx = random.randrange(0,len(cl_list))
    #     k = cl_list[idx]
    #     pos, size = cl_dict[k]
    #     print("Looking for", k, pos, size)
    #     f_in.seek(pos)
    #     bytes = f_in.read(size)
    #     tree = etree.parse(BytesIO(bytes))
    #     #cl = tree.getroot()
    #     els = tree.xpath("/cell-line/accession-list/accession[@type='primary']")
    #     print("Got",els[0].text)
    #     # prof we get the element back and its sub-components
    #     # print(cl.tag)
    #     # for el in cl: print(el.tag)
    #     # for k in cl.keys(): print(k, cl.get(k))
    # f_in.close()
    # delta = datetime.now() - t0
    # print(datetime.now(), "Access count:" , access_count, "duration:", round(delta.total_seconds(),3))


    print(datetime.now(), "end")
    sys.exit()
