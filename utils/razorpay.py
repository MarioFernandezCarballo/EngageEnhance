import razorpay
from database import Product
import datetime


def createRPProduct(app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))
    plan = client.plan.create({
        'period': 'monthly',
        'interval': 1,
        'item': {
            'name': 'Engage Enhance - Monthly',
            'amount': 25000,
            'currency': 'INR',
            'description': 'Insightful Posts, Impactful Presence.',
        },
        'notes': {'notes_key_1': 'Tea, Earl Grey, Hot'}
    })
    subscription = client.subscription.create({
        'plan_id': plan['id'],  # app.config['RAZORPAY_PLAN_ID'],
        'total_count': 999,
        'quantity': 1,
        'customer_notify': 1,
    })
    item = Product(vendor='Razorpay', productId=plan['id'], planId=subscription['id'])

    return item


def getPayment(payId, app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))
    payment = client.payment.fetch(payId)
    payment['created_at'] = datetime.datetime.utcfromtimestamp(payment['created_at']).strftime("%Y/%m/%d")
    return payment