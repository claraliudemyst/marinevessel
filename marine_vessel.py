
# coding: utf-8

# # marine vessel

# In[273]:


import urllib.request
import json
from bs4 import *
import datetime
import pytz


def find_vessel(keyword):
    try:
        #search
        
        if not isinstance(keyword,int):
            keyword_st="%20".join(keyword.split())
        else:
            keyword_st=str(keyword)
            
        #keyword_st='414118000'
        url='https://www.marinetraffic.com/en/ais/index/search/all?keyword='+keyword_st
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        obj=urllib.request.Request(url=url,headers=headers)
        data = urllib.request.urlopen(obj).read()
        raw=BeautifulSoup(data, fromEncoding='utf-8')
        
        #get target url
        urlnew=''
        for i in raw.find_all('a',attrs={'class':"search_index_link"}):
            shipid=i.get('href').split('shipid:')[1].split('/')[0]
            mmsi=i.get('href').split('mmsi:')[1].split('/')[0]
            print(i,keyword_st==mmsi,shipid,mmsi)
            
            #keyword is a number
            if isinstance(keyword,int):
                if keyword_st==shipid or keyword_st==mmsi:
                    urlnew='https://www.marinetraffic.com'+i.get('href')
                    print(urlnew)
            else:
                if str.upper(i.get_text())==str.upper(keyword):
                    urlnew='https://www.marinetraffic.com'+i.get('href')
                    print(urlnew)
                    
         
        #get target data
        #if urlnew!='':
        obj=urllib.request.Request(url=urlnew,headers=headers)
        data = urllib.request.urlopen(obj).read()
        return BeautifulSoup(data, fromEncoding='utf-8')
    except:
        return "Result not found"
    
def get_vessel_info(soup):
    detail={'Vessel Name':soup.find('title').get_text().split(':')[1].split('(')[0]}
    for att in soup.find_all('div',attrs={'class': ["group-ib short-line","group-ib short-line vertical-offset-5"]}):
        detail[" ".join(att.find('span').get_text().split())]=att.find('b').get_text()
    return(detail)

def get_voyage_info(soup):
    time_time=[]
    location=[]

    #create departure and arrival list
    time_att=["Actual Time of Departure","Actual Time of Arrival"] 
    
    #create time list
    for t in soup.find_all('span',attrs={'class':"time-format hide-me"}):
        try:time_time.append(int(t.get_text().split()[0]))
        except:time_time.append('')
    
    #create location list
    for loc in soup.find_all('span',attrs={'class':"text-default text-darker"}):
        try:location.append(loc.get_text())
        except:location.append('')
            
    #voyage dic
    voyage_time={}
    voyage_loc={}

    for i in range(2):
        try:
            d=datetime.datetime.fromtimestamp(time_time[i])
            string_time = d.strftime("%Y-%m-%d %H:%M")
        except:
            string_time=''
            
        voyage_time[time_att[i]]=string_time
    try:
        voyage_loc['From']=location[0]
    except:
        voyage_loc['From']=' '
    try:
        voyage_loc['To']=location[1]
    except:
        voyage_loc['To']=' '
    
    #mt-table
    mt={}

    for i in soup.find_all('div',attrs={'class':"table-responsive mt-table"}): 
        mt_att=[]
        value=[]
        
        #mt attributes
        for att in i.find_all('td',style="width: 50%;"):
            #print(att.get_text())
            mt_att.append(att.get_text())
            
        #mt-value
        try:
            for val in i.find_all('b'):
                value.append(val.get_text())
        except:
            value=[]
        for j in range(len(mt_att)):
            if j<len(value):
                mt[mt_att[j]]=value[j]
            else:
                mt[mt_att[j]]=''
       
    return voyage_time,voyage_loc,mt

def get_position(soup):
    latest_position=soup.find('div',attrs={'class':"table-cell cell-full collapse-768",'style':"vertical-align: top"})
    latest_position_received=latest_position.find('div',attrs={'class':'group-ib'})
    latest_position_details=latest_position.find_all('div',attrs={'class':'vertical-offset-10 group-ib'})

    latest={}
    latest[latest_position_received.find('span').get_text()]=" ".join(latest_position_received.find('strong').get_text().split())
    for i in latest_position_details:
        latest[i.find('span').get_text()]=i.find('strong').get_text()

    return latest

def query(keyword):
    data=find_vessel(keyword)
    vessel=get_vessel_info(data)
    voyage=get_voyage_info(data)
    position=get_position(data)
    return vessel,voyage,position

