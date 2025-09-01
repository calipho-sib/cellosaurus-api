from fastapi import FastAPI, Query, responses, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
#from fastapi import status, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Optional
#from typing import List
from pydantic import BaseModel
#from pydantic import Field as PydanticField
from urllib.parse import urlencode
import uvicorn
from enum import Enum
from namespace_registry import NamespaceRegistry
from starlette.middleware.base import BaseHTTPMiddleware


import os
#import sys
import json
import argparse
#import http.client
import datetime
#import pickle
#import traceback
from lxml import etree, html
import cellapi_builder as api
import ApiCommon
from api_platform import ApiPlatform
from ApiCommon import log_it, get_search_result_txt_header, get_search_result_txt_header_as_lines, get_format_from_headers
#from ApiCommon import get_properties
from fields_utils import FldDef
from fields_enum import Fields
from scripts.html_builder import HtmlBuilder

import requests
#import json

from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
#from fastapi.openapi.docs import get_redoc_html,
import urllib.parse

from gunicorn import glogging

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



json_type_responses = { "description": "Successful response", "content" : { "application/json": {} } }


# simple multi media types response
four_media_types_responses = { "description": "Successful response", "content" : {
  "application/json": {},
  "text/plain": {},
  "application/xml": {},
  "text/tab-separated-values": {}
  }
}

class ThreeFormat(str, Enum):
    jsn = "json"
    txt = "txt"
    tsv = "tsv"

three_media_types_responses = { "description": "Successful response", "content" : {
  "application/json": {},
  "text/plain": {},
  "text/tab-separated-values": {}
  }
}


# for some reason, rdf_is_visible, a global variable used as a parameter value in some @app.get(...) 
# must be declared and set before the @app.get(...) methods
rdf_is_visible = (os.getenv("RDF_IS_VISIBLE","False").upper() == "TRUE")
log_it("INFO:", "reading / getting default for env variable", f"RDF_IS_VISIBLE={rdf_is_visible}")
platform_key = os.getenv("PLATFORM_KEY","prod").lower()
log_it("INFO:", "reading / getting default for env variable", f"PLATFORM_KEY={platform_key}")
platform = ApiPlatform(platform_key)
ns_reg = NamespaceRegistry(platform)


subns_dict = dict()
for ns in [ns_reg.cvcl, ns_reg.xref, ns_reg.orga, ns_reg.pub, ns_reg.cello, ns_reg.db ]:
  subdir = ns.url.split("/")[-2]
  #print(">>> subdir:", subdir)
  subns_dict[subdir] = subdir

SubNs = Enum('SubNs', subns_dict)


class RdfFormat(str, Enum):
    ttl = "ttl"
    rdf = "rdf"
    n3 = "n3"
    jsonld = "jsonld"
    html = "html"

format2mimetype = {
    "ttl": "text/turtle",
    "rdf": "application/rdf+xml",
    "n3": "application/n-triples",
    "jsonld": "application/ld+json",
    "html": "text/html"
}

rdf_media_types_responses = { "description": "Successful response", "content" : {
    "text/turtle": {},
    "application/rdf+xml": {},
    "application/n-triples": {},
    "application/ld+json": {},
    "text/html": {},
  }
}


# documentation for categories containng the API methods in the display, see also tags=["..."] below
tags_metadata = [
    {   "name": "General",
        "description": "Get general information about the current Cellosaurus release",
    },{ "name": "Cell lines",
        "description": "Get all or part of the information related to cell lines",
    }]
if rdf_is_visible:
    tags_metadata.append({ "name": "RDF", "description": "RDF description of entities" })




class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        #log_it(">>> no cache", request.url)
        return response


# general documentation in the header of the page
app = FastAPI(
    title="Cellosaurus API methods",
    description="This API is dedicated to users who want to query and access programmatically Cellosaurus data.",
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
    # root_path = "/bla/bla" # see https://fastapi.tiangolo.com/advanced/behind-a-proxy/
    # root_path can be passed to fastapi from uvicorn as an argument (see __main__ below) 
    # but cannot be passed from gunicorn unless a custom worker class is created
    # see https://github.com/Midnighter/fastapi-mount/tree/root-path
    # but a simple ENV variable or config file can also be used to set root_path directly 
    # here in the FastAPI c'tor
    )


