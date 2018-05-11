
# coding: utf-8

# In[2]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re

osm_file = open("C:\\Users\\smasung\\Desktop\\stu\\work\\project-five-sydney\\sydney_sample_big.osm", "r")

big_numbers = [" Westfield Hornsby", " George St", " Pittwater Road"]
CHARNUM = re.compile(r'^[0-9]|[0-9]|[0-9]|[a-b]')  #change the capitalization of XXXa or XXXb, without changing the "a" or "b" in English words like "gate"


def audit_housenumber(number):
    if 'Lvl' in number:
        number = number.replace("Lvl","level")
    for big in big_numbers:
        if big in number:
            number = number.replace(big,"")
    if re.search(CHARNUM,number):
        number = number.replace("a","A")
        number = number.replace("b","B")
                
            
             


