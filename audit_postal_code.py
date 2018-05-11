
# coding: utf-8

# In[ ]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re

osm_file = open("C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney_sample_big.osm", "r")


postalcode = []

def is_postalcode(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_postalcode(elem):
            code = elem.attrib['v']
            if 'NSW' in code:
                code = code.replace("NSW","").strip()
            postalcode.append(code)
    print postalcode
             

if __name__ == '__main__':
    audit()