#
# Adds a Cache-control: no-cache header in response
# see CacheControlMiddleware class above
#
# With this setting, perplexity.ai says:
# FastAPI will always resend a fresh response with status 200 for your own routes if you only set Cache-Control: no-cache 
# and do not implement validation headers like ETag or Last-Modified or handle conditional requests. The no-cache directive forces the 
# browser to revalidate with the server, but unless your server checks the client's cache validation headers and returns a 
# 304 Not Modified when appropriate, FastAPI will simply generate and send a new response with status 200 every time
#
# It seems that the header Cache-Control: no-cache is also sent by CacheControlMiddleware for static resources whatever the response status (200, 304).
# Browsers seem to send If-Not_Modified-Since and If-None-Match headers which are properly handled by FastAPI
# The best "trick" to make sure cache is handled properly on browsers is to update the timestamp of resource files befaore each release
#
# Conclusion: we don't use CacheControlMiddleware class
#  
# app.add_middleware(CacheControlMiddleware)
#


# local hosting of js / css for swagger and redocs
# see https://fastapi.tiangolo.com/advanced/extending-openapi/

# Note: 
# Local copy of old swagger ui because is not compatible with new openai syntax is not used anymore
# Does not work with current json generated by fastapi.
# Local copy of swagger css modified by me is not used anymore by swagger generated page... but still used by api-quick-start and api-fields pages

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# historical routes with permanent redirect
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/help-methods", include_in_schema=False)
async def redirect_to_new_route():
    return RedirectResponse(url="/api-methods", status_code=301)

@app.get("/help-fields", include_in_schema=False)
async def redirect_to_new_route():
    return RedirectResponse(url="/api-fields", status_code=301)

@app.get("/fullsearch-form", include_in_schema=False)
async def redirect_to_new_route():
    return RedirectResponse(url="/api-search-form", status_code=301)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# active routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/api-methods", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    print("calling custom_swagger_ui_html()")
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    #print("scope", scope)
    html_response = get_swagger_ui_html(
        openapi_url=scope + app.openapi_url,
        title=app.title,
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        #swagger_js_url= scope + "/static/swagger-ui-bundle.js", # see note above
        #swagger_css_url= scope + "/static/swagger-ui.css",      # see note above
        swagger_favicon_url = scope + "/static/favicon32.png"
    )
 
    # now add navigation to the swagger page generated by FastAPI
    content_tree = html.fromstring(html_response.body.decode())
    # build a new HTTP response with amended content
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return HTMLResponse(content=final_content, status_code=200)


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
    global cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in, cl_xml_f_in, rf_xml_f_in, fldDef , release_info, clid_dict, htmlBuilder 
    global rdf_is_visible, platform, ns_reg

    t0 = datetime.datetime.now()
    release_info = api.load_pickle(ApiCommon.RI_FILE)
    cl_dict = api.load_pickle(ApiCommon.CL_IDX_FILE)
    rf_dict = api.load_pickle(ApiCommon.RF_IDX_FILE)
    cl_txt_f_in = open(ApiCommon.CL_TXT_FILE,"rb")
    rf_txt_f_in = open(ApiCommon.RF_TXT_FILE,"rb")
    cl_xml_f_in = open(ApiCommon.CL_XML_FILE,"rb")
    rf_xml_f_in = open(ApiCommon.RF_XML_FILE,"rb")
    fldDef = FldDef(ApiCommon.FLDDEF_FILE)
    clid_dict = api.get_clid_dic(fldDef)
    htmlBuilder = HtmlBuilder(platform)
    
    # Customizing uvicorn native log is done below in __main__()
    # Note: log_it() is self-made, unrelated to fastAPI / uvicorn /gunicorn logging system
    log_it("INFO:", "Read cl_dict.pickle" , len(cl_dict), duration_since=t0)
    log_it("INFO:", "app.stattup() callback was called :-)" )



# see also https://github.com/tiangolo/fastapi/issues/50
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/release-info", name="Get release information in various formats",
         tags=["General"],
