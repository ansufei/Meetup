#Goal: Find the category, name, date and address of all the upcoming sport meetups in Shanghai

#List of matching groups
#Detail of the upcoming events for these groups
#You will need your own meetup access key (log in on meetup and collect your key at: https://secure.meetup.com/meetup_api/key/)

#mykey=

import requests
import json
import pandas as pd

#Find the list of matching groups
#The meetup API indicates how to formulate html requests, e.g. https://www.meetup.com/meetup_api/docs/find/groups/

#Find the id of the "Sports&Outdoors" category
r_cat=requests.get('https://api.meetup.com/2/categories?key=key&sign=true')
json_cat=r_cat.json()
json_cat
df_cat=pd.DataFrame(json_cat['results'])
df_cat.loc[df_cat['shortname'] == 'Sports','id']

#Find the zipcode of Shanghai
r_loc=requests.get('https://api.meetup.com/find/locations?query=Shanghai&key=mykey&sign=true')
json_loc=r_loc.json()
json_loc

#pd.read_json(‘url_address’) simplifies the extraction and returns a dataframe.
pd.read_json('https://api.meetup.com/find/locations?query=Shanghai&key=mykey&sign=true')

r_sport=requests.get('https://api.meetup.com/find/groups?category=32&lon=121.47&lat=31.23&key=mykey&sign=true')
json_sport=r_sport.json()
with open('json_sport.txt', 'w') as outfile:
    json.dump(json_sport, outfile)

#List of public events
#df_groups=pd.read_json('https://api.meetup.com/find/groups?category=32&lon=121.47&lat=31.23&key=mykey&sign=true')
#Send the request only once then save it to csv
#df_groups.to_csv('df_groups.csv')
list_groups=list(df_groups['urlname'])

def finished():
    return num_tries == 3
def find_events(urlname):
    num_tries = 0
    while not finished():
        print(urlname)
        r=requests.get('https://api.meetup.com/2/events?key=mykey&group_urlname='+urlname+'&sign=true')   
        try:
            j = r.json()
            #if j['errorCode']:
            #    raise RuntimeError(j['message'])
            return pd.DataFrame(j['results'])
        except ValueError:
            num_tries += 1
            if not finished():
                print("Event URL failed. Will retry...")
    raise RuntimeError("Error: Event URL failed.")

#events=pd.concat([find_events(urlname) for urlname in list_groups],ignore_index=True)
#events.head()
events.to_csv('events.csv')

events=pd.read_csv('events.csv')
events_group = pd.DataFrame(events['group'].tolist())['name']
events_filtered = events[['name','time']].join(events_group,rsuffix='_group')
events_filtered.head()

clean_venue=[{} if type(x)==float else x for x in events['venue'].tolist()]
events_venue=pd.DataFrame.from_records(clean_venue)[['address_1','name']]
events_filtered = events_filtered .join(events_venue,rsuffix='_venue')
events_filtered.head()

#Transform time into datetime
events_filtered.time=pd.to_datetime(events_filtered.time,unit='ms')
events_filtered.head()

#remove repetitions of the same event:
events_norepeat=events_filtered.drop_duplicates(subset=['name', 'name_group', 'address_1', 'name_venue'])
events_norepeat.shape