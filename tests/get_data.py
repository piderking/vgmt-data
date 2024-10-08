import requests





access_token = requests.get("http://localhost:3321/users/a863335b-0db6-49b6-98cc-1bdf8044a796/").json()["data"]["providers"]["dexcom"]["access_token"].strip()

url = "https://sandbox-api.dexcom.com/v3/users/self/egvs"

query = {
  "startDate": "2024-02-06T09:12:35",
  "endDate": "2024-02-07T09:13:35"
}

headers = {"Authorization": "Bearer {}".format(access_token)}

response = requests.get(url, headers=headers, params=query)

print(access_token)
print(response.text)
print(response.status_code)