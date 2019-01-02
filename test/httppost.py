#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests

response = requests.post(
    'https://www.cmsweb.club/home/game/verify/acceptBuyin',
    data = {
        'auto': False
    },
    cookies = {
        'connect.sid': 's%3A05be02c3-8a00-4537-a07d-17bd1f83d35f.mZ%2FmGnHvltFAn%2B6E6w3rqF3xNVNqnadepIwFeUG5FNs'
    }
)

print (response)
print (response.headers['Content-Type'])