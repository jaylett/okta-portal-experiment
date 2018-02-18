from flask import Flask, session, request, redirect, url_for, render_template
from flask_oauthlib.client import OAuth
from okta import AuthClient
import os
from urllib.parse import urlencode, urljoin, urlunsplit


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config.from_pyfile(os.path.join(BASE_DIR, 'sso_app.cfg'))


@app.route('/')
def index():
    # Two options: login and app. App goes to the okta client app,
    # which uses the OpenID Connect flow, so if there's no current
    # okta session you'll be hit with a login barrier. Login is
    # _our_ login, following which there should be an okta session.
    #
    # Following a login from within another app, all okta apps should
    # be able to automatically authenticate without user action
    # (depending on okta config), although we don't currently have a
    # demo for this.
    return render_template('sso_index.html')


@app.route('/login')
def login():
    # Log in to okta, convert to a session (so other apps
    # can authenticate without user action), and show what
    # happened.
    #
    # Must provide okta with source User Agent, Accept-Language,
    # and IP Address (as X-Forwarded-For) to pass client request
    # context.
    # Authorization: SSWS <okta-api-token>
    auth = AuthClient(
        base_url=app.config['OKTA_BASE_URL'],
        api_token=app.config['OKTA_API_TOKEN'],
        headers={
            'User-Agent': request.headers['User-Agent'],
            'Accept-Language': request.headers['Accept-Language'],
        },
    )
    resp = auth.authenticate(
        username=app.config['OKTA_USER_LOGIN'],
        password=app.config['OKTA_USER_PASSWORD'],
    )
    # And redirect to make the Okta session.
    if resp.status == 'SUCCESS':
        return redirect(
            urljoin(
                app.config['OKTA_BASE_URL'],
                urlunsplit(
                    (
                        '', # no scheme -- we are creating a URL relative
                        '', # no netloc -- to OKTA_BASE_URL
                        'oauth2/v1/authorize',
                        urlencode(
                            {
                                'client_id': app.config['OKTA_CLIENT_ID'],
                                'response_type': 'id_token',
                                'scope': 'openid',
                                'prompt': 'none',
                                # 'response_mode': 'query',
                                # backend needs to know, but we can't
                                # actually combine this with id_token.
                                # Of course we've done the login already,
                                # so we could have created a session local
                                # to the portal at _that_ point, and then
                                # we don't need it here.
                                'redirect_uri': url_for(
                                    'logged_in',
                                    _external=True,
                                ),
                                'state': 'a-different-fishy',
                                'nonce': 'bad-nonce',
                                'sessionToken': resp.sessionToken,
                            },
                        ),
                        '', # no fragment
                    )
                )
            )
        )
    else:
        return render_template(
            'login_failure.html',
            resp=resp,
        )


@app.route('/login/done')
def logged_in():
    if request.args.get('error'):
        return render_template(
            'login_redirect_failure.html',
            error=request.args.get('error'),
            error_description=request.args.get('error_description'),
        )
    return render_template(
        'logged_in.html',
        session=None,
        profile=None,
    )


if __name__ == '__main__':
    app.run(port=9000)
