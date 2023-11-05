import requests
from requests.auth import HTTPBasicAuth
import json

from database import Product


def createProduct(app):
    token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    payload = {
        "grant_type": "client_credentials"
    }
    response = requests.post(
        token_url,
        auth=HTTPBasicAuth(app.config['PAYPAL_ID'], app.config['PAYPAL_SECRET']),
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = json.loads(response.text)

    url = 'https://api-m.sandbox.paypal.com/v1/catalogs/products'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'Authorization': 'Bearer ' + token['access_token']
    }

    data = json.dumps({
        "name": "Engage Enhance",
        "description": "Insightful Posts, Impactful Presence.",
        "type": "SERVICE",
        "category": "SOFTWARE",
    })
    response = requests.post(url, headers=headers, data=data)
    product = json.loads(response.text)
    return createPlan(app, product, token)


def createPlan(app, product, token):
    url = 'https://api-m.sandbox.paypal.com/v1/billing/plans'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'Authorization': 'Bearer ' + token['access_token']
    }

    data = json.dumps({
        "product_id": product['id'],
        "name": "Engage Enhance",
        "description": "Discover effortless social engagement with EngageEnhance.",
        "status": "ACTIVE",
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "300",
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "payment_failure_threshold": 1
        },
        "taxes": {
            "percentage": "10",
            "inclusive": True
        }
    })

    response = requests.post(url, headers=headers, data=data)
    plan = json.loads(response.text)
    item = Product(vendor='Paypal', productId=product['id'], planId=plan['id'])
    return item


def getSubscription(subId, app):
    token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    payload = {
        "grant_type": "client_credentials"
    }
    response = requests.post(
        token_url,
        auth=HTTPBasicAuth(app.config['PAYPAL_ID'], app.config['PAYPAL_SECRET']),
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = json.loads(response.text)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
        'Authorization': 'Bearer ' + token['access_token']
    }
    response = requests.get('https://api-m.sandbox.paypal.com/v1/billing/subscriptions/' + subId, headers=headers)
    data = json.loads(response.text)
    data['billing_info']['last_payment']['time'] = data['billing_info']['last_payment']['time'].split('T')[0]
    data['billing_info']['next_billing_time'] = data['billing_info']['next_billing_time'].split('T')[0]
    return data
