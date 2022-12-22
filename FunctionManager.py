import re
import requests
import json
from bs4 import BeautifulSoup as bs

class FunctionManager():
    '''Class that defines some helper functions for the App'''
    def __init__(self):
        pass
    @staticmethod
    def get_ns_string(raw_targets, selected_target, inp_dict, ID = None,targetMode="class"):
        '''Returns the NodeShape String together with the namespace and the target iri of the selected target 
        selected_target = selected_target.split(" ")[0]
        target_iri = [i for i in raw_targets if re.search(".*#+"+selected_target+"$",i) != None][0]
        shacl_target = ""
        namespace = ""
        for i in inp_dict:
            if inp_dict[i] in target_iri:
                namespace = i+":"
                shacl_target = namespace+selected_target
        '''

        namespace = selected_target.split("(")[1].split(")")[0]

        selected_target = selected_target.split(" ")[0]

        shacl_target = namespace+":"+selected_target

        targets = [i for i in raw_targets if re.search(".*#+"+selected_target+"$",i) != None]

        target_iri = [t for t in targets if inp_dict[namespace] in t][0]

        if targetMode == "class":
            if ID == None:
                ns_string = "[\n\ta sh:NodeShape ;\n\tsh:nodeKind sh:BlankNodeOrIRI;\n\tsh:targetClass "+shacl_target+" ;\n] ."
            else:
                ns_string = ID+"\n\ta sh:NodeShape ;\n\tsh:nodeKind sh:BlankNodeOrIRI;\n\tsh:targetClass "+shacl_target+" ."
        elif targetMode == "subject":
            if ID == None:
                ns_string = "[\n\ta sh:NodeShape ;\n\tsh:targetSubjectsOf "+shacl_target+" ;\n] ."
            else:
                ns_string = ID+"\n\ta sh:NodeShape ;\n\tsh:targetSubjectsOf "+shacl_target+" ."
        elif targetMode == "object":
            if ID == None:
                ns_string = "[\n\ta sh:NodeShape ;\n\tsh:targetObjectsOf "+shacl_target+" ;\n] ."
            else:
                ns_string = ID+"\n\ta sh:NodeShape ;\n\tsh:targetObjectsOf "+shacl_target+" ."

        return (ns_string, namespace, target_iri)
    
    @staticmethod
    def get_ps_string(raw_properties, selected_property,id, inp_dict):
        
        namespace = selected_property.split("(")[1].split(")")[0]
        
        selected_property = selected_property.split(" ")[0]

        shacl_property = namespace+":"+selected_property

        properties = [i for i in raw_properties if re.search(".*#+"+selected_property+"$",i) != None]

        property_iri = [p for p in properties if inp_dict[namespace] in p][0]

        ps_string = id+" a sh:PropertyShape ;\n\tsh:path "+shacl_property+" ."
        
        return (ps_string, namespace, property_iri)
    
    @staticmethod
    def get_namespace(inp_dict, raw_items, selected_item,offset=0):
        item_iri = [i for i in raw_items if re.search(".*#+"+selected_item+"$",i) != None][offset]
        namespace = str(None)
        for i in inp_dict:
            if inp_dict[i] in item_iri:
                namespace = i
        
        return namespace



    @staticmethod
    def get_path_string(window_txt, inp_dict, raw_properties,selected_path, hasID=False):
        
        namespace = selected_path.split("(")[1].split(")")[0]+":"
        selected_path = selected_path.split(" ")[0]

        if not hasID:
            b = window_txt.split(";\n] .")
            b.insert(-1,"\n\tsh:property [\n\t\ta sh:PropertyShape ;\n\t\tsh:path "+namespace+selected_path+" ; ] ;\n] .")
            return ";".join(b[0:-1])      
        else:
            x1 = window_txt.split(".")
            x1.insert(-1,"\n\t"+"sh:property [\n\t\ta sh:PropertyShape ;\n\t\tsh:path "+namespace+selected_path+" ; ] .")
            return ";".join(x1[0:-1])

    
    @staticmethod
    def getNewPathPropertyString(window_txt,inp_dict, raw_properties,selected_property, hasID=False):

        namespace = selected_property.split("(")[1].split(")")[0]+":"
        selected_property = selected_property.split(" ")[0]
       
        if not hasID: 
            tmp = window_txt.split("#")
            c = tmp[0].split("; ] ;\n")
            c.insert(-1,"\tsh:property [\n\t\ta sh:PropertyShape ;\n\t\tsh:path "+namespace+selected_property+" ; ] ;\n] .")
            d = " ; ] ;\n".join(c[0:-1])
            tmp[0] = d
            return "\n#".join(tmp)
        else:
            tmp = window_txt.split("#")
            x3 = tmp[0].split("; ] .")
            x3.insert(-1,"\n\t"+"sh:property [\n\t\ta sh:PropertyShape ;\n\t\tsh:path "+namespace+selected_property+" ; ] .")
            d = "; ] ;".join(x3[0:-1])
            tmp[0] = d
            return "\n#".join(tmp)      
    
    @staticmethod
    def get_property_iri(selected_property,inp_dict, raw_properties):
        namespace = selected_property.split("(")[1].split(")")[0]
        
        selected_property = selected_property.split(" ")[0]

        properties = [i for i in raw_properties if re.search(".*#+"+selected_property+"$",i) != None]

        property_iri = [p for p in properties if inp_dict[namespace] in p][0]

        return property_iri

    @staticmethod
    def getXSDDatatypes():
        # Making a GET request
        r = requests.get('https://www.w3.org/TR/rdf-mt/#dtype_interp')
        # Parsing the HTML
        s = bs(r.content, 'html.parser')
        #scrape the list of currently supported xml schema datatypes and return it as a python list
        return [re.sub("xsd:","",i.text) for i in s.select('td.ruletable a[href*="xmlschema"] code')]
    
    @staticmethod
    def getlangTags():
        #returns the language tags according to RFC 5646
        #source: https://gist.githubusercontent.com/msikma/8912e62ed866778ff8cd/raw/c0cb604e5a9832b1ec16e3ec4d03f8845182110f/rfc5646-language-tags.js
        return dict({
            'af': 'Afrikaans',
            'af-ZA': 'Afrikaans (South Africa)',
            'ar': 'Arabic',
            'ar-AE': 'Arabic (U.A.E.)',
            'ar-BH': 'Arabic (Bahrain)',
            'ar-DZ': 'Arabic (Algeria)',
            'ar-EG': 'Arabic (Egypt)',
            'ar-IQ': 'Arabic (Iraq)',
            'ar-JO': 'Arabic (Jordan)',
            'ar-KW': 'Arabic (Kuwait)',
            'ar-LB': 'Arabic (Lebanon)',
            'ar-LY': 'Arabic (Libya)',
            'ar-MA': 'Arabic (Morocco)',
            'ar-OM': 'Arabic (Oman)',
            'ar-QA': 'Arabic (Qatar)',
            'ar-SA': 'Arabic (Saudi Arabia)',
            'ar-SY': 'Arabic (Syria)',
            'ar-TN': 'Arabic (Tunisia)',
            'ar-YE': 'Arabic (Yemen)',
            'az': 'Azeri (Latin)',
            'az-AZ': 'Azeri (Latin) (Azerbaijan)',
            'az-Cyrl-AZ': 'Azeri (Cyrillic) (Azerbaijan)',
            'be': 'Belarusian',
            'be-BY': 'Belarusian (Belarus)',
            'bg': 'Bulgarian',
            'bg-BG': 'Bulgarian (Bulgaria)',
            'bs-BA': 'Bosnian (Bosnia and Herzegovina)',
            'ca': 'Catalan',
            'ca-ES': 'Catalan (Spain)',
            'cs': 'Czech',
            'cs-CZ': 'Czech (Czech Republic)',
            'cy': 'Welsh',
            'cy-GB': 'Welsh (United Kingdom)',
            'da': 'Danish',
            'da-DK': 'Danish (Denmark)',
            'de': 'German',
            'de-AT': 'German (Austria)',
            'de-CH': 'German (Switzerland)',
            'de-DE': 'German (Germany)',
            'de-LI': 'German (Liechtenstein)',
            'de-LU': 'German (Luxembourg)',
            'dv': 'Divehi',
            'dv-MV': 'Divehi (Maldives)',
            'el': 'Greek',
            'el-GR': 'Greek (Greece)',
            'en': 'English',
            'en-AU': 'English (Australia)',
            'en-BZ': 'English (Belize)',
            'en-CA': 'English (Canada)',
            'en-CB': 'English (Caribbean)',
            'en-GB': 'English (United Kingdom)',
            'en-IE': 'English (Ireland)',
            'en-JM': 'English (Jamaica)',
            'en-NZ': 'English (New Zealand)',
            'en-PH': 'English (Republic of the Philippines)',
            'en-TT': 'English (Trinidad and Tobago)',
            'en-US': 'English (United States)',
            'en-ZA': 'English (South Africa)',
            'en-ZW': 'English (Zimbabwe)',
            'eo': 'Esperanto',
            'es': 'Spanish',
            'es-AR': 'Spanish (Argentina)',
            'es-BO': 'Spanish (Bolivia)',
            'es-CL': 'Spanish (Chile)',
            'es-CO': 'Spanish (Colombia)',
            'es-CR': 'Spanish (Costa Rica)',
            'es-DO': 'Spanish (Dominican Republic)',
            'es-EC': 'Spanish (Ecuador)',
            'es-ES': 'Spanish (Spain)',
            'es-GT': 'Spanish (Guatemala)',
            'es-HN': 'Spanish (Honduras)',
            'es-MX': 'Spanish (Mexico)',
            'es-NI': 'Spanish (Nicaragua)',
            'es-PA': 'Spanish (Panama)',
            'es-PE': 'Spanish (Peru)',
            'es-PR': 'Spanish (Puerto Rico)',
            'es-PY': 'Spanish (Paraguay)',
            'es-SV': 'Spanish (El Salvador)',
            'es-UY': 'Spanish (Uruguay)',
            'es-VE': 'Spanish (Venezuela)',
            'et': 'Estonian',
            'et-EE': 'Estonian (Estonia)',
            'eu': 'Basque',
            'eu-ES': 'Basque (Spain)',
            'fa': 'Farsi',
            'fa-IR': 'Farsi (Iran)',
            'fi': 'Finnish',
            'fi-FI': 'Finnish (Finland)',
            'fo': 'Faroese',
            'fo-FO': 'Faroese (Faroe Islands)',
            'fr': 'French',
            'fr-BE': 'French (Belgium)',
            'fr-CA': 'French (Canada)',
            'fr-CH': 'French (Switzerland)',
            'fr-FR': 'French (France)',
            'fr-LU': 'French (Luxembourg)',
            'fr-MC': 'French (Principality of Monaco)',
            'gl': 'Galician',
            'gl-ES': 'Galician (Spain)',
            'gu': 'Gujarati',
            'gu-IN': 'Gujarati (India)',
            'he': 'Hebrew',
            'he-IL': 'Hebrew (Israel)',
            'hi': 'Hindi',
            'hi-IN': 'Hindi (India)',
            'hr': 'Croatian',
            'hr-BA': 'Croatian (Bosnia and Herzegovina)',
            'hr-HR': 'Croatian (Croatia)',
            'hu': 'Hungarian',
            'hu-HU': 'Hungarian (Hungary)',
            'hy': 'Armenian',
            'hy-AM': 'Armenian (Armenia)',
            'id': 'Indonesian',
            'id-ID': 'Indonesian (Indonesia)',
            'is': 'Icelandic',
            'is-IS': 'Icelandic (Iceland)',
            'it': 'Italian',
            'it-CH': 'Italian (Switzerland)',
            'it-IT': 'Italian (Italy)',
            'ja': 'Japanese',
            'ja-JP': 'Japanese (Japan)',
            'ka': 'Georgian',
            'ka-GE': 'Georgian (Georgia)',
            'kk': 'Kazakh',
            'kk-KZ': 'Kazakh (Kazakhstan)',
            'kn': 'Kannada',
            'kn-IN': 'Kannada (India)',
            'ko': 'Korean',
            'ko-KR': 'Korean (Korea)',
            'kok': 'Konkani',
            'kok-IN': 'Konkani (India)',
            'ky': 'Kyrgyz',
            'ky-KG': 'Kyrgyz (Kyrgyzstan)',
            'lt': 'Lithuanian',
            'lt-LT': 'Lithuanian (Lithuania)',
            'lv': 'Latvian',
            'lv-LV': 'Latvian (Latvia)',
            'mi': 'Maori',
            'mi-NZ': 'Maori (New Zealand)',
            'mk': 'FYRO Macedonian',
            'mk-MK': 'FYRO Macedonian (Former Yugoslav Republic of Macedonia)',
            'mn': 'Mongolian',
            'mn-MN': 'Mongolian (Mongolia)',
            'mr': 'Marathi',
            'mr-IN': 'Marathi (India)',
            'ms': 'Malay',
            'ms-BN': 'Malay (Brunei Darussalam)',
            'ms-MY': 'Malay (Malaysia)',
            'mt': 'Maltese',
            'mt-MT': 'Maltese (Malta)',
            'nb': 'Norwegian (Bokm?l)',
            'nb-NO': 'Norwegian (Bokm?l) (Norway)',
            'nl': 'Dutch',
            'nl-BE': 'Dutch (Belgium)',
            'nl-NL': 'Dutch (Netherlands)',
            'nn-NO': 'Norwegian (Nynorsk) (Norway)',
            'ns': 'Northern Sotho',
            'ns-ZA': 'Northern Sotho (South Africa)',
            'pa': 'Punjabi',
            'pa-IN': 'Punjabi (India)',
            'pl': 'Polish',
            'pl-PL': 'Polish (Poland)',
            'ps': 'Pashto',
            'ps-AR': 'Pashto (Afghanistan)',
            'pt': 'Portuguese',
            'pt-BR': 'Portuguese (Brazil)',
            'pt-PT': 'Portuguese (Portugal)',
            'qu': 'Quechua',
            'qu-BO': 'Quechua (Bolivia)',
            'qu-EC': 'Quechua (Ecuador)',
            'qu-PE': 'Quechua (Peru)',
            'ro': 'Romanian',
            'ro-RO': 'Romanian (Romania)',
            'ru': 'Russian',
            'ru-RU': 'Russian (Russia)',
            'sa': 'Sanskrit',
            'sa-IN': 'Sanskrit (India)',
            'se': 'Sami',
            'se-FI': 'Sami (Finland)',
            'se-NO': 'Sami (Norway)',
            'se-SE': 'Sami (Sweden)',
            'sk': 'Slovak',
            'sk-SK': 'Slovak (Slovakia)',
            'sl': 'Slovenian',
            'sl-SI': 'Slovenian (Slovenia)',
            'sq': 'Albanian',
            'sq-AL': 'Albanian (Albania)',
            'sr-BA': 'Serbian (Latin) (Bosnia and Herzegovina)',
            'sr-Cyrl-BA': 'Serbian (Cyrillic) (Bosnia and Herzegovina)',
            'sr-SP': 'Serbian (Latin) (Serbia and Montenegro)',
            'sr-Cyrl-SP': 'Serbian (Cyrillic) (Serbia and Montenegro)',
            'sv': 'Swedish',
            'sv-FI': 'Swedish (Finland)',
            'sv-SE': 'Swedish (Sweden)',
            'sw': 'Swahili',
            'sw-KE': 'Swahili (Kenya)',
            'syr': 'Syriac',
            'syr-SY': 'Syriac (Syria)',
            'ta': 'Tamil',
            'ta-IN': 'Tamil (India)',
            'te': 'Telugu',
            'te-IN': 'Telugu (India)',
            'th': 'Thai',
            'th-TH': 'Thai (Thailand)',
            'tl': 'Tagalog',
            'tl-PH': 'Tagalog (Philippines)',
            'tn': 'Tswana',
            'tn-ZA': 'Tswana (South Africa)',
            'tr': 'Turkish',
            'tr-TR': 'Turkish (Turkey)',
            'tt': 'Tatar',
            'tt-RU': 'Tatar (Russia)',
            'ts': 'Tsonga',
            'uk': 'Ukrainian',
            'uk-UA': 'Ukrainian (Ukraine)',
            'ur': 'Urdu',
            'ur-PK': 'Urdu (Islamic Republic of Pakistan)',
            'uz': 'Uzbek (Latin)',
            'uz-UZ': 'Uzbek (Latin) (Uzbekistan)',
            'uz-Cyrl-UZ': 'Uzbek (Cyrillic) (Uzbekistan)',
            'vi': 'Vietnamese',
            'vi-VN': 'Vietnamese (Viet Nam)',
            'xh': 'Xhosa',
            'xh-ZA': 'Xhosa (South Africa)',
            'zh': 'Chinese',
            'zh-CN': 'Chinese (S)',
            'zh-HK': 'Chinese (Hong Kong)',
            'zh-MO': 'Chinese (Macau)',
            'zh-SG': 'Chinese (Singapore)',
            'zh-TW': 'Chinese (T)',
            'zu': 'Zulu',
            'zu-ZA': 'Zulu (South Africa)'
        })

    @staticmethod
    def getFlags():
        #returns the flags according to https://www.w3.org/TR/xpath-functions/#flags
        return dict({
            "s":"single-line mode",
            "m":"multi-line mode",
            "i":"case-insensitive mode",
            "x":"remove-whitespace mode",
            "q":"implicit-escape mode" 
        })

    @staticmethod
    def getAstreaShapes(ont_graph):
        #specify rest api url and request header
        api_url = "https://astrea.linkeddata.es/api/shacl/document"
        headers =  {"Content-Type":"application/json"}

        #the input is the ontology graph and its format as a json file
        ont_dict = {
            "ontology":str(ont_graph.serialize(format='turtle')),
            "serialisation" : "TURTLE"
        }

        #executing the post request
        response = requests.post(api_url,data=json.dumps(ont_dict),headers=headers)

        #the response content contains the shapes, serialized in turtle
        astrea_shapes = response.content

        return astrea_shapes
         
