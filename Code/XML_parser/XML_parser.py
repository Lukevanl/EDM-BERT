from xml.etree import cElementTree as ET
import json
import re
import sys

def to_json(title, contents):
    dic = {
        'id': title,
        'contents': "".join([f"**PARAGRAPH** {c[0]}: {c[1]} " for c in contents if c[0] not in ["See Also","References"] and len(c[1]) > 100])
    }
    res = json.dumps(dic)
    #print(res)
    return res + '\n'

def get_title(title: str):
    """Returns the title in DBpedia format"""
    return f"<dbpedia:{title.replace(' ', '_')}>"

def split_into_paragraphs(text):
    """Split the wikipedia text into paragraphs. Returns a list with tuples with the name of a paragraph and the content"""
    paragraphs = re.split(r"==(\w|\s){2,100}==\s", text)
    paragraph_names = ["Abstract"] + [p.replace('=','') for p in re.findall(r"==.{2,100}==", text)]

    return zip(paragraph_names, paragraphs)

def filter_entities(content):
    #change [[entity]] into ENTITY/entity
    ent = re.findall(r"\[\[([\w\-\(\)\s]+)(\]\])", content)
    for entity in ent:
        ent_repl = entity[0].replace(' ', '_')
        replace = f"{entity[0]} ENTITY/{ent_repl}"
        content = re.sub("\[\[([\w\-\(\)\s]+)(\]\])", replace, content, 1) 

    #change [[entity1|entity2]] into ENTITY/entity
    ent = re.findall(r"\[\[([\w\-\(\)\s]+)\|([\w\-\(\)\s]+)(\]\])", content)
    for entity in ent:
        ent_repl = entity[0].replace(' ', '_')
        replace = f"{entity[0]} ENTITY/{ent_repl}"
        content = re.sub("\[\[([\w\-\(\)\s]+)\|([\w\-\(\)\s]+)(\]\])", replace, content, 1)

    #change [[wikt:entity]] into ENTITY/entity
    ent = re.findall(r'\[\[(wikt:)([\w\-\(\)\s]+)(\]\])', content)
    for entity in ent:
        ent_repl = entity[1].replace(' ', '_')
        replace = f"{entity[1]} ENTITY/{ent_repl}"
        content = re.sub("\[\[(wikt:)([\w\-\(\)\s]+)]]", replace, content, 1) 

    #change [[wikt:entity1|entity2]] into ENTITY/entity
    ent = re.findall(r'\[\[(wikt:)([\w\-\(\)\s]+)\|([\w\-\(\)\s]+)\]\]', content)
    for entity in ent:
        ent_repl = entity[1].replace(' ', '_')
        replace = f"{entity[1]} ENTITY/{ent_repl}"
        content = re.sub("\[\[(wikt:)([\w\-\(\)\s]+)\|([\w\-\(\)\s]+)\]\]", replace, content, 1)  

    return content

def cleanup_paragraph(paragraph):
    title, content = paragraph
    # regexes = ['(\{\{([\s\S]*?)\}\})', '(\[(http)([\s\S]*?)\"])', '((<ref)([\s\S]*?)(/ref>))', '((\<\!\-\-)([\s\S]*?)(\-\-\>))', '((&lt;)|(<)|(&gt;)|(>))', "(\[\[(File:)([\s\S]*?)\]\])", "(\[\[(Image:)([\s\S]*?)\]\])", "(\[\[(Category:)([\s\S]*?)\]\])"]
    # content = re.sub("|".join(regexes), "", content)
    # Alles in 1 regex stoppen is NIET sneller
    content = re.sub(r"\{\|(.|\n)*?\|\}", "", content)
    content = re.sub(r'\{\{([\s\S]*?)\}\}', "", content)
    content = re.sub(r'\[(http)([\s\S]*?)\]', "", content)
    content = re.sub(r'(<ref)([\s\S]*?)(/ref>)', "", content)
    content = re.sub(r"(\<\!\-\-)([\s\S]*?)(\-\-\>)", "", content)
    content = re.sub(r'(&lt;)|(<)|(&gt;)|(>)', "", content)
    content = re.sub(r"\[\[(File:)([\s\S]*?)\]\]", "", content) 
    content = re.sub(r"\[\[(Image:)([\s\S]*?)\]\]", "", content)
    content = re.sub(r"\[\[(Category:)([\s\S]*?)\]\]", "", content)
    content = re.sub(r'(\n)+\*?', " ", content)
    content = filter_entities(content)
    return (title, content)

def parse_content(content):
    paragraphs = split_into_paragraphs(content)
    return [cleanup_paragraph(paragraph) for paragraph in paragraphs]
    


def parse(XMLfile, list_of_titles, output_file):
    results = 0
    tree = ET.parse(XMLfile)
    root = tree.getroot()
    with open(output_file, "w") as f:
        for elem in list(root):
            if (elem.tag[-4:] == "page"):
                title = elem.find('title').text
                content = elem.find('revision').find('text').text
                if ((content is not None) and content[:1] != "#"): #Filter out empty pages (redirects)
                    dbpedia_title = get_title(title)
                    if (dbpedia_title in list_of_titles):
                        f.write(to_json(dbpedia_title, parse_content(content)))
                        results += 1
    return results

def parse_tsv(file, pos):
    result = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            result.append(re.split("\n|\t", line)[0])
        return result


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} wiki.xml entities.tsv outputfolder")
        XMLfile = "wikipedia_extract.xml"
        tsv_file = "abstract_extract.tsv"
        output_file = "results.json"
        print(f"Now using defaults: {sys.argv[0]} {XMLfile} {tsv_file} {output_file}")
    else:
        XMLfile = sys.argv[1]
        tsv_file = sys.argv[2]
        output_folder = sys.argv[3]
        output_file = f"{output_folder}/{XMLfile.split('/')[-1]}.json"
        
    list_of_titles = parse_tsv(tsv_file, 0) #TODO, get list of entities of Emma
    result = parse(XMLfile, list_of_titles, output_file)
    
    
