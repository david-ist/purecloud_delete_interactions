import requests
import base64
import sys

def get_token() -> "global response":
    client_id = "XXXXXXXXXXXXXX"
    client_secret = "XXXXXXXXXXXXXXXXXXX"
    authorization = base64.b64encode(bytes(client_id + ":" + client_secret, "ISO-8859-1")).decode("ascii")
    request_headers = {"Authorization": f"Basic {authorization}","Content-Type": "application/x-www-form-urlencoded"}
    request_body = {"grant_type": "client_credentials"}
    global response
    response = requests.post("https://login.mypurecloud.de/oauth/token", data=request_body, headers=request_headers)
    error_handling("token is generated")

def queue_query() -> "result":
    r = requests.post("https://api.mypurecloud.de/api/v2/analytics/queues/observations/query", headers=requestHeaders, json = body)
    global result
    jsonresult=r.json()
    result = jsonresult["results"]
    result = result[0]
    result = result["data"]
    result = result[0]

def error_handling(text:str) -> None:
    if response.status_code == 200:
        print(text)
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason }")
        sys.exit(response.status_code)


get_token()
response_json = response.json()
requestHeaders = {"Authorization": f"{ response_json['token_type'] } { response_json['access_token']}"}

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
            "value": "c76fea65-d8fa-461f-897f-1c7e7e09b9f0"
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

queue_query()
if "observations" in result:
    result_final = result["observations"]
    for i in result_final:
        convid = i["conversationId"]
        response = requests.post(f"https://api.mypurecloud.de/api/v2/conversations/{convid}/disconnect", headers=requestHeaders)
        error_handling(f"{convid} has been deleted")
else:
    print("no e-mail found")