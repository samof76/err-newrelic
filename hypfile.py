#!/usr/bin/env python3

import os
import json
import re
import requests
import sys
import time

from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


def hipchat_file(token, room, filepath, host='api.hipchat.com'):

    """ Send file to a HipChat room via API version 2
    Parameters
    ----------
    token : str
        HipChat API version 2 compatible token - must be token for active user
    room: str
        Name or API ID of the room to notify
    filepath: str
        Full path of file to be sent
    host: str, optional
        Host to connect to, defaults to api.hipchat.com
    """

    if not os.path.isfile(filepath):
        raise ValueError("File '{0}' does not exist".format(filepath))

    url = "https://{0}/v2/room/{1}/share/file".format(host, room)
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept-Charset': 'UTF-8',
        'Content-Type': 'multipart/related',
    }
    raw_body = MIMEMultipart('related')
    with open(filepath, 'rb') as fin:
        img = MIMEImage(fin.read())
        img.add_header(
            'Content-Disposition',
            'attachment',
            name = 'file',
            filename = filepath.split('/')[-1]
        )
        raw_body.attach(img)    

    raw_headers, body = raw_body.as_string().split('\n\n', 1)
    boundary = re.search('boundary="([^"]*)"', raw_headers).group(1)
    headers['Content-Type'] = 'multipart/related; boundary="{}"'.format(boundary)
    r = requests.post(url, data = body, headers = headers)


# my_token = 'XXXXXXXXXXXXX'
# my_room = 'XXXXXXXXX'
# my_file = '/tmp/app_reponse_time_01f2f3f10831441e935a88666658092f.png'

# try:
#     hipchat_file(my_token, my_room, my_file)
# except Exception as e:
#         msg = "[ERROR] HipChat file failed: '{0}'".format(e)
#         print(msg, file=sys.stderr)
#         sys.exit(1) 