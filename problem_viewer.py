#Design by JLL - Dynatrace
#########################################################################################################
#import re
import json
import requests
import calendar
import os
import urllib3
import csv
import time
import datetime
import os
import re
import sys

##################################
### Source from the problem API
##################################


tenant_source='https://xxx.com/e/<tenantid>'
token_source==<API_Token_GEtProblem>

##################################
### Target for the dataingest
##################################
        
tenant_target='https://xxx.com/e/<tenantid>'
token_target=<API_Token_WriteDataingest>


##################################
### variables
##################################
#disable the warning
urllib3.disable_warnings()

#API-ENV
API_PROBLEM='/api/v2/problems/'
API_INGEST='/api/v2/metrics/ingest'

PB=dict()
status=''


##################################
## GENERIC functions
##################################

def head_with_token(TOKEN):
    http_header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
    }
    return http_header
	
# generic function GET to call API with a given uri
def queryDynatraceAPI(uri,TOKEN):
    head=head_with_token(TOKEN)
    jsonContent = None
    #print(uri)
    try:
        response = requests.get(uri,headers=head,verify=False)
        # For successful API call, response code will be 200 (OK)
        if(response.ok):
            if(len(response.text) > 0):
                jsonContent = json.loads(response.text)
        else:
            jsonContent = json.loads(response.text)
            print(jsonContent)
            errorMessage = ''
            if(jsonContent['error']):
                errorMessage = jsonContent['error']['message']
                print('Dynatrace API returned an error: ' + errorMessage)
            jsonContent = None
            raise Exception('Error', 'Dynatrace API returned an error: ' + errorMessage)
            status='failed'            
    except :
        status='failed'

    return jsonContent

# generic function POST to call API with a given uri
def postDynatraceAPI(uri, payload,TOKEN):
    head=head_with_token(TOKEN)
    jsonContent = None
    status='success'
    #print(uri)
    try:
        response = requests.post(uri,headers=head,verify=False, json=payload)
        if(response.ok):
            if(len(response.text) > 0):
                jsonContent = json.loads(response.text)
        else:
            jsonContent = json.loads(response.text)
            print(jsonContent)
            errorMessage = ''
            if (jsonContent['error']):
                errorMessage = jsonContent['error']['message']
                print('Dynatrace API returned an error: ' + errorMessage)
            jsonContent = None
            raise Exception('Error', 'Dynatrace API returned an error: ' + errorMessage)
            status='failed'
    except :
         status='failed'
    #print(jsonContent,status)
    #For successful API call, response code will be 200 (OK)
    return (jsonContent,status)


# generic function PUT to call API with a given uri
def putDynatraceAPI(uri, payload,TOKEN):
    head=head_with_token(TOKEN)
    jsonContent = None
    #print(uri)
    status='success'
    try:
        response = requests.put(uri,headers=head,verify=False, json=payload)
        if(response.ok):
            if(len(response.text) > 0):
                jsonContent = json.loads(response.text)
        else:
            jsonContent = json.loads(response.text)
            print(jsonContent)
            errorMessage = ''
            if (jsonContent['error']):
                errorMessage = jsonContent['error']['message']
                print('Dynatrace API returned an error: ' + errorMessage)
            jsonContent = None
            raise Exception('Error', 'Dynatrace API returned an error: ' + errorMessage)
            status='failed'
    except :
         status='failed'
    # For successful API call, response code will be 200 (OK)

    return (jsonContent,status)

# generic function del to call API with a given uri
def delDynatraceAPI(uri,TOKEN):
    head=head_with_token(TOKEN)
    jsonContent = None
    #print(uri)
    status='success'
    try:
        response = requests.delete(uri,headers=head,verify=False)
        if(response.ok):
            if(len(response.text) > 0):
                jsonContent = json.loads(response.text)
        else:
            jsonContent = json.loads(response.text)
            print(jsonContent)
            errorMessage = ''
            if (jsonContent['error']):
                errorMessage = jsonContent['error']['message']
                print('Dynatrace API returned an error: ' + errorMessage)
            jsonContent = None
            raise Exception('Error', 'Dynatrace API returned an error: ' + errorMessage)
            status='failed'
    except :
         status='failed'
    # For successful API call, response code will be 200 (OK)

    return (jsonContent,status)

