from fastapi import FastAPI, Query, responses, Path, Request
#from fastapi import status, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Optional
#from typing import List
from pydantic import BaseModel
#from pydantic import Field as PydanticField

import uvicorn
from enum import Enum


#import os
#import sys
import json
import argparse
#import http.client
import datetime
#import pickle
#import traceback
from lxml import etree
import cellapi_builder as api
import ApiCommon
from ApiCommon import log_it, get_search_result_txt_header, get_format_from_headers
#from ApiCommon import get_properties
from fields_utils import FldDef
from fields_enum import Fields

import requests
#import json

from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
#from fastapi.openapi.docs import get_redoc_html
import urllib.parse

# ----------------------------------------
# to be run first (in spyder only)
# ----------------------------------------
# import nest_asyncio
# nest_asyncio.apply()
# ----------------------------------------


# used for API documentation about errors
class ErrorMessage(BaseModel):
    message: str
    code: int

# used to give verified values for output format
class Format(str, Enum):
    jsn = "json"
    xml = "xml"
    txt = "txt"
    tsv = "tsv"


# simple multi media types resposne
four_media_types_responses = { "description": "Successful response", "content" : {
  "application/json": {},
  "text/plain": {},
  "application/xml": {},
  "text/tab-separated-values": {}
  }
}


# documentation for categories containng the API methods in the display, see also tags=["..."] below
tags_metadata = [
    {   "name": "General",
        "description": "Get general information about the current Cellosaurus release",
    },{ "name": "Cell lines",
        "description": "Get all or part of the information related to cell lines",
    }
]


# general documentation in the header of the page
app = FastAPI(
    title="Cellosaurus API",
    description="The <img src='static/cellosaurus.png' height='16px;' /><b>API</b> is dedicated to users who want to query and access programmatically the Cellosaurus.",
    version=ApiCommon.CELLAPI_VERSION,
    terms_of_service="https://www.expasy.org/terms-of-use",
#    contact={
#        "name": "Cellosaurus",
#        "email": "cellosaurus@sib.swiss", # requires a valid email address otherwise openapi.json fails to build
#    },
    license_info={
        "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "url": "https://creativecommons.org/licenses/by/4.0/",
    },
    docs_url = None, redoc_url = None,
    #docs_url="/docs", redoc_url="/alt/help",
    openapi_tags=tags_metadata,
    #root_path = "/bla/bla" # see https://fastapi.tiangolo.com/advanced/behind-a-proxy/
    )



# this is necessary for fastapi / swagger to know where the static files are served i.e. cellosaurus.ng above)
app.mount("/static", StaticFiles(directory="static"), name="static")

# local hosting of js / css for swagger and redocs
# see https://fastapi.tiangolo.com/advanced/extending-openapi/

@app.get("/help", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    print("calling custom_swagger_ui_html()")
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    #print("scope", scope)
    return get_swagger_ui_html(
        openapi_url=scope + app.openapi_url,
        title=app.title,
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url= scope + "/static/swagger-ui-bundle.js",
        swagger_css_url= scope + "/static/swagger-ui.css",
        swagger_favicon_url = scope + "/static/favicon32.png"
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# @app.get("/redoc", include_in_schema=False)
# async def redoc_html():
#     return get_redoc_html(
#         openapi_url=app.openapi_url,
#         title=app.title + " - ReDoc",
#         redoc_js_url="/static/redoc.standalone.js"
#     )



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.on_event("startup")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def startup_event():

    # load cellosaurus data
    global cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in, cl_xml_f_in, rf_xml_f_in, fldDef , release_info

    t0 = datetime.datetime.now()
    release_info = api.load_pickle(ApiCommon.RI_FILE)
    cl_dict = api.load_pickle(ApiCommon.CL_IDX_FILE)
    rf_dict = api.load_pickle(ApiCommon.RF_IDX_FILE)
    cl_txt_f_in = open(ApiCommon.CL_TXT_FILE,"rb")
    rf_txt_f_in = open(ApiCommon.RF_TXT_FILE,"rb")
    cl_xml_f_in = open(ApiCommon.CL_XML_FILE,"rb")
    rf_xml_f_in = open(ApiCommon.RF_XML_FILE,"rb")
    fldDef = FldDef(ApiCommon.FLDDEF_FILE)
    log_it("Read cl_dict.pickle" , len(cl_dict), "duration:", round((datetime.datetime.now() - t0).total_seconds(),3))

    log_it("app.statrtup() callback was called :-)" )


# see also https://github.com/tiangolo/fastapi/issues/50
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/release-info", name="Get release information in various formats",
         tags=["General"],
#         response_model=ReleaseInfo, # useful when examples are given but examples for XML dont work
         responses={ "200":four_media_types_responses})
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_release_info(
        request: Request,
        format: Optional[Format] = Query(
            default= None,
            example = "txt",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            )
        ):

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)

    # build and return response in appropriate format
    if format == "tsv":
        data = "version\tupdated\tnb-cell-lines\tnb-publications\n"
        data += release_info.get("version") + "\t"
        data += release_info.get("updated") + "\t"
        data += release_info.get("nb-cell-lines") + "\t"
        data += release_info.get("nb-publications") + "\n"
        return responses.Response(content=data, media_type="text/tab-separated-values")
    elif format == 'txt':
        data  = "version: " +release_info.get("version") + "; "
        data += "updated: " +release_info.get("updated") + "; "
        data += "nb-cell-lines: " +release_info.get("nb-cell-lines") + "; "
        data += "nb-publications: " +release_info.get("nb-publications") + "\n"
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        obj = {"Cellosausus": {"header": {"release": release_info}}}
        data = json.dumps(obj, sort_keys=True, indent=2)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        root_el = etree.Element("Cellosaurus")
        head_el = etree.SubElement(root_el, "header")
        rel_el = etree.SubElement(head_el, "release")
        rel_el.attrib["version"] = release_info.get("version")
        rel_el.attrib["updated"] = release_info.get("updated")
        rel_el.attrib["nb-cell-lines"] = release_info.get("nb-cell-lines")
        rel_el.attrib["nb-publications"] = release_info.get("nb-publications")
        data = etree.tostring(root_el, encoding="utf-8", pretty_print=True)
        return responses.Response(content=data, media_type="application/xml")



