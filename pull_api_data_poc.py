# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 11:02:16 2017

@author: gf_admin
"""

import requests
import pandas as pd
#from requests.auth import HTTPDigestAuth
import json

import sqlite3
from sqlite3 import Error

# Replace with the correct URL
url = "https://etherscamdb.info/api/scams/"

# It is a good practice not to hardcode the credentials. So ask the user to enter credentials at runtime
myResponse = requests.get(url)
#print (myResponse.status_code)
db_file = "C:\\uppsala\demo.db"
# For successful API call, response code will be 200 (OK)
if(myResponse.ok):

    # Loading the response data into a dict variable
    # json.loads takes in only binary or string variables so using content to fetch binary content
    # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
    jData = json.loads(myResponse.content)

    print("The response contains {0} properties".format(len(jData)))
    print("\n")
    for key in jData:
        #print(str(key) + " : " + jData[key])
        print(key)
        #print(jData[key])
   
    if jData['success']:
        result = pd.DataFrame(jData['result'])
    
    columns = ['id', 'name', 'url', 'category', 'subcategory', 'description',
               'ip', 'nameservers', 'status' ]
    
    result = result[columns]
        
    result = result.fillna({
      'description': ' ',
      'ip': ' ',
      'nameservers': ' ',
    })
    
    result['nameservers'] = result['nameservers'].apply(lambda x: ','.join(map(str, x)))
    
    
    print(result.head(15))

    try:
        conn = sqlite3.connect(db_file)
                            
        pd.DataFrame.to_sql(result, con=conn, flavor=None, name='etherscamdb', 
                            schema=None, if_exists='replace', index=False, 
                            index_label=False, chunksize=None, dtype=None)

    
    except Error as e:
        print(e)
    finally:
        conn.commit()
        conn.close()    

else:
  # If response code is not ok (200), print the resulting http error code with description
    myResponse.raise_for_status()