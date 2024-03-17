from sys import exit
import requests, json, urllib3, os, re
from tabulate import tabulate

# from dotenv import load_dotenv
# load_dotenv('/opt/.env')

X_Auth_Key = "HERE"
ACCOUNT_ID = "HERE"
IP = "HERE"
DOMAIN = "HERE"
X_Auth_Email = "HERE"


def get_zoneid(domain):
    headers = {
        'X-Auth-Email': '{}'.format(X_Auth_Email),
        'X-Auth-Key': '{}'.format(X_Auth_Key),
        'Content-Type': 'application/json',
    }

    params = {
        'name': '{}'.format(domain),
        'status': 'active',
        'account.id': '{}'.format(ACCOUNT_ID),
        'page': '1',
        'per_page': '20',
        'order': 'status',
        'direction': 'desc',
        'match': 'all',
    }

    response = requests.get('https://api.cloudflare.com/client/v4/zones', params=params, headers=headers)
    data = json.loads(response.text)
    zoneid = data['result'][0].get('id')
    return zoneid

def get_dns_recordid(domain):
    zoneid = get_zoneid(domain)

    headers = {
        'X-Auth-Email': '{}'.format(X_Auth_Email),
        'X-Auth-Key': '{}'.format(X_Auth_Key),
        'Content-Type': 'application/json',
    }

    params = {
        'type': 'A',
        'name': '{}'.format(domain),
        'page': '1',
        'per_page': '100',
        'order': 'type',
        'direction': 'desc',
        'match': 'all',
    }

    response = requests.get('https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(zoneid), params=params, headers=headers)
    data = json.loads(response.text)
    dns_recordid = data['result'][0].get('id')
    return dns_recordid

def update_dns_recordA(domain, ip):
    zoneid = get_zoneid(domain)
    dns_recordid = get_dns_recordid(domain)
    headers = {
        'X-Auth-Email': '{}'.format(X_Auth_Email),
        'X-Auth-Key': '{}'.format(X_Auth_Key),
    }

    json_data = {
        'type': 'A',
        'name': '{}'.format(domain),
        'content': '{}'.format(ip),
        'ttl': 1,
        'proxied': True,
}

    response = requests.put('https://api.cloudflare.com/client/v4/zones/{0}/dns_records/{1}'.format(zoneid,dns_recordid), headers=headers, json=json_data)
    return response


def change_origin_mode_ssl(domain):
    zoneid = get_zoneid(domain)
    headers = {
        'X-Auth-Email': '{}'.format(X_Auth_Email),
        'X-Auth-Key': '{}'.format(X_Auth_Key),
        'Content-Type': 'application/json',
    }

    json_data = {
        'value': 'flexible',
    }

    response = requests.patch('https://api.cloudflare.com/client/v4/zones/{0}/settings/ssl'.format(zoneid), headers=headers, json=json_data)
    return response

if __name__ == "__main__":
    table = []
    headers = ["Type", "Name", "Content"]
    text = ""

    state = update_dns_recordA(DOMAIN, IP)
    if state.status_code == 200:
        text = "Update DNS success, status code {}".format(state.status_code)
        data = json.loads(state.text)
        table.append([
            data['result'].get('type'),
            data['result'].get('name'),
            data['result'].get('content')
        ])
        text = tabulate(table, headers=headers, tablefmt="pretty")
        print(text)
    else:
        text = "something went wrong !!!"
        print(text)

    state_origin = change_origin_mode_ssl(DOMAIN)
    if state.status_code == 200:
        text = "Change origin mode SSL to Flexible success, status code {}".format(state.status_code)
        data = json.loads(state.text)
        print(text)
        print(data)
    else:
        text = "something went wrong !!!"
        print(text)