#         response_model=ReleaseInfo, # useful when examples are given but examples for XML dont work
         responses={ "200":four_media_types_responses})
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_release_info(
        request: Request,
        format: Format = Query(
            default= None,
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            )
        ):

    t0 = datetime.datetime.now()
    # precedence of format over request headers
    #print("format", format)
    if format is None: format = get_format_from_headers(request.headers) # this might return "html" which is not suitable here
    #print("format", format)
    if format is None or format == "html": format = "json"
    #print("format", format)

    # build and return response in appropriate format
    if format == "tsv":
        data = "version\tupdated\tnb-cell-lines\tnb-publications\n"
        data += release_info.get("version") + "\t"
        data += release_info.get("updated") + "\t"
        data += release_info.get("nb-cell-lines") + "\t"
        data += release_info.get("nb-publications") + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="text/tab-separated-values")
    elif format == 'txt':
        data  = "version: " +release_info.get("version") + "; "
        data += "updated: " +release_info.get("updated") + "; "
        data += "nb-cell-lines: " +release_info.get("nb-cell-lines") + "; "
        data += "nb-publications: " +release_info.get("nb-publications") + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        obj = {"Cellosaurus": {"header": {"release": release_info}}}
        data = json.dumps(obj, sort_keys=True, indent=2)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
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
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/xml")



