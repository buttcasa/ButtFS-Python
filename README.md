# ButtFS-Python Beta Release 0.6
Initial release of the Python SDK for ButtFS. This release allows developers get started building ButtFS-based applications. Unfortunately the functionality is far from complete.

### Current Functionality
This release supports a subset of ButtFS functionality. Most operations with files and folders are supported, though objects cannot be restored from the trash. Reaching full REST functionality is expected to happen in the next few weeks.

Here are the major missing features:

* Shares
* User Creation
* File Version History

If any of those features are vital to your use case, let us know so we can prioritize them. Otherwise, the above order will be the release order.

Python-SDK specific functionality is also planned once the REST interface is implemented.

### Tests
The tests that exist are functional tests designed to be used with a ButtFS test user and are the tests used to develop the API. They will use API requests on your free ButtFS account, but if you run out of requests just create a new account.

These tests also act as a guide for intended functionality. Some test lines are commented out to reflect the current state of the SDK or REST interface.

#### Test Setup
The test_settings.py file in the test directory contains all the constants needed for the API. 

* BUTTFS_ID = Application Client ID
* BUTTFS_SECRET = Application Secret
* BUTTFS_BASE = Application API Server
* TEST_USER_EMAIL = email for a test user
* TEST_USER_PASSWORD = password for a test user

A user created (non-test) through the API should work just as well.

### Notes
All calls have an optional debug parameter that will print the request & response associated with that request. The ButtFSRESTAdapter also has a method to get this as a string to help debug any difficulties. Including the failed requests in pull requests / other contact will help us debug what's going on. 

Example: 
```python
s = Session(base_url,
            buttfs_id,
            buttfs_secret)
s.authenticate(username, password, debug=True)
```
```
Request:
POST: https://xxxxxxxx.cloudfs.io/v2/oauth2/token
Date : Sat, 25 Oct 2014 03:10:15 GMT
Content-Length : 60
Content-Type : application/x-www-form-urlencoded; charset="utf-8"
Authorization : BCS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Body:
	username=<username>
	password=<password>
	grant_type=password

Response:
HTTP Code: 200
content-length : 308
set-cookie : tkey_auth_api_stage_sessionid=US2.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY; Domain=.cloudfs.io; Max-Age=2592000; Path=/; expires=Mon, 24-Nov-2014 03:10:13 GMT, tkey_auth_api_stage_csrf=7fb02c4c212d4c2b8139b1328d313963; Domain=.cloudfs.io; Max-Age=2592000; Path=/; expires=Mon, 24-Nov-2014 03:10:13 GMT
server : Apache
date : Sat, 25 Oct 2014 03:10:13 GMT
x-bcp : s:api06-v2-us2, be:api, fe:https
content-type : application/json; charset=UTF-8
Body:
{u'access_token': u'US2.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
 u'token_type': u'bearer',
 u'transmission_key': u'<160 character transmission key>'}
 ```

### Feedback
We would love to hear what features or functionality you're interested in, or general comments on the SDK (good and bad - especially bad). 
