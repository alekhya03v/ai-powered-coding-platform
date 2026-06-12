import requests

url = 'https://leetcode.com/graphql'
json_data = {
    'operationName': 'questionData',
    'variables': {'titleSlug': 'two-sum'},
    'query': 'query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { title content difficulty } }'
}
headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
resp = requests.post(url, json=json_data, headers=headers)
print(resp.status_code)
print(str(resp.json())[:500])