# see also https://github.com/tiangolo/fastapi/issues/50
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line/{ac}", name="Get cell line in various formats", tags=["Cell lines"] , responses={"200":four_media_types_responses, "404": {"model": ErrorMessage}})
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line(
        request: Request,
        ac: str = Path(        
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines. Example: 'CVCL_S151'"
            ),
        format: Format = Query(
            default= None,
            # title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            ),
        fld: list[Fields] = Query(
            default = None,
            title = "Output fields",
            description="""Optional list of fields to return in the response.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="api-fields">here</a>.
            """
            ),
        fields: str = Query(
            default = None,
            title = "Output fields (alternate syntax)",
            description="""Optional list of fields to return in the response.
            <i>fields</i> value is a comma-separated list of field tags or field shortnames.
            Examples: 'id,sy,cc,rx', 'id,ac,ox'.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="api-fields">here</a>.
            """
            )

        ):

    t0 = datetime.datetime.now()

    # ensure we have tag names and no shortnames in fields
    fields = fldDef.get_tags(fields)

    # precedence of fld over fields
    if fld is not None: fields = fld

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)
    if format is None or format == "html": format = "json"

    # check AC existence, see also parameter responses=... in the @app.get() annotation above
    if ac not in cl_dict:
        obj = {"code": 404, "message": "Item not found, ac: " + ac}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/json", status_code=404)

    # build and return response in appropriate format
    if format == "tsv":
        data = api.get_tsv_multi_cell([ac], fields, fldDef, cl_dict, cl_txt_f_in)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        prefixes = fldDef.get_prefixes(fields)
        data = api.get_txt_multi_cell([ac], prefixes, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell([ac], xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        obj = api.get_json_object(node)
        data = json.dumps(obj, sort_keys=True, indent=2)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell([ac], xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        data = etree.tostring(node, encoding="utf-8", pretty_print=True)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/xml")




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cellapi/cell-line-children/{ac}.tsv", name="Get cell line children in TSV format", tags=["Cell lines"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cellapi_cell_line_children_tsv(
        ac: str = Path(
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines. Example: 'CVCL_1922'"
            )
        ):
    return get_cell_line_children(ac, "tsv")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line-children/{ac}.tsv", name="Get cell line children in TSV format", tags=["Cell line"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line_children_tsv(
        ac: str = Path(
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines. Example: 'CVCL_1922'"
            )
        ):
    return get_cell_line_children(ac, "tsv")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/cell-line-children/{ac}.txt", name="Get cell line children in text format", tags=["Cell line"], include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_cell_line_children_txt(
        ac: str = Path(
            title="Cell line accession number",
            description="The accession number (field AC) is a unique identifier for cell-lines. Example: 'CVCL_1922'"
            )
        ):
    return get_cell_line_children(ac, "txt")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cell_line_children(ac, format):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if format is None or format == "": format = "tsv"

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
            title="search query",
            description="Search query string using Solr synax. Example: 'id:Hela'"
            ),

        start: int = Query(
            default=0,
            title="start",
            description="Index of first item to retrieve in the search result list. See also <i>start</i> parameter in Solr syntax."
            ),

        rows: int = Query(
            default=1000,
            title="rows",
            description="Number of items to retrieve from the search result list. See also <i>rows</i> in Solr synax, Example: '10'"
            ),
        format: Format = Query(
            default= None,
            title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/xml, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            ),
        fld: list[Fields] = Query(
            default = None,
            title = "Output fields",
            description="""Optional list of fields to return in the response.
            All the fields are returned in the response if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on content of fields <a href="api-fields">here</a>.
            """
            ),
        fields: str = Query(
            default = None,
            title = "Output fields (alternate syntax)",
            description="""Optional list of fields to return in the response.
            <i>fields</i> value is a comma-separated list of field tags or field shortnames.
            Examples: 'id,ac,sy,cc', 'id,ac,ox'.
            All the fields are returned if undefined.
            Values passed in parameter <i>fld</i> takes precedence over values passed in parameter <i>fields</i>.
            More information on fields <a href="api-fields">here</a>.
            """
            ),
        sort: str = Query(
            default=None,
            title = "Sort order",
            description = """Optional field(s) determining the sort order of the search result.
            Every field name must be followed with a space and the sort direction (ASCending or DESCending).
            When multiple fields are used as the value of this parameter, they must be separated by a comma.
            Example: 'group asc,derived-from-site desc'
            All the fields described <a href="api-fields">here</a> in are sortable. 
            When this parameter is undefined, the search result rows are sorted by relevance.
            """
            )
        ):

    t0 = datetime.datetime.now()

    # ensure we have tag names and no shortnames in fields
    fields = fldDef.get_tags(fields)

    # precedence of fld over fields
    if fld is not None: fields = fld

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)
    if format is None or format=="html": format = "json"

    # call solr service
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields="ac", sort=sort, start=start, rows=rows)
    headers = { "Accept": "application/json" }
    print("url...:", url)
    print("params: ", params)
    response = requests.get(url, params=params, headers=headers)
    obj = response.json()
    if response.status_code != 200:
        error_msg = ""
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        obj = {"code": response.status_code, "message": error_msg}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/json", status_code=response.status_code)

    # now handle successful response
    meta = dict()
    obj["responseHeader"]["params"]["q"]=q           # query typed by API user
    meta["QTime"]=obj["responseHeader"]["QTime"]
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
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        prefixes = fldDef.get_prefixes(fields)
        #print("ac_list", ac_list)
        #print("prefixes", prefixes)
        data = api.get_txt_multi_cell(ac_list, prefixes, cl_dict, rf_dict, cl_txt_f_in, rf_txt_f_in)
        data = get_search_result_txt_header(meta) + data
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell(ac_list, xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        obj = api.get_json_object(node)
        data = json.dumps(obj, sort_keys=True, indent=2)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="application/json")
    elif format == "xml":
        xpaths = fldDef.get_xpaths(fields)
        node = api.get_xml_multi_cell(ac_list, xpaths, cl_dict, rf_dict, cl_xml_f_in, rf_xml_f_in)
        data = etree.tostring(node, encoding="utf-8", pretty_print=True)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/xml")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/describe/entity/ontology/.{format}" , name="RDF description of the Cellosaurus ontology", tags=["RDF"], response_class=responses.Response, responses={"200":rdf_media_types_responses, "400": {"model": ErrorMessage}}, include_in_schema=rdf_is_visible)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def describe_onto(
        request: Request,
        format: RdfFormat = Path(
            title="Response format",
            description="Response output format"
            ),
        ):
    return describe_any(SubNs["ontology"], "", format, request)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/describe/entity/ontology/" , name="RDF description of the Cellosaurus ontology", tags=["RDF"], response_class=responses.Response, responses={"200":rdf_media_types_responses, "400": {"model": ErrorMessage}}, include_in_schema=rdf_is_visible)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def describe_onto(
        request: Request,
        format: RdfFormat = Query(
            default= None,
            title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/turtle, application/rdf+xml, application/n-triples, application/ld+json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the ld+json format."""
            )
        ):
    return describe_any(SubNs["ontology"], "", format, request)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO: decide whether we keep it or not
@app.get("/describe/entity/{prefix}/{id}.{format}" , name="RDF description of a cellosaurus entity", tags=["RDF"], response_class=responses.Response, responses={"200":rdf_media_types_responses, "400": {"model": ErrorMessage}}, include_in_schema=rdf_is_visible)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def describe_entity(
        request: Request,
        prefix: SubNs = Path(        
            title="Prefix of the entity ",
            description="The prefix (or namespace) of the entity IRI as defined in the Cellosaurus ontology, i.e. 'cello' in cello:CellLine"            
            ),
        id: str = Path(
            title="Identifier of the entity",
            description="The identifier of the entity in its namespace (prefix), i.e. 'CellLine' in cello:CellLine"
            ),
        format: RdfFormat = Path(
            title="Response format",
            description="Response output format"
            ),
        ):
    return describe_any(prefix, id, format, request)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/describe/entity/{prefix}/{id}" , name="RDF description of a cellosaurus entity", tags=["RDF"], response_class=responses.Response, responses={"200":rdf_media_types_responses, "400": {"model": ErrorMessage}}, include_in_schema=rdf_is_visible)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def describe_entity(
        request: Request,
        prefix: SubNs = Path(        
            title="Prefix of the entity ",
            description="The prefix (or namespace) of the entity IRI as defined in the Cellosaurus ontology, i.e. 'cello' in cello:CellLine"            
            ),
        id: str = Path(
            title="Identifier of the entity",
            description="The identifier of the entity in its namespace (prefix), i.e. 'CellLine' in cello:CellLine"
            ),
        format: RdfFormat = Query(
            default= None,
            title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/turtle, application/rdf+xml, application/n-triples, application/ld+json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the ld+json format."""
            )
        ):
    return describe_any(prefix, id, format, request)




