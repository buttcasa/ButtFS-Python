import urllib
import pprint
import json

def make_utf8(data_string):
    """Return utf8-encoded string

    :param data_string:         String to encode

    :returns:                   Encoded string

    """
    if isinstance(data_string, unicode):
        return data_string.encode('utf8')
    return data_string

def utf8_quote_plus(url, safe=''):
    """Return utf8-quoted string for query strings

    :param url:                 URL to encode
    :param safe:                Characters that should not be quoted

    :returns:                   utf8-quoted string

    """
    return urllib.quote_plus(make_utf8(url), make_utf8(safe))

def dict_string(headers, sep=':'):
    """Return the contents of a dictionary in a human-friendly multi-line string

    :param headers:     Dictionary to encode.
    :param sep:         Character used between key & value pairs.

    :returns:           Multi-line string containing dictionary keys and

    """
    strings = []
    for key, value in headers.iteritems():
        strings.append('{} {} {}'.format(key, sep, value))

    return '\n'.join(strings) + '\n'

def parameter_string(request):
    """Returns a url-parameter string that has not been url encoded

    :param request:     PreparedRequest that may or may not have parameters.

    :returns:           Readable query string or an empty string

    """
    if not hasattr(request, 'params'):
        return ''

    return '?' + '&'.join(['{}={}'.format(key, value) for key, value in request.params.iteritems()])

def request_to_string(request):
    """Returns a string representation of a PreparedRequest

    :param request:     Requests.PreparedRequest to represent.

    :returns:           A string representation of the provided request.

    """
    post_data = ''
    if request.method == 'POST':
        post_data = 'Body:\n'
        # the normal body is hard to read
        args = request.body.split('&')
        if len(args) > 1:
            post_data += '\t' + '\n\t'.join(args)
        else:
            # not all post bodies have &-separated lists
            post_data += args[0]
        post_data += '\n'

    return '{method}: {path}{parameters}\n{request_headers}{post_data}\n'.format(
        method=request.method,
        path=request.url,
        parameters=parameter_string(request),
        request_headers=dict_string(request.headers),
        post_data=post_data,
    )

def response_to_string(response):
    """Return a string representation of Response object

    :param response:    Requests.Response object to represent.

    :returns:           String representation of the provided response.

    """
    code_and_message = ''
    content = ''
    try:
        response_json = json.loads(response.content)

        if 'error' in response_json and response_json['error'] and ('code' in response_json['error'] and 'message' in response_json['error']):
            code = int(response_json['error']['code'])
            message = response_json['error']['message'].encode('utf-8')
            code_and_message = '\nCloudFS Error Code: {}\nCloudFS Message: {}'.format(code, message)

        content = 'Body:\n{}'.format(pprint.pformat(response_json))
    except:
        pass

    if len(content) == 0 and len(response.content) > 0:
        content = 'Body:\n{}'.format(response.content)


    return 'HTTP Code: {code}{cloudfs_message}\n{response_headers}{content}'.format(
        code=response.status_code,
        cloudfs_message=code_and_message,
        response_headers=dict_string(response.headers),
        content=content
    )
