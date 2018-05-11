
# coding: utf-8

# In[ ]:


import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney.osm"  # Replace this with your osm file
SAMPLE_FILE = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney_sample_big.osm"

k = 2 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# In[1]:


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import sys
sys.path.append("C:\\Users\\smasung\\.ipynb_checkpoints")
import schema1

SCHEMA = schema1.schema
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
OSM_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney_sample_big.osm"

expected = ["Street", "Avenue", "Boulevard", "Broadway", "Drive", "Plaza", "Square", "Circuit", "Highway", "Mall", 
            "Market", "Close", "Court", "Lane", "Road", "Parade", "Square", "Way", "Walk", 
            "Crescent", "Parkway","Esplanade", "Wolli"]
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "st": "Street",
            "Streett": "Street",
            "Ave": "Avenue",
            "Avenuue": "Avenue",
            "Rd": "Road",
            "street": "Street",
            "Pl": "Place"
            }
big_names = [" Woolloomooloo", " Sydney", " marrickville"]
big_numbers = [" Westfield Hornsby", " George St", " Pittwater Road"]
CHARNUM = re.compile(r'^[0-9]|[0-9]|[0-9]|[a-b]')  #change the capitalization of XXXa or XXXb, without changing the "a" or "b" in English words like "gate"
# Make sure the fields order in the csvs matches the column order in the sql table schema
NODES_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\big_sample\\nodes.csv"
NODE_TAGS_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\big_sample\\nodes_tags.csv"
WAYS_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\big_sample\\ways.csv"
WAY_NODES_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\big_sample\\ways_nodes.csv"
WAY_TAGS_PATH = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\big_sample\\ways_tags.csv"

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def audit_housenumber(number):
    if 'Lvl' in number:
        number = number.replace("Lvl","level")
    for big in big_numbers:
        if big in number:
            number = number.replace(big,"")
    if re.search(CHARNUM,number):
        number = number.replace("a","A")
        number = number.replace("b","B")
    return number

def audit_postalcode(code):
    if 'NSW' in code:
        code = code.replace("NSW","").strip()
    return code

def audit_street_type(name):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            name = name.replace(street_type,mapping[street_type])
        for big in big_names:
            if big in name:
                name = name.replace(big,"")
    return name

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    # YOUR CODE HERE
    if element.tag == 'node':
        for n in node_attr_fields:
            if n == "id" or n == "uid" or n== "changeset":
                node_attribs[n] = int(element.attrib[n])
            elif n == "lat" or n == "lon":
                node_attribs[n] = float(element.attrib[n])
            else:
                node_attribs[n] = element.attrib[n]
    
        for t in element.iter('tag'):
            tgs = {}
            if re.search(LOWER_COLON,t.attrib['k'])!= None:
                tgs['id'] = int(element.attrib['id'])
                tgs['type'] = t.attrib['k'][:t.attrib['k'].find(':')] 
                tgs['key'] = t.attrib['k'][t.attrib['k'].find(':'):].strip(':')
                if tgs['key'] == 'street':
                    tgs['value'] = audit_street_type(t.attrib['v'])
                elif tgs['key'] == 'postalcode':
                    tgs['value'] = audit_postalcode(t.attrib['v'])
                elif tgs['key'] == 'housenumber':
                    tgs['value'] = audit_housenumber(t.attrib['v'])
                else:
                    tgs['value'] = t.attrib['v']
            elif re.search(PROBLEMCHARS,t.attrib['k'])!= None:
                tgs = {}
            else:
                tgs['id'] = int(element.attrib['id'])
                tgs['type'] = 'regular'
                tgs['key'] = t.attrib['k']
                tgs['value'] = t.attrib['v']
            tags.append(tgs)
          
        return {'node': node_attribs, 'node_tags': tags}
        
    
    elif element.tag == 'way':
        for w in way_attr_fields:
            if w == 'id' or w == 'uid' or w== 'changeset':
                way_attribs[w] = int(element.attrib[w])
            else:
                way_attribs[w] = element.attrib[w]
            
        i = 0
        for w in element.iter('nd'):
            wn = {}
            wn['id'] = int(element.attrib['id'])
            wn['node_id'] = int(w.attrib['ref'])
            wn['position'] = i
            way_nodes.append(wn)
            i+=1
             
        for t in element.iter('tag'):
            tgs = {}
            if re.search(LOWER_COLON,t.attrib['k'])!= None:
                tgs['id'] = int(element.attrib['id'])
                tgs['type'] = t.attrib['k'][:t.attrib['k'].find(':')] 
                tgs['key'] = t.attrib['k'][t.attrib['k'].find(':'):].strip(':') 
                tgs['value'] = t.attrib['v']
            elif re.search(PROBLEMCHARS,t.attrib['k'])!= None:
                tgs = {}
            else:
                tgs['id'] = int(element.attrib['id'])
                tgs['type'] = 'regular'
                tgs['key'] = t.attrib['k']
                tgs['value'] = t.attrib['v']
            tags.append(tgs)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file,          codecs.open(WAYS_PATH, 'wb') as ways_file,         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
   

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)