def describe_any(dir, ac, format, request):
    t0 = datetime.datetime.now()
    log_it("INFO", f"called describe_any(dir=\"{dir.value}\", ac=\"{ac}\")")

    # precedence of format over request headers (does NOT work from swagger page !!! but of from curl)
    #print(">>>> format 1", format, format== RdfFormat.jsonld)
    #print(request.headers)
    if format is None: format = get_format_from_headers(request.headers)
    #print(">>>> format 2", format, format== RdfFormat.jsonld)
    if format is None: format = RdfFormat.jsonld
    #print(">>>> format 3", format, format== RdfFormat.jsonld)

    # method to redirect to website in case of text/html Accept header
    # using the virtuoso x-nice-microdata instead was chosen, see below.
    # if format == RdfFormat.html:
    #     url = "https://www.cellosaurus.org/" + ac
    #     log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
    #     return responses.RedirectResponse(url=url, status_code=301) # 301: Permanent redirect

    sparql_service = platform.get_private_sparql_service_IRI()
    iri = f"<{platform.get_rdf_base_IRI()}/{dir.value}/{ac}>"
    query = f"""DEFINE sql:describe-mode "CBD" describe {iri}"""
    print("query:", query)
    payload = {"query": query}
    if format == RdfFormat.html: payload["format"] = "application/x-nice-microdata"
    mimetype = format2mimetype.get(format)
    headers = { "Content-Type": "application/x-www-form-urlencoded" , "Accept" : mimetype }    
    response = requests.post(sparql_service, data=urlencode(payload), headers=headers)
    log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
    return responses.Response(content=response.text, media_type=mimetype )



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/describe/model" , name="Typical triples found in Cellosaurus RDF", tags=["RDF"], response_class=responses.Response, responses={"200":json_type_responses, "400": {"model": ErrorMessage}}, include_in_schema=rdf_is_visible)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_model_description(request:Request):
    t0 = datetime.datetime.now()
    log_it("INFO", f"called describe/model")
    sparql_service = platform.get_private_sparql_service_IRI()
    query = """
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
    print("query:", query)
    payload = {"query": query}
    mimetype = "application/sparql-results+json"
    headers = { "Content-Type": "application/x-www-form-urlencoded" , "Accept" : mimetype }    
    response = requests.post(sparql_service, data=urlencode(payload), headers=headers)
    log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
    return responses.Response(content=response.text, media_type=mimetype )



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/fsearch/cell-line" , name="Quick search cell lines", tags=["Cell lines"], responses={"200":three_media_types_responses, "400": {"model": ErrorMessage}}, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def fsearch_cell_line(
        request: Request,
        q: str = Query(
            default="id:HeLa",
            title="Quick facet search query",
            description="Quick search query string using Solr synax"
            ),

        rows: int = Query(
            default=1000,
            title="rows",
            description="Number of items to retrieve from the search result list. See also <i>rows</i> in Solr synax"
            ),

        format: ThreeFormat = Query(
            default= "txt",
            title="Response format",
            description="""Use this parameter to choose the response output format.
            Alternatively you can also use the HTTP Accept header of your
            request and set it to either text/plain, text/tab-separated-values, application/json.
            If the format parameter is used, the accept header value is ignored.
            If both the format parameter and the Accept header are undefined, then the response will use the json format."""
            ),
        ):

    t0 = datetime.datetime.now()

    # precedence of format over request headers
    if format is None: format = get_format_from_headers(request.headers)
    if format is None: format = "json"

    fields = "ac,id"
    facet_field="id"
    sort = "score desc" # sort order of response / docs

    # call solr service for quick facet search
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields=fields, sort=sort, start=0, rows=rows)
    params["facet"] = "true"            # enables facet search
    params["facet.field"] = facet_field # solr field which concats id,ac and ox values
    params["facet.method"] = "fc"       # fastest method
    params["facet.sort"] = "index"      # sort order of id field: 'index' means alphabetically
    params["facet.limit"] = rows        # same role as rows when we read facet value list
    params["facet.mincount"] = 1        # to get only records matching query q
    params["rows"] = 1                  # we don't need document list, we get result from facet_fields
    # value on next line does not seem to change performance
    params["indent"] = "True"

    headers = { "Accept": "application/json" }
    print("url...:", url)
    print("params: ", params)
    response = requests.get(url, params=params, headers=headers)
    obj = response.json()
    #print(obj)
    if response.status_code != 200:
        error_msg = ""
        solr_error = obj.get("error")
        if solr_error is not None: error_msg = solr_error.get("msg")
        obj = {"code": response.status_code, "message": error_msg}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data, media_type="application/json", status_code=response.status_code)

    # now handle successful response
    meta = dict()
    obj["responseHeader"]["params"]["q"]=q           # query typed by API user
    meta["QTime"]=obj["responseHeader"]["QTime"]
    meta["query"]=obj["responseHeader"]["params"]
    meta["numFound"]=obj["response"]["numFound"]
    meta["sort"]=sort
    meta["fields"]=fields
    meta["format"]=format

    # init lines with header
    lines = get_search_result_txt_header_as_lines(meta) 

    # 1) have a look at response docs and see if we have an exact match on ac or id
    exact_match = False
    items = obj["response"]["docs"]
    if len(items)==1:
        item = items[0]
        #print("item", item)
        id = item["id"]
        lowid = id.lower()
        lowac = item["ac"].lower()
        lowq = q.lower()
        #print("found first", "<" + lowac + ">", "<" + lowid + ">", "lowq:", "<" + lowq + ">")
        if lowq == lowac or lowq == "ac:" + lowac or lowq == "as:" + lowac or lowq == "acas:" + lowac or lowq == "text:" + lowac: exact_match = True
        elif lowq == lowid or lowq == "id:" + lowid or lowq == "sy:" + lowid or lowq == "idsy:" + lowid or lowq == "text:" + lowid: exact_match = True
        #print("exact_match", exact_match)
    if exact_match:
        lines.append(clid_dict[id])

    # 2) retrieve id field values from facets
    items = obj["facet_counts"]["facet_fields"].get(facet_field) or []
    if exact_match:
        for idx in range(len(items)):
            item = items[idx]
            # skip item already set above in case of exact match
            if idx % 2 == 0 and item != id: lines.append(clid_dict[item]) 
    else:
        for idx in range(len(items)):
            item = items[idx]
            if idx % 2 == 0: lines.append(clid_dict[item]) 

    # use api methods to retrieve full / partial records in multiple formats
    if format == "tsv":
        data = "\n".join(lines)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/tab-separated-values")
    elif format == 'txt':
        data = "\n".join(lines)
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="text/plain")
    elif format == 'json':
        data={"response": "json not yet supported"}
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
        log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)
        return responses.Response(content=data,media_type="application/json")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_basic_help(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # print(">>> scope", scope, "version", request.app.version)
    # read HTML template
    content = htmlBuilder.get_file_content("html.templates/api-quick-start.template.html")
    # build response and send it
    content = content.replace("$scope", scope).replace("$version",request.app.version)
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/rdf-concept-hopper", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_rdf_concept_hopper(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # print(">>> scope", scope, "version", request.app.version)
    # read HTML template
    content = htmlBuilder.get_file_content("html.templates/rdf-concept-hopper.template.html")
    # build response and send it
    #content = content.replace("$base_IRI", platform.get_rdf_base_IRI()) # no variable to set so far
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content, media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/rdf-downloads", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_rdf_downloads(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # print(">>> scope", scope, "version", request.app.version)
    # read HTML template
    content = htmlBuilder.get_file_content("html.templates/rdf-downloads.template.html")
    # build response and send it
    #content = content.replace("$base_IRI", platform.get_rdf_base_IRI()) # no variable to set so far
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/rdf-dereferencing", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_help_resolver(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # print(">>> scope", scope, "version", request.app.version)
    # read HTML template
    content = htmlBuilder.get_file_content("html.templates/rdf-dereferencing.template.html")
    # build response and send it
    content = content.replace("$base_IRI", platform.get_rdf_base_IRI())
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/sparql-service", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_help_resolver(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    content = htmlBuilder.get_file_content("html.templates/sparql-service.template.html")
    # build response and send it
    content = content.replace("$base_IRI", platform.get_rdf_base_IRI())
    content = content.replace("$public_sparql_URI", platform.get_public_sparql_service_IRI())
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/sparql-editor", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_sparql_editor(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    #print(">>> scope", scope, "version", request.app.version)
    # read HTML template
    f=open("html.templates/sparql-editor.template.html","r")
    content = f.read()
    f.close()
    # build response and send it
    content = content.replace("$sparql_IRI", platform.get_public_sparql_service_IRI())
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/rdf-ontology", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_sparql_editor(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # print(">>> scope", scope, "version", request.app.version)
    # read original file, insert navgation header, and send it
    
    content = htmlBuilder.get_file_content("static/sparql/doc/index-en.html")     # the file generated by widoco
    content_tree = html.fromstring(content)
    htmlBuilder.fix_ontology_css_collisions(content_tree)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_favicon_link_to_head(content_tree)
    htmlBuilder.add_script_node_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# @app.get("/static/toto.txt", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# async def handle_toto(request: Request):
#     scope = request.scope.get("root_path")
#     if scope is None or scope == "/": scope = ""
#     #print(">>> scope", scope, "version", request.app.version)

#     content = "<html><head></head><body>Hello toto</body></html"
#     # build response and send it
#     content_tree = html.fromstring(content)
#     htmlBuilder.add_nav_css_link_to_head(content_tree)
#     htmlBuilder.add_nav_node_to_body(content_tree)
#     final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
#     return responses.Response(content=final_content,media_type="text/html")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/api-fields", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_help_fields(request: Request):
    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""
    # build response and send it
    content = fldDef.get_content_of_api_fields_page()
    content = content.replace("$scope", scope).replace("$version",request.app.version)
    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    
    return responses.Response(content=final_content,media_type="text/html")





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.get("/api-search-form", tags=["Cell lines"], response_class=responses.HTMLResponse, include_in_schema=False)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def fullsearch_form(
    request: Request, 
    q: str = Query(default="id:HeLa"),
    fields: str = Query(default="id,ac,ox"),
    sort: str = Query(default="score desc"),
    rows: int = Query(default=8),
):

    t0 = datetime.datetime.now()

    scope = request.scope.get("root_path")
    if scope is None or scope == "/": scope = ""

    # set default query criterion if none
    if q is None or q == "": q = "id:HeLa"
    if fields is None or fields == "": fields = "ac,id,ox"
    if sort is None or sort == "": sort = "score desc"
    if rows is None or rows == 0: rows = 8

    # make sure we have 'ac' field
    if "ac" not in fields.lower(): fields = "ac," + fields

    # send request to solr
    url = api.get_solr_search_url()
    params = api.get_all_solr_params(fldDef, query=q, fields=fields, sort=sort, rows=rows)
    headers = { "Accept": "application/json" }

    print("url...:", url)
    print("params:", params)

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
        # INFO: remember field names may differ from user known fields (see fldDef.normalize_solr_*() ) 
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
                if field.strip() == "ac":
                    lnk1 = "/cell-line/" + value + "?fields=" + fields + "&format=xml"
                    #lnk2 = "/cell-line/" + value + "?fields=" + "&format=xml"
                    columns.append(f"""<td><a target="_blank" href="{lnk1}">{value}</a></td>""")
                else:
                    columns.append("<td>" + value + "</td>")
            resultRows.append("<tr>" + "".join(columns) + "</tr>")

    # build response and send it
        # read HTML template
    f=open("html.templates/api-search-form.template.html","r")
    content = f.read()
    f.close()

    input_q = q.replace("\"", "&quot;")
    content = content.replace("$q", input_q)
    content = content.replace("$fields", fields)
    content = content.replace("$sort", sort)
    content = content.replace("$rows", str(rows))
    content = content.replace("$numFound", str(numFound))
    content = content.replace("$resultRows", resultHeader + "".join(resultRows))
    content = content.replace("$scope", scope)

    content_tree = html.fromstring(content)
    htmlBuilder.add_nav_css_link_to_head(content_tree)
    htmlBuilder.add_nav_node_to_body(content_tree)
    final_content = html.tostring(content_tree, pretty_print=True, method="html", doctype="<!DOCTYPE html>",  encoding="utf-8")    

    log_it("INFO:", "Processed" , request.url, "format", format, duration_since=t0)

    return responses.Response(content=final_content,media_type="text/html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# NOTE: mounting /static at the end of this file rather than just after app creation allows
# for app.get() methods defined above to override the default behaviour for static files directory
# see example app.get("/static/toto")

# serve files in ./static as if they were in ./static
# this is necessary for fastapi / swagger to know where the static files are served i.e. cellosaurus.ng above)
app.mount("/static", StaticFiles(directory="static"), name="static")

# serve files in ./static/sparql/doc as if they were in ./
# this is used for serving page "/rdf-ontology"
app.mount("/", StaticFiles(directory="static/sparql/doc"), name="widoco")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 



# INFO
# building tsv with solr
# https://solr.apache.org/guide/8_8/response-writers.html
# add parameters wt=csv & csv.separator=%09


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# the __main__ code is used when you run this program as below:
#
# $ python main.py -s $server -p $port -r $scope -l True
#
# In production main.py run from an external script invoking gunicorn,
# a multiprocess HTTP request handler, see api_service.sh
# requirements: pip3.x install "uvicorn[standard]" gunicorn
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #print("I was in __main__")

    parser = argparse.ArgumentParser(description="Run a simple HTTP proxy for cellapi services")
    parser.add_argument("-s", "--server", default="localhost", help="IP address on which the server listens")
    parser.add_argument("-p", "--port", type=int, default=8088, help="port on which the server listens")
    parser.add_argument("-w", "--workers", default="1", help="Number of processes to run in parallel")
    parser.add_argument("-r", "--root_path", default="/", help="root path")
    parser.add_argument("-l", "--reload", default=False, help="reload on source code change")
    args = parser.parse_args()

    api.get_solr_search_url(verbose=True)
    print("args.root_path",args.root_path)

    # add timestamp in logging system of uvicorn (does NOT work for gunicorn)
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] =  '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    log_config["formatters"]["default"]["fmt"] = '%(asctime)s %(levelprefix)s %(message)s'
    log_config["loggers"]["uvicorn.access"]["propagate"] = True
    # uvicorn is mono-process, see gunicorn usage in api_service.sh
    uvicorn.run("main:app", port=args.port, host=args.server, reload=args.reload, log_level="info", log_config=log_config, root_path=args.root_path) #, workers=args.workers )