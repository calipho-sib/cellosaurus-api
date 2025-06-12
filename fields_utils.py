import datetime
from ApiCommon import CELLAPI_VERSION

class FldDef:

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, file_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if file_name is None: file_name = 'fields_def.txt'
        f_in = open(file_name)
        line_no=0
        fld_dic = dict()   # key = TG, value = field object
        name2cano = dict() # key = TG or SH, value = solr field name
        while True:
            line = f_in.readline()
            if line == "": break
            line_no +=1
            line = line.strip()
            if line == "": continue
            if line[0:1]=="#": continue
            if line.startswith("TG   "):
                key=line[5:].lower().strip()         # make sure key only uses low case
                cano = key.replace("-", "_")
                names = [key]
                prefixes = list()
                xpaths = list()
                help_blocks = list()
                shortname = None
            elif line.startswith("SH   "):
                shortname = line[5:]
                names.append(shortname)
            elif line.startswith("PR   "):
                prefixes.append(line[5:])
            elif line.startswith("XP   "):
                xpaths.append(line[5:])
            elif line.startswith("DE   "):
                help_blocks.append(line[5:].strip())
            elif line.startswith("//"):
                for name in names: name2cano[name] = cano
                fld_dic[key] = {"prefixes": prefixes, "xpaths": xpaths, 
                                "shortname": shortname, "help": " ".join(help_blocks)}
        f_in.close()
        self.fld_dic = fld_dic
        self.name2cano = name2cano


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keys(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.fld_dic.keys()


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def split_on_solr_special_chars(self, str):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # delimiters variable contains the list of solr special characters 
    # plus <space> appearing in solr q parameter as a delimiter
    # plus <comma> used in solr fl parameter
    # plus <\> which is the solr escape character
    # minus <-> because we also use it in field names so it requires a special treatement
    # <\> appears as python-escaped in delimiters string
    # <"> appears as python-escaped in delimiters string

        delimiters = "+&|!(){}[]^\"~*?:/ \\,"
        token = ""
        result = list()
        for ch in str:
            if ch in delimiters:                # case of delimiters
                if len(token) > 0: 
                    result.append(token)
                    token = ""
                result.append(ch)
            
            elif ch == "-" and token == "":     # case of "-" in front of a token
                result.append(ch) 
            else:                               # case of non delimiters and of "-" within a token
                token += ch
        if len(token) > 0: result.append(token)
        return result

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalize_solr_q(self, q):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if q is None: return None
        return self.normalize_solr(q, onlyBeforeColon=True)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalize_solr_fl(self, fl):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fl is None: return None
        return self.normalize_solr(fl, onlyBeforeColon=False).replace(" ", "")
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalize_solr_sort(self, sort_order):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if sort_order is None: return None
        return self.normalize_solr(sort_order, onlyBeforeColon=False)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def normalize_solr(self, q, onlyBeforeColon):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        parts = self.split_on_solr_special_chars(q)
        for idx in range(0, len(parts)):
            elem = parts[idx]
            cano = self.get_canonical_name(elem)
            #print(idx, elem, cano)
            if cano is not None:
                if not onlyBeforeColon or ((idx+1 < len(parts) and parts[idx+1]) == ":"):
                    parts[idx] = cano
        return "".join(parts)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_canonical_name(self, name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.name2cano.get(name.lower().strip())


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_tag(self, field_name):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        cano = self.name2cano.get(field_name.lower().strip())
        return cano.replace("_","-") if cano is not None else None


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_tags(self, field_names):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if field_names is None: return None
        tags = list()
        for elem in field_names.split(","):
            tags.append(self.get_tag(elem) or elem.lower().strip())
        return ",".join(tags)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_prefixes(self, fld_tags):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fld_tags is None or fld_tags=="": return None

        tags = fld_tags if isinstance(fld_tags,list) else fld_tags.split(",")
        pr_set = set()
        for tag in tags:
            fld = self.fld_dic.get(tag.lower().strip())
            if fld is None: continue
            for pr in fld["prefixes"]:
                pr_set.add(pr)
        return pr_set


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_xpaths(self, fld_tags):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fld_tags is None or fld_tags=="": return None

        tags = fld_tags if isinstance(fld_tags,list) else fld_tags.split(",")
        xp_set = set()
        for tag in tags:
            fld = self.fld_dic.get(tag.lower())
            if fld is None: continue
            for xp in fld["xpaths"]:
                xp_set.add(xp)
        return xp_set

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_description(self, tag):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if tag is None: tag==""
        rec = self.fld_dic.get(tag.lower().strip())
        descr = rec.get("help") if rec is not None else None
        return descr if descr is not None else "Sorry, no description"
        
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_shortname(self, tag):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if tag is None: tag==""
        rec = self.fld_dic.get(tag.lower().strip())
        shortname = rec.get("shortname") if rec is not None else None
        return shortname

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def build_enum(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        f_out = open("fields_enum.py", "w")
        f_out.write("#\n# Generated : " + datetime.datetime.now().isoformat().replace('T',' ')[:19] + "\n#\n\n")
        f_out.write("from enum import Enum\n\n")
        f_out.write("class Fields(str, Enum):\n")
        for k in self.fld_dic.keys():
            f_out.write("\t" + k.replace("-","_").upper() + " = \"" + k + "\"\n")
        f_out.write("\n\n")
        f_out.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_content_of_api_fields_page(self):
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # read HTML template
        f=open("html.templates/api-fields.template.html","r")
        template = f.read()
        f.close()
        
        # build help file from template and by iterating over elements in fld def
        rows = ""
        for tag in self.fld_dic.keys():
            #print("tag",tag)
            #print("descr",self.get_description(tag))
            descr = self.get_description(tag)
            short = self.get_shortname(tag) or "-"
            row_data = list()
            row_data.append("<tr>")
            row_data.append(f"""<td style="width:12%; padding-top:10px; padding-bottom:10px; vertical-align:middle;">{tag}</td>""")
            row_data.append(f"""<td style="width:7%; padding-top:10px; padding-bottom:10px; text-align:center; vertical-align:middle;">{short}</td>""")
            row_data.append(f"""<td style="width:80%; padding-top:10px; padding-bottom:10px; vertical-align:middle;">{descr}</td>""")
            row_data.append("</tr>")
            rows += "\n".join(row_data)
        content = template.replace("$rows", rows).replace("$version",CELLAPI_VERSION)
        return content
        # f_out = open("static/api-fields-help.template.html", "w")
        # f_out.write(content)
        # f_out.close()
        

# ===========================================================================================
if __name__ == "__main__":
# ===========================================================================================

    fldDef = FldDef(None)
    
    fldDef.build_enum()
    print("Built file fields_enum.py")
        
    print("End")

    if 1==2:
        print("--- Test prefixes for each tag")
        cd = FldDef(None)
        for k in cd.keys():
            for pr in cd.get_prefixes(k):
                print(k, "->", pr)
    
        print("--- Test getting prefixes of specific tags")
        s1 = cd.get_prefixes("IDSY,CC-group,RA")
        s2 = cd.get_prefixes(["IDSY","CC-group","RA"])
        s3 = cd.get_prefixes("IDSY")
        print(s1)
        print(s2)
        print(s3)

        print("--- Test getting xpaths of specific tags")
        s1 = cd.get_xpaths("IDSY,CC-group,RA")
        s2 = cd.get_xpaths(["IDSY","CC-group","RA"])
        s3 = cd.get_xpaths("IDSY")
        print(s1)
        print(s2)
        print(s3)

        print("--- Test names to canonical namesw")
        for name in cd.name2cano:
            print(name, "->", cd.name2cano[name])

        print("--- Test canonization")
        names = ["ID", "Id", "iD", "id", " id ", "genOme-anCEStry", "anc", "unknown-field"]
        for s in names: print(s, '->', cd.get_canonical_name(s))

        print("--- Test normalization of field names appearing before <colon>")
        queries = [
            "genome-ancestry:(misc OR time) AND anc:anc",
            "reg:\"ludwig institute\"~4",
            "happy:boy"
        ]
        for q in queries: print(q, "->", cd.normalize_solr_q(q) )

        print("--- Test normalization of field names appearing in solr fl parameter")
        solr_fl = "id,AC, miss , hla,misc"
        print(solr_fl, "->",  cd.normalize_solr_fl(solr_fl))

        print("--- Test normalization of field names appearing in solr sort parameter")
        solr_sort = "ANC desc, int asc, score desc"
        print(solr_sort, "->",  cd.normalize_solr_sort(solr_sort))