##################################
### INFO functions###
##################################

# info problem tenant_source
def info_pb(TENANT,TOKEN):
    uri=TENANT+API_PROBLEM+'?pageSize=500&from=now-2h&to=now&Api-Token='+TOKEN
    PB_DIC=dict()
    #print(uri)
    datastore = queryDynatraceAPI(uri,TOKEN)
    count_open=0
    count_closed=0
    #print(datastore)
    if datastore != []:
        apilist = datastore['problems']
        count=datastore['totalCount']
        for entity in apilist:
            value_mz=False
            if entity['managementZones'] != []:
                title=entity['status']+",title="+entity['title'].lower().replace(" ","_").split("/")[0].split("(")[0]
                if title[len(title)-1] == "_":
                    title=title[:-1]
                for mz in entity['managementZones'] :
                    if mz['name'].startswith("p_"):
                        #si plusieurs management zone creer multimanagement zone
                        key=("problem.open,status="+entity['status']+",title="+title+",severitylevel="+entity['severityLevel'].lower().replace(" ","_")+",impactlevel="+entity['impactLevel'].lower().replace(" ","_")+",managementzones="+mz['name'].lower().split(" ")[0])
                        if entity['status'] == "OPEN":
                            new_value=1
                            count_open+=1
                        elif entity['status'] == "CLOSED":
                            #print(entity['problemId'])
                            new_value=-1
                            count_closed+=1
                        if key not in PB_DIC:
                            PB_DIC[key]=new_value
                        else :
                            PB_DIC[key]=PB_DIC[key]+new_value
                        value_mz=True

                if value_mz == False :
                        key=("problem.open,status="+entity['status']+",title="+title+",severitylevel="+entity['severityLevel'].lower().replace(" ","_")+",impactlevel="+entity['impactLevel'].lower().replace(" ","_")+",managementzones=NA")
                        if entity['status'] == "OPEN":
                            new_value=1
                            count_open+=1
                        elif entity['status'] == "CLOSED":
                            new_value=-1
                            count_closed+=1
                            #print(entity['problemId'])
                        if key not in PB_DIC:
                            PB_DIC[key]=new_value
                        else :
                            PB_DIC[key]=PB_DIC[key]+new_value
                                                    
    else:
        status='failed'
    return (PB_DIC, count, count_open, count_closed)

##################################
### dataingest###
##################################

def PostIngestData(TENANT,TOKEN,data):
    uri=TENANT+API_INGEST
    headers = {
        'accept': '*/*',
        'Authorization': 'Api-Token '+TOKEN,
        'Content-Type': 'text/plain; charset=utf-8'
    }
    jsonContent = None
    status='success'
    try:
        response=requests.post(uri,headers=headers,verify=False,data=data)
        if(response.ok):
            if(len(response.text) > 0):
                jsonContent = json.loads(response.text)
        else:
            jsonContent = json.loads(response.text)
            if debug != 0: print(jsonContent)
            errorMessage = ''
            if (jsonContent['error']):
                errorMessage = jsonContent['error']['message']
                print('...Dynatrace API returned an error: ' + errorMessage)
            raise Exception('Error', 'Dynatrace API returned an error: ' + errorMessage)
    except :
         status='failed'
    #For successful API call, response code will be 200 (OK)
    return ()

##################################
### main program###
##################################

PB=info_pb(tenant_source,token_source)
result=0
for key, value in PB[0].items() :
    data=key+" "+str(value)
    PostIngestData(tenant_target, token_target, key+" "+str(value))
if status!='failed' :
    print(PB[1],PB[2],PB[3])
else:
    print(-1)

