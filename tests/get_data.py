import requests





access_token = requests.get("http://localhost:3321/users/89b20116-2895-439a-8158-b6f68853db6b/").json()["data"]["providers"]["dexcom"]["access_token"].strip()

url = "https://api.dexcom.com/v3/users/self/egvs"

query = {
  "startDate": "2022-02-06T09:12:35",
  "endDate": "2022-02-06T09:12:35"
}

headers = {"Authorization": "Bearer {}".format(access_token)}

response = requests.get(url, headers=headers, params=query)

print(access_token)
print(response.text)
print(response.status_code)