from datetime import timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.request import urlopen
from flask import Flask, Blueprint, make_response, redirect, url_for, request, flash, render_template, jsonify
from flask_jwt_extended import create_access_token, JWTManager, set_access_cookies, unset_jwt_cookies
from flask_login import login_user, login_required, logout_user, current_user
from database import Product, User
from utils import createApp, createDatabase, userSignup, getUserOnly, userLogin, createTrelloBoards, getPayment, getSubscription


app = Flask(__name__)
app = createApp(app)
createDatabase(app)

loginManager = app.config["loginManager"]
jwt = app.config["jwt"]


@loginManager.user_loader
def loadUser(user_id):
    return getUserOnly(user_id)


@jwt.expired_token_loader
def refreshToken(jwt_header, jwt_data):
    response = make_response(redirect(url_for('loginEndPoint')))
    unset_jwt_cookies(response)
    return response


@app.route('/', methods=['GET'])
def homeEndPoint():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    d = json.load(urlopen('http://ipinfo.io/' + ip + '/json'))
    if 'country' in d.keys():
        if d['country'] == 'IN':
            product = Product.query.filter_by(vendor='Razorpay').first()
            return render_template('home_razor.html', product=product, razorpayKey=app.config['RAZORPAY_ID'], title='Welcome', user=current_user if not current_user.is_anonymous else None)
    #product = Product.query.filter_by(vendor='Razorpay').first()
    #return render_template('home_razor.html', product=product, razorpayKey=app.config['RAZORPAY_ID'], user=current_user if not current_user.is_anonymous else None)

    product = Product.query.filter_by(vendor='Paypal').first()
    return render_template('home_paypal.html', product=product, clientId=app.config['PAYPAL_ID'], title='Welcome', user=current_user if not current_user.is_anonymous else None)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return json.load(urlopen('http://ipinfo.io/' + ip + '/json')), 200


@app.route('/success/<idPaypal>', methods=['GET'])
def successEndPoint(idPaypal):
    # Double check
    return render_template('signup.html', title="Register", id=idPaypal, user=current_user if not current_user.is_anonymous else None)


@app.route('/register', methods=['POST'])
def registerEndPoint():
    status, new_user = userSignup(app.config['database'], request.form)
    if status == 200:
        if new_user:
            createTrelloBoards(new_user)
        response = redirect(url_for('dashboardEndPoint'))
        set_access_cookies(response, create_access_token(identity=new_user.username,
                                                         expires_delta=timedelta(days=365)))
        login_user(new_user)
        flash("Registered successfully")
        return response
    if status == 402:
        flash("The username already exists")
    if status == 403:
        flash("Password fields must coincide")
    if status == 405:
        flash("Username must not have special characters")

    return render_template('signup.html', title="Register", id=request.form['paypal'], user=current_user if not current_user.is_anonymous else None)


@app.route('/login', methods=['GET', 'POST'])
def loginEndPoint():
    if request.method == 'POST':
        status, user = userLogin(request.form)
        if status == 200:
            flash("Login successful")
            response = redirect(url_for('dashboardEndPoint'))
            set_access_cookies(response, create_access_token(identity=user.username))
            login_user(user)
            return response
        if status == 401:
            flash("Could not verify")
            return make_response(render_template('login.html', title="Login", user=current_user if not current_user.is_anonymous else None), 401, {'Authentication': '"login required"'})
    return render_template('login.html', title="Login", user=current_user if not current_user.is_anonymous else None)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logoutEndPoint():
    response = redirect(url_for('loginEndPoint'))
    unset_jwt_cookies(response)
    logout_user()
    flash("Logout successfully")
    return response


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboardEndPoint():
    return render_template('dashboard.html', title=current_user.username, user=current_user if not current_user.is_anonymous else None)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profileEndPoint():
    return render_template('profile.html', title=current_user.username, user=current_user if not current_user.is_anonymous else None, goBack=True)


@app.route('/subscription', methods=['GET'])
@login_required
def subscriptionEndPoint():
    d = json.load(urlopen('http://ipinfo.io/' + request.remote_addr + '/json'))
    if 'country' in d.keys():
        if d['country'] == 'IN':
            data = getPayment(current_user.subscriptionId, app)
            return render_template('subscription_razor.html', title=current_user.username,
                                   user=current_user if not current_user.is_anonymous else None, goBack=True, data=data)
    data = getSubscription(current_user.subscriptionId, app)
    return render_template('subscription_paypal.html', title=current_user.username,
                           user=current_user if not current_user.is_anonymous else None, goBack=True, data=data)


@app.route('/update', methods=['POST'])
@login_required
def updateEndPoint():
    form = request.form
    us = User.query.filter_by(username=current_user.username).first()
    if check_password_hash(us.password, form['password']):
        us.username = form['username'] if form['username'] else current_user.username
        us.email = form['email'] if form['email'] else current_user.email
        us.website = form['website'] if form['website'] else current_user.website
        app.config['database'].session.commit()
        if form['password-1'] and form['password-2']:
            if form['password-1'] == form['password-2']:
                us.password = generate_password_hash(form['password-1'])
                app.config['database'].session.commit()
                flash("Profile updated")
                return redirect(url_for('profileEndPoint'))
            else:
                flash("Passwords must coincide")
                return redirect(url_for('profileEndPoint'))
    flash("Bad password")
    return redirect(url_for('profileEndPoint'))


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])


