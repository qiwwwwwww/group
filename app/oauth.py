from rauth import OAuth2Service
from flask import current_app, url_for, request, redirect, session
import json

#the OAuthSignIn class created for both google and facebook
class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

# the particular facebook sign in class
# for its authorization ( will redirect user to authorize/<provider>/page and call back(will redirect the user to callback/<provider>/page

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=id,email').json()
        return (
            me.get('email').split('@')[0],
            me.get('email')
        )


# the particular google sign in class
# for its authorization ( will redirect user to authorize/<provider>/page and call back(will redirect the user to callback/<provider>/page

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
                                     name='google',
                                     client_id=self.consumer_id,
                                     client_secret=self.consumer_secret,
                                     authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
                                     access_token_url='https://www.googleapis.com/oauth2/v4/token',
                                     base_url='https://www.googleapis.com/oauth2/v3/userinfo'
                                     )
    
    def authorize(self):
        return redirect(self.service.get_authorize_url(
                                                       scope='email',
                                                       response_type='code',
                                                       redirect_uri=self.get_callback_url())
                        )
    
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
                                                      data={'code': request.args['code'],
                                                      'grant_type': 'authorization_code',
                                                      'redirect_uri': self.get_callback_url()},
                                                      decoder = json.loads
                                                      )
        me = oauth_session.get('').json()
        return (
                me.get('email').split('@')[0],
                me['email'])



