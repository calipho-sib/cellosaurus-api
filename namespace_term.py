

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Term:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, ns, id, hidden=False):
        self.ns = ns; self.id = id; self.iri = ":".join([ns, id]); self.props = dict(); 
        self.hidden = hidden; self.composite_comment_already_built = False

    def __str__(self) -> str:
        return ":".join([self.ns, self.id])
    
    def __repr__(self) -> str:        
        return f"Term({self.iri}, {self.props})"

    def isA(self, owlType):
        value_set = self.props.get("rdf:type") or set()
        result = owlType in value_set
        #print(">>>", self.iri, result, owlType, "-- in ? --", value_set)
        return result


    def unwrap_xsd_string(self, str):
        tmp = str
        # remove left part of the wrapper
        if tmp.startswith("\"\"\""): tmp = tmp[3:]
        elif tmp.startswith("\""): tmp = tmp[1:]
        # remove right part of the wrapper
        if tmp.endswith("\"\"\"^^xsd:string"): tmp = tmp[:-15]
        elif tmp.endswith("\"^^xsd:string"): tmp = tmp[:-13]
        tmp = self.unescape_string(tmp)
        return tmp
        
    def unescape_string(self, str):
        str = str.replace("\\\\","\\")      # inverse of escape backslashes with double backslashes (\ => \\)
        str = str.replace("\\\"", "\"")     # inverse of escape double-quotes (" => \")
        return str



    def get_label_str(self):
        label_set = self.props.get("rdfs:label")
        # if is stored in props, return first item in set
        if label_set is not None and len(label_set) > 0:
            xsd_label = next(iter(label_set))
            return self.unwrap_xsd_string(xsd_label)
        # otherwise return default label built from id
        else:
            return Term.build_default_label(self.id)


    def build_default_label(id):
        # 1) insert space instead of "_" and on case change  
        chars = list()
        wasupper = False
        for ch in id:
            if ch.isupper() and not wasupper and len(chars)>0: chars.append(" "); chars.append(ch)
            elif ch == "_": chars.append(" ")
            else: chars.append(ch)
            wasupper = ch.isupper()
        sentence = "".join(chars).replace("  ", " ")
        words = sentence.split(" ")
        # 2) lower all words except first and those having all chars uppercase
        first = True
        new_words = list()
        for w in words:
            if first: first = False; new_words.append(w)
            else:
                allUpper = True
                for ch in w:
                    if ch.islower(): allUpper = False
                if allUpper: new_words.append(w)
                else: new_words.append(w.lower())
        return " ".join(new_words)
