import razorpay
from database import Product
import datetime


def createRPProduct(app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))

    item = Product(vendor='Razorpay', productId=app.config['RAZORPAY_PLAN_ID'], planId=app.config['RAZORPAY_SUB_ID'])

    return item


def getPayment(payId, app):
    client = razorpay.Client(auth=(app.config['RAZORPAY_ID'], app.config['RAZORPAY_SECRET']))
    payment = client.payment.fetch(payId)
    payment['created_at'] = datetime.datetime.utcfromtimestamp(payment['created_at']).strftime("%Y/%m/%d")
    return payment