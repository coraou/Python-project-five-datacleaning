
# coding: utf-8

# In[2]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney_sample_big.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Broadway", "Drive", "Plaza", "Square", "Circuit", "Highway", "Mall", 
            "Market", "Close", "Court", "Lane", "Road", "Parade", "Square", "Way", "Walk", 
            "Crescent", "Parkway","Esplanade", "Wolli"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "st": "Street",
            "Ave": "Avenue",
            "Avenuue": "Avenue",
            "Rd": "Road",
            "street": "Street",
            "Pl": "Place"
            }
big_names = [" Woolloomooloo", " Sydney", " marrickville"]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types



def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            name = name.replace(street_type,mapping[street_type])
    return name

def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            for big in big_names:
                if big in name:
                    name = name.replace(big,"").strip(',')
                    
    
            better_name = update_name(name, mapping)
            
            if name != better_name:
                print name, "=>", better_name
            

if __name__ == '__main__':
    test()

