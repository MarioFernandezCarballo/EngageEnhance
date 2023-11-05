from werkzeug.security import generate_password_hash, check_password_hash

from database import User, Social


def userSignup(database, form):
    if form['username'].isalnum():
        if form['password'] == form['password-1']:
            hashed_password = generate_password_hash(form['password'])
            if User.query.filter_by(username=form['username']).first():
                return 402, None
            new_user = User(
                email=form['email'],
                username=form['username'],
                password=hashed_password,
                website=form['website'],
                subscriptionId=form['paypal']
            )
            database.session.add(new_user)
            database.session.commit()
            addSocial(new_user, form['social-1'], database)
            addSocial(new_user, form['social-2'], database)
            addSocial(new_user, form['social-3'], database)
            return 200, new_user
        else:
            return 403, None
    return 405, None


def addSocial(user, social, database):
    if social:
        database.session.add(Social(
            url=social,
            user_id=user.id
        ))
        database.session.commit()


def userLogin(form):
    if form['username'].isalnum():
        user = User.query.filter_by(username=form['username']).first()
        if user:
            if check_password_hash(user.password, form['password']):
                return 200, user
    return 401, None


def getUserOnly(pl):
    return User.query.filter_by(id=pl).first()