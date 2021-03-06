import users

import dpy
import mock
import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from oauth2client import client as oauth2client

import models

dpy.SetTestMode()

class UsersTest(unittest.TestCase):

  CLIENT_ID = 'fake_client_id'
  CLIENT_SECRET = 'fake_client_secret'

  USER_ID = 'test@example.com'
  AUTH_CODE = 'fake_auth_code'
  CREDENTIALS = oauth2client.OAuth2Credentials(
      access_token='fake_access_token',
      client_id=CLIENT_ID,
      client_secret=CLIENT_SECRET,
      refresh_token='fake_refresh_token',
      token_expiry=None,
      token_uri='fake_token_uri',
      user_agent='fake_user_agent')

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    ndb.get_context().clear_cache()

    models.ClientSecret.set(self.CLIENT_SECRET)
    self.exchanger = mock.Mock()
    self.exchanger.exchange.return_value = self.CREDENTIALS
    self.client = users.UsersClient(auth_code_exchanger=self.exchanger)

  def test_get_credentials_none(self):
    self.assertIsNone(self.client.get_credentials(user_id=self.USER_ID))

  def test_set_credentials(self):
    self.client.set_credentials(self.CREDENTIALS, user_id=self.USER_ID)
    self.assertEqual(
        self.client.get_credentials(user_id=self.USER_ID).to_json(),
        self.CREDENTIALS.to_json())

  def test_exchange_auth_code(self):
    self.assertEqual(
        self.client.exchange_auth_code(self.AUTH_CODE).to_json(),
        self.CREDENTIALS.to_json())
    self.exchanger.exchange.assert_called_with(
        self.CLIENT_SECRET, self.AUTH_CODE)
