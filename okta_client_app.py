from flask import Flask, session, request, jsonify, redirect, url_for
from flask_oauthlib.client import OAuth
import json
from okta import UsersClient
import os
import requests
from urllib.parse import urljoin


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config.from_pyfile(os.path.join(BASE_DIR, 'okta_client_app.cfg'))

oauth = OAuth()
okta = oauth.remote_app(
    'okta',
    base_url=urljoin(app.config['OKTA_BASE_URL'], '/oauth2/v1/'),
    request_token_url=None,
    request_token_params={'scope': 'openid'},
    access_token_method='POST',
    access_token_url='token',
    authorize_url='authorize',
    consumer_key=app.config['OKTA_CLIENT_ID'],
    consumer_secret=app.config['OKTA_CLIENT_SECRET'],
)


@app.route('/')
def index():
    if 'okta_token' in session:
        me = okta.get('userinfo')
        user_id = me.data['sub']
        users = UsersClient(
            base_url=app.config['OKTA_BASE_URL'],
            api_token=app.config['OKTA_API_TOKEN'],
        )
        user = json.loads(users.get_path('/{0}'.format(user_id)).text)
        groups = json.loads(users.get_path('/{0}/groups'.format(user_id)).text)
        user['groups'] = groups
        return jsonify(user)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    resp = okta.authorize(callback=url_for('authorized', _external=True), state='fishy')
    return resp


@app.route('/logout')
def logout():
    okta.get('logout')
    session.pop('okta_token', None)
    return jsonify({'status': 'logged out'})


@app.route('/login/authorized')
def authorized():
    resp = okta.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['okta_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


@okta.tokengetter
def get_okta_oauth_token():
    return session.get('okta_token')


if __name__ == '__main__':
    app.run()