# see also https://github.com/tiangolo/fastapi/issues/50
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line/{ac}", name="Get cell line in various formats", tags=["Cell lines"] , responses={"200":four_media_types_responses, "404": {"model": ErrorMessage}})
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line(
        request: Request,
        ac: str = Path(
            default="CVCL_S151",
            example="CVCL_S151",
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines"
            ),
        format: Optional[Format] = Query(
            default= None,
            example = "txt",
            # title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            ),
        fld: Optional[list[Fields]] = Query(
            default = None,
            example=[],
            title = "Output fielfields",
            description="""Optional list of fields to return in the response.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="static/fields_help.html">here</a>.
            """
            ),
        fields: Optional[str] = Query(
            default = None,
            example="id,sy,cc,rx",
            title = "Output fields (alternate syntax)",
            description="""Optional list of fields to return in the response.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="static/fields_help.html">here</a>.
            """
            )

        ):

    # precedence of fld over fields
    if fld is not None: fields = fld

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)


    # check AC existence, see also parameter responses=... in the @app.get() annotation above
    if ac not in cl_dict:
        obj = {"code": 404, "message": "Item not found, ac: " + ac}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        return responses.Response(content=data, media_type="application/json", status_code=404)

    # build and return response in appropriate format
    if format == "tsv":
        data = api.get_tsv_multi_cell([ac], fields, fldDef, cl_dict, cl_txt_f_in)
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        prefixes = fldDef.get_prefixes(fields)
        data = api.get_txt_multi_cell([ac], prefixes, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell([ac], xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        obj = api.get_json_object(node)
        data = json.dumps(obj, sort_keys=True, indent=2)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell([ac], xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        data = etree.tostring(node, encoding="utf-8", pretty_print=True)
        return responses.Response(content=data, media_type="application/xml")




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cellapi/cell-line-children/{ac}.tsv", name="Get cell line children in TSV format", tags=["Cell lines"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cellapi_cell_line_children_tsv(
        ac: str = Path(
            default="CVCL_1922",
            example="CVCL_1922",
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines"
            )
        ):
    return get_cell_line_children(ac, "tsv")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line-children/{ac}.tsv", name="Get cell line children in TSV format", tags=["Cell line"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line_children_tsv(
        ac: str = Path(
            default="CVCL_1922",
            example="CVCL_1922",
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines"
            )
        ):
    return get_cell_line_children(ac, "tsv")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line-children/{ac}.txt", name="Get cell line children in text format", tags=["Cell line"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line_children_txt(
        ac: str = Path(
            default="CVCL_1922",
            example="CVCL_1922",
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines"
            )
        ):
    return get_cell_line_children(ac, "txt")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cell_line_children(ac, format):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if format is None or format == "": format = "tev"

    if format == "tsv":
        data = api.get_tsv_multi_cell_children([ac], cl_dict)
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        data = api.get_txt_multi_cell_children([ac], cl_dict)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        node = api.get_xml_multi_cell_children([ac], cl_dict)
        obj = api.get_json_object(node)
        data = json.dumps(obj, sort_keys=True, indent=2)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        node = api.get_xml_multi_cell_children([ac], cl_dict)
        data = etree.tostring(node, encoding="utf-8", pretty_print=True)
        return responses.Response(content=data, media_type="application/xml")




