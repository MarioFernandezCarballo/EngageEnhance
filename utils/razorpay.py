import razorpay
from database import Product
import datetime


def createRPProduct(app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))
    subscription = client.subscription.create({
        'plan_id': app.config['RAZORPAY_PLAN_ID'],
        'total_count': 999,
        'quantity': 1,
        'customer_notify': 1,
    })
    item = Product(vendor='Razorpay', productId=app.config['RAZORPAY_PLAN_ID'], planId=subscription['id'])

    return item


def getPayment(payId, app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))
    payment = client.payment.fetch(payId)
    payment['created_at'] = datetime.datetime.utcfromtimestamp(payment['created_at']).strftime("%Y/%m/%d")
    return payment