# Copyright (c) 2023 Victor Palma
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
import time
import requests
import psycopg2
import yaml
import json
import akeyless
from datetime import datetime


configuration = akeyless.Configuration(
        host = "https://api.akeyless.io"
)

def get_secret(secret_id):
    body = akeyless.GetSecretValue(names=['secret_id'], token=token)
    res = api.get_secret_value(body)

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

def write_to_database(database_target, currency_rates):
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
    print(f"Inserted {len(currency_rates['data'])} currency rates into the database.")


def main(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # api_token = config['api_token']
    api_token = get_secret('/coincap/api_token')
    db_targets = config['db_targets']

    while True:
        data = get_currency_rates(api_token)
        for db_target in db_targets:
            write_to_database(db_targets[db_target], data)
        time.sleep(config['interval'])


if __name__ == '__main__':
    main('config.yaml')