# see also https://fastapi.tiangolo.com/advanced/additional-responses/
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/search/cell-line" , name="Search cell lines", tags=["Cell lines"], responses={"200":four_media_types_responses, "400": {"model": ErrorMessage}})
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def search_cell_line(
        request: Request,
        q: str = Query(
            default="id:HeLa",
            example="id:HeLa",
            title="search query",
            description="Search query string using Solr synax"
            ),

        start: int = Query(
            default=0,
            example=0,
            title="start",
            description="Index of first item to retrieve in the search result list. See also <i>start</i> parameter in Solr synax"
            ),

        rows: int = Query(
            default=1000,
            example=10,
            title="rows",
            description="Number of items to retrieve from the search result list. See also <i>rows</i> in Solr synax"
            ),
        format: Optional[Format] = Query(
            default= None,
            example = "txt",
            title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            ),
        fld: Optional[list[Fields]] = Query(
            default = None,
            example=[],
            title = "Output fields",
            description="""Optional list of fields to return in the response.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="static/fields_help.html">here</a>.
            """
            ),
        fields: Optional[str] = Query(
            default = None,
            example="id,ac,sy,cc",
            title = "Output fields (alternate syntax)",
            description="""Optional list of fields to return in the response.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="static/fields_help.html">here</a>.
            """
            ),
        sort: Optional[str] = Query(
            default=None,
            example="group asc,sampling-site desc",
            title = "Sort order",
            description = """Optional field(s) determining the sort order of the search result.
            Every field name must be followed with a space and the sort direction (ASCending or DESCending).
            When multiple fields are used as the value of this parameter, they must be separated by a comma.
            All the files described <a href="static/fields_help.html">here</a> in are sortable. 
            When this parameter is undefined, the search result rows are sorted by relevance.
            """
            )
        ):

    # precedence of fld over fields
    if fld is not None: fields = fld

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)

    # solr_q = api.get_solr_formatted(q)
    # solr_sort = "score desc"
    # if sort is not None: solr_sort = app.get_solr_formatted(sort)

    # call solr service
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields="ac", sort=sort, start=start, rows=rows)
    headers = { "Accept": "application/json" }

    response = requests.get(url, params=params, headers=headers)
    obj = response.json()
    if response.status_code != 200:
        error_msg = ""
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        obj = {"code": response.status_code, "message": error_msg}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        return responses.Response(content=data, media_type="application/json", status_code=response.status_code)

    # now handle successful response
    meta = dict()
    obj["responseHeader"]["params"]["q"]=q           # query typed by API user
    meta["query"]=obj["responseHeader"]["params"]
    meta["numFound"]=obj["response"]["numFound"]
    meta["sort"]=sort
    meta["fields"]=fields
    meta["format"]=format
    # build a list ac from the solr result
    ac_list = list()
    items = obj["response"]["docs"]
    for item in items: ac_list.append(item["ac"])

    # use api methods to retrieve full / partial records in multiple formats
    if format == "tsv":
        data = api.get_tsv_multi_cell(ac_list, fields, fldDef, cl_dict, cl_txt_f_in)
        data = get_search_result_txt_header(meta) + data
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        prefixes = fldDef.get_prefixes(fields)
        #print("ac_list", ac_list)
        #print("prefixes", prefixes)
        data = api.get_txt_multi_cell(ac_list, prefixes, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in)
        data = get_search_result_txt_header(meta) + data
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell(ac_list, xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        obj = api.get_json_object(node)
        data = json.dumps(obj, sort_keys=True, indent=2)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell(ac_list, xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        data = etree.tostring(node, encoding="utf-8", pretty_print=True)
        return responses.Response(content=data, media_type="application/xml")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def basic_help(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    #print(">>> scope", scope, "version", request.app.version)

    # read HTML template
    f=open("basic_help.template.html","r")
    content = f.read()
    f.close()

    # build response and send it
    content = content.replace("$scope", scope).replace("$version",request.app.version)
    return responses.Response(content=content,media_type="text/html")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/search/form.html", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def search_form(request: Request, q: str = Query(
    default="id:HeLa",
    example="id:HeLa",
    title="search query",
    description="Search query string using Solr synax"
    ),
):

    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    print(">>> scope", scope)

    # read HTML template
    f=open("search_form.template.html","r")
    content = f.read()
    f.close()

    # set default query criterion if none
    if q is None or q == "": q = "id:HeLa"
    log_it("q", q)

    # send request to solr
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields="id", sort="id asc", rows=1000000)
    headers = { "Accept": "application/json" }

    # get response
    response = requests.get(url, params=params, headers=headers)
    obj = response.json()

    # handle errors
    if response.status_code != 200:
        error_msg = ""
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        numFound = 0
        idsFound = ["error_msg: " + error_msg,  "status_code: " + str(response.status_code) ]
    # handle success
    else:
        numFound = obj["response"]["numFound"]
        idsFound = list()
        for doc in obj["response"]["docs"]: idsFound.append(doc["id"])

    # build response and send it
    content = content.replace("$q", q.replace("\"", "&quot;"))
    content = content.replace("$numFound", str(numFound))
    content = content.replace("$idsFound", "\n".join(idsFound))
    content = content.replace("$scope", scope)


    return responses.Response(content=content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/fullsearch/form.html", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def fullsearch_form(
    request: Request, 
    q: str = Query(default="id:HeLa"),
    fields: str = Query(default="id,ac,ox"),
    sort: str = Query(default="score desc"),
    rows: int = Query(default=20),
):

    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""

    # set default query criterion if none
    if q is None or q == "": q = "id:HeLa"
    if fields is None or fields == "": fields = "id,ac,ox"
    if sort is None or sort == "": sort = "score desc"
    if rows is None or rows == 0: rows = 20

    # send request to solr
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields=fields, sort=sort, rows=rows)
    headers = { "Accept": "application/json" }

    print("url", url, "params", params)

    # get response
    response = requests.get(url, params=params, headers=headers)
    obj = response.json()
    # handle errors
    if response.status_code != 200:
        error_msg = ""
        obj = response.json()
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        numFound = 0
        idsFound = ["<tr><td>" + "error_msg: " + error_msg + "</td></td>" + "status_code: " + str(response.status_code) + "</tr></td>"]
    # handle success
    else:
        numFound = obj["response"]["numFound"]
        resultRows = list()
        # build table column headers by iterating on solr fields names
        # INFO: remember field names may differ from user known fields (see api.get_solr_formatted() ) 
        solr_fields=params["fl"] # get solr names of fields
        field_list = solr_fields.split(",")
        resultHeader=""
        for f in field_list: resultHeader += "<th>" + f + "</th>"
        resultHeader="<tr>" + resultHeader + "</tr>"

        # build table rows with results
        for doc in obj["response"]["docs"]: 
            columns = list()
            for field in field_list:
                value = doc.get(field.strip())
                if value is None: value = "-"
                if isinstance(value, list): value = " | ".join(value)
                columns.append("<td>" + value + "</td>")
            resultRows.append("<tr>" + "".join(columns) + "</tr>")

    # build response and send it
        # read HTML template
    f=open("fullsearch_form.template.html","r")
    content = f.read()
    f.close()

    content = content.replace("$q", q)
    content = content.replace("$fields", fields)
    content = content.replace("$sort", sort)
    content = content.replace("$rows", str(rows))
    content = content.replace("$numFound", str(numFound))
    content = content.replace("$resultRows", resultHeader + "".join(resultRows))
    content = content.replace("$scope", scope)

    return responses.Response(content=content,media_type="text/html")


# INFO
# building tsv with solr
# https://solr.apache.org/guide/8_8/response-writers.html
# add parameters wt=csv & csv.separator=%09


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    parser = argparse.ArgumentParser(description="Run a simple HTTP proxy for cellapi services")
    parser.add_argument("-s", "--server", default="localhost", help="IP address on which the server listens")
    parser.add_argument("-p", "--port", type=int, default=8088, help="port on which the server listens")
    parser.add_argument("-w", "--workers", default="1", help="Number of processes to run in parallel")
    parser.add_argument("-r", "--root_path", default="/", help="root path")
    parser.add_argument("-l", "--reload", default=True, help="reload on source code change")
    args = parser.parse_args()

    api.get_solr_search_url(verbose=True)
    print("args.root_path",args.root_path)
    uvicorn.run("main:app", port=args.port, host=args.server, reload=args.reload, log_level="info",  root_path=args.root_path) #, workers=args.workers )
