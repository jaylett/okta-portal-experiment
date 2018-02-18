# SSO portal experiment with Okta

Fill out the following variables in `sso_app.cfg`:

 * `OKTA_API_TOKEN`, `OKTA_CLIENT_ID`, `OKTA_BASE_URL`
 * `OKTA_USER_LOGIN` and `OKTA_USER_PASSWORD`
 * `SECRET_KEY`

You also want some things in `okta_client_app.cfg`:

 * `OKTA_API_TOKEN`, `OKTA_CLIENT_ID`, `OKTA_CLIENT_SECRET`, `OKTA_BASE_URL`
 * `SECRET_KEY`

Optionally, set `DEBUG` to `true` in both of them.

Then you should be able to run both apps at once, and use the SSO
portal login (`sso_app.py`) to avoid having to log in to Okta before using
the client app (`okta_client_app.py`).
