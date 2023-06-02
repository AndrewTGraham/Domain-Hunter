# Domain Hunter

# Count of domains to check per API call. 
# 500 is the max.
chunk_size = 500

# Price range in USD you are willing to pay for a domain.
min_price = 0
max_price = 1000000

import requests
import time
import json
import pandas as pd

with open('GodaddyKeys.txt') as f:
    GodaddyKeys = f.readlines()


api_key = GodaddyKeys[0].strip()
secret_key = GodaddyKeys[1].strip()
url = "https://api.godaddy.com/v1/domains/available"

# API key and secret are sent in the header
headers = {"Authorization" : "sso-key {}:{}".format(api_key, secret_key)}



df = pd.read_csv('unigram_freq.csv')

df['len']  = df['word'].str.len()

df=df.iloc[:100000]

df=df[df['len']>=6]

df['first5']=df['word'].str[:5]
df['last5']=df['word'].str[-5:]
df['firstoverlap']=df['first5'].str[-4:]
df['lastoverlap']=df['last5'].str[:4]
dffirst=df[['first5','firstoverlap','count']].copy(deep=True).rename(columns={'firstoverlap':'overlap','count':'firstcount'})
dflast=df[['last5','lastoverlap','count']].copy(deep=True).rename(columns={'lastoverlap':'overlap','count':'lastcount'})

dffirst=dffirst.groupby(['first5','overlap']).sum()
dffirst.reset_index(inplace=True)

dflast=dflast.groupby(['last5','overlap']).sum()
dflast.reset_index(inplace=True)

df = dffirst.merge(dflast,on='overlap',how='inner')
df['word']=df['first5']+df['last5'].str[-1]

df['priority']=df[['firstcount','lastcount']].min(axis=1)

df.sort_values('priority',ascending=False,inplace=True)

df.drop_duplicates('word',keep='first',inplace=True)

# all_domains = list(map('{}.com'.format, list(df[df['len']==11]['word'])))

all_domains = list(map('{}.com'.format, list(df['word'])))

# This function splits all domains into chunks
# of a given size
def chunks(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]
# Split the original array into subarrays
domain_chunks = list(chunks(all_domains, chunk_size))
 
# For each domain chunk (ex. 500 domains)
counter=0
found_domains = {}
for domains in domain_chunks:
    counter+=1
    # Get availability information by calling availability API
    availability_res = requests.post(url, json=domains, headers=headers)
    # Get only available domains with price range
    for domain in json.loads(availability_res.text)["domains"]:
        if domain["available"]:
            price = float(domain["price"])/1000000
            if price >= min_price and price <= max_price:
                print("{:30} : {:10}".format(domain["domain"], price))
                found_domains[domain["domain"]]=price
    print('Completed {} of {}'.format(str(counter),str(len(domain_chunks))),'-'*(30-(len(str(counter)+str(len(domain_chunks))))))
    # API call frequency should be ~ 30 calls per minute 
    time.sleep(2)