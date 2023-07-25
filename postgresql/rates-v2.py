#!/bin/env python3
# Copyright (c) 2023 Victor Palma
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
import akeyless
import argparse
import asyncio
import json
import psycopg2
import requests
import time
import yaml
import os
from datetime import datetime


def get_secret(secret_val):
    configuration = akeyless.Configuration(
        host="https://api.akeyless.io"
    )
    api_client = akeyless.ApiClient(configuration)
    api = akeyless.V2Api(api_client)
    body = akeyless.Auth(access_id='', access_key='')
    res = api.auth(body)
    print(res)
    
    token = res.token

    body = akeyless.GetSecretValue(names=[secret_val], token=token)
    res = api.get_secret_value(body)
    print(res[secret_val])

    return res[secret_val]

def get_currency_rates(api_token):
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.get('https://api.coincap.io/v2/rates', headers=headers)
    response.raise_for_status()
    return json.loads(response.content)


def to_null_string(obj):
    if obj is None:
        return "Null"
    else:
        return str(obj)


async def write_to_database(pg_version, database_target, currency_rates):
    timestamp = datetime.fromtimestamp(int(time.time()))
    data = {key: value for d in database_target for key, value in d.items()}

    conn = psycopg2.connect(
        host=data['host'],
        port=data['port'],
        user=data['user'],
        password=data['password'],
        database=data['database']
    )

    with conn.cursor() as cur:
        for rate in currency_rates['data']:
            cur.execute("SELECT id FROM asset WHERE id=%s", (rate['id'],))
            result = cur.fetchone()
            if result:
                cur.execute("UPDATE asset SET timestamp=%s, rate_usd=%s WHERE id=%s",
                            (timestamp, rate['rateUsd'], rate['id']))
            else:
                cur.execute("INSERT INTO asset (id, timestamp, symbol, currency_symbol, type, rate_usd) VALUES (%s, %s, %s, %s, %s, %s)",
                            (rate['id'], timestamp, rate['symbol'], to_null_string(rate['currencySymbol']), rate['type'], rate['rateUsd']))
    conn.commit()
    conn.close()
    print(f"{datetime.now()}: Inserted {len(currency_rates['data'])} currency rates into the database: {pg_version}.")


async def main(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    api_token = config['api_token']
    db_targets = config['db_targets']

    use_secret_vault = os.environ.get("USE_VAULT_SVC", "false")
    if use_secret_vault.lower() == "true":
        api_token = get_secret("/service/coincap/api_token")
        print(f"{datetime.now()}: Retrieved password from secret vault.")
        
    print("Starting rates-v2.py")
    while True:
        data = get_currency_rates(api_token)
        tasks = []
        for db_target in db_targets:
            task = asyncio.create_task(write_to_database(db_target, db_targets[db_target], data))
            tasks.append(task)
        await asyncio.gather(*tasks)
        await asyncio.sleep(config['interval'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Path to config file (default: config.yaml)')
    args = parser.parse_args()
    asyncio.run(main(args.config))
