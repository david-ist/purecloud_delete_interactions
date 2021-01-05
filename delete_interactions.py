import requests
import base64
import sys

# Request oauth token  reference: https://developer.inindca.com/api/tutorials/oauth-client-credentials/?language=python&step=1
def get_token() -> "global response":
    client_id = "XXXXXXXXXXXXXX"
    client_secret = "XXXXXXXXXXXXXXXXXXX"
    authorization = base64.b64encode(bytes(client_id + ":" + client_secret, "ISO-8859-1")).decode("ascii")
    request_headers = {"Authorization": f"Basic {authorization}","Content-Type": "application/x-www-form-urlencoded"}
    request_body = {"grant_type": "client_credentials"}
    global response
    response = requests.post("https://login.mypurecloud.de/oauth/token", data=request_body, headers=request_headers)
    error_handling("token is generated")

#Function to do the query for Purecloud analytics. Afterward trim the unwanted information and keep only the converstaion ID
def queue_query() -> "result":
    r = requests.post("https://api.mypurecloud.de/api/v2/analytics/queues/observations/query", headers=requestHeaders, json = body)
    global result
    jsonresult=r.json()
    result = jsonresult["results"]
    result = result[0]
    result = result["data"]
    result = result[0]
    
#Function for error handling depending on the response code
def error_handling(text:str) -> None:
    if response.status_code == 200:
        print(text)
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason }")
        sys.exit(response.status_code)


get_token()
#Set json response and the required header, along with the body we are passing in queue_query function
response_json = response.json()
requestHeaders = {"Authorization": f"{ response_json['token_type'] } { response_json['access_token']}"}

#The body uses to search one specific queueID along with one specific mediatype interaction(in this case email)   
#Consult with https://developer.mypurecloud.com/developer-tools/#/analytics-query-builder to build search queries
body = {
        "filter": {
        "type": "and",
        "clauses": [
        {
            "type": "and",
            "predicates": [
            {
            "type": "dimension",
            "dimension": "mediaType",
            "operator": "matches",
            "value": "email"
            },
            {
            "type": "dimension",
            "dimension": "queueId",
            "operator": "matches",
            "value": "c76fkl65-d9fa-421f-897f-1c7e7e09b9f0"
            }
            ]
        }
        ]
        },
        "metrics": [
        "oWaiting"
        ],
        "detailMetrics": [
        "oWaiting"
        ]
        }

#Observations query only returns maximum of 100 values. With while loop we mitigate this by rerunning queue_query func to retrieve another 100 batch
while True:
    queue_query()
    if "observations" in result:
        result_final = result["observations"]
        for i in result_final:
            convid = i["conversationId"]
            response = requests.post(f"https://api.mypurecloud.de/api/v2/conversations/{convid}/disconnect", headers=requestHeaders)
            error_handling(f"{convid} has been deleted")
    else:
        print("no more interactions found")
        sys.exit()
