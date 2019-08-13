import requests
import json
from urllib.parse import urlencode

VALID_ENTITIES = (
    'leads', 'contacts', 'accounts', 'deals', 'campaigns', 'tasks',
    'cases', 'events', 'calls', 'solutions', 'products', 'vendors',
    'sales_orders', 'purchase_orders', 'invoices', 'price_books',
    'users','org','roles','profiles',"settings"
)

class _Session(object):

    def __init__(self, access_token, refresh_token='', client_id='', client_secret='', api_domain="https://www.zohoapis.eu"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.request_session = self._init_session()
        self.API_URL = f"{api_domain}/crm/v2/"


    def update_access_token(self):
        update_url = f"https://accounts.zoho.eu/oauth/v2/token?refresh_token={self.refresh_token}&client_id={self.client_id}&client_secret={self.client_secret}&grant_type=refresh_token"
        response = requests.post(update_url).json()
        self.access_token = response['access_token']
        self.request_session = self._init_session()
        return self.access_token

    
    def remove_refresh_token(self, refresh_token=''):
        remove_url = f'https://accounts.zoho.eu/oauth/v2/token/revoke?token={refresh_token if refresh_token else self.refresh_token}'
        requests.post(url)
        return True

    
    def _init_session(self, access_token=None):
        session = requests.Session()
        session.headers["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
        return session


    def _send_api_request(self, service, http_method='get', object_id=None, params={}):
        url = f"{self.API_URL}{service}/{object_id}" if object_id else f"{self.API_URL}{service}"
        if http_method == 'get' and params:
            url += "&"+urlencode(params) if "?" in url else "?"+urlencode(params)
        response = self.request_session.__getattribute__(http_method)(url, data=params)
        if response.status_code == 401:
            self.update_access_token()
            response = self.request_session.__getattribute__(http_method)(url, data=params)
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    
    def list(self, service, params={}, object_id=None):
        return self._send_api_request(service=service, params=params)


    def get(self, service, object_id, params={}):
        return self._send_api_request(service=service, object_id=object_id, params=params)

    
    def create(self, service, params={}, object_id=None):
        return self._send_api_request(service=service, http_method="post", params=params)

    
    def update(self, service, object_id, params={}):
        return self._send_api_request(service=service, object_id=object_id, http_method='put', params=params)


    def delete(self, service, object_id, params={}):
        return self._send_api_request(service=service, object_id=object_id, http_method='delete', params=params)


class ZOHOClient(object):
    def __init__(self, access_token, refresh_token='', client_id="", client_secret="", api_domain="https://www.zohoapis.eu"):
        self._session = _Session(access_token, refresh_token, client_id=client_id, client_secret=client_secret, api_domain=api_domain)


    def __getattr__(self, method_name):
        if method_name not in VALID_ENTITIES:
            raise ValueError("invalid zohocrm entity - {}".format(method_name))
        return _Request(self, method_name)


    @property
    def access_token(self):
        return self._session.access_token
    
    
    @property
    def refresh_token(self):
        return self._session.refresh_token
    
    
    def update_access_token(self):
        return self._session.update_access_token()


    def remove_refresh_token(self):
        return self._session.remove_refresh_token()


    def __call__(self, method_name, method_kwargs={}):
        return getattr(self, method_name)(method_kwargs)


class _Request(object):
    __slots__ = ('_api', '_methods', '_method_args', '_object_id')

    def __init__(self, api, methods):
        self._api = api
        self._methods = methods


    def __getattr__(self, method_name):
        return _Request(self._api, {'service':self._methods,'method': method_name})


    def __call__(self, object_id=None, data={}):
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")
        return self._api._session.__getattribute__(self._methods['method'])(
                service=self._methods["service"],
                object_id=object_id,
                params=data
            )
