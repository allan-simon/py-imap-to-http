import os
import asyncio
import base64
import importlib

from aioimaplib import aioimaplib
import mailparser
import requests
from requests_toolbelt import MultipartEncoder

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


IMAP_SERVER = os.environ['IMAP_SERVER']
IMAP_USER = os.environ['IMAP_USER']
IMAP_PASSWORD = os.environ['IMAP_PASSWORD']

IMAP_CHECK_FOLDER = os.environ.get('IMAP_CHECK_FOLDER', 'INBOX')
IMAP_SUCCESS_FOLDER = os.environ['IMAP_SUCCESS_FOLDER']
IMAP_FAILURE_FOLDER = os.environ['IMAP_SUCCESS_FOLDER']

IMAP_POST_TO_URL = os.environ['IMAP_POST_TO_URL']

@asyncio.coroutine
def idle_loop(host, user, password):
    imap_client = aioimaplib.IMAP4_SSL(host=host, timeout=30)
    yield from imap_client.wait_hello_from_server()

    login_response = yield from imap_client.login(user, password)
    if login_response.result == "NO":
        raise Exception("Authentication failed")

    response = yield from imap_client.select(IMAP_CHECK_FOLDER)

    while True:
        response = yield from imap_client.uid('fetch', '1:*', 'RFC822')

        # start is: 2 FETCH (UID 18 RFC822 {42}
        # middle is the actual email content
        # end is simply ")"
        # the last line is removed as it's only "success"-ish information
        # the iter + zip tricks is to iterate three by three
        iterator = iter(response.lines[:-1])
        for start, middle, _end in zip(iterator, iterator, iterator):
            if not isinstance(middle, bytes):
                continue
            # index 3 because the actual id is at the position 3
            # 0   1     2   3
            # |   |     |   |
            # v   v     v   v
            # 2 FETCH (UID 18 RFC822 {42}
            email_uid = start.split(' ')[3]
            parsed_email = mailparser.parse_from_bytes(middle)
            treated_correctly = treat_email(parsed_email)
            if treated_correctly:
                yield from imap_client.uid(
                    'move',
                    email_uid + ':' + email_uid ,
                    IMAP_SUCCESS_FOLDER,
                )
            else:
                yield from imap_client.uid(
                    'store',
                    email_uid,
                    '-FLAGS',
                    '(\Seen)'
                )
                yield from imap_client.uid(
                    'move',
                    email_uid + ':' + email_uid ,
                    IMAP_FAILURE_FOLDER,
                )

        idle = yield from imap_client.idle_start(timeout=60)
        print((yield from imap_client.wait_server_push()))

        imap_client.idle_done()
        yield from asyncio.wait_for(idle, 30)


def treat_email(email):

    print(email.subject)
    fields = {
        # both 'from' and 'to' fields looks like
        # [('Display Name', 'email')] hence the [0][1]
        'from': email.from_[0][1],
        'to': email.to[0][1],
        'message_id': email.message_id,
        'body': ''.join(email.text_plain),
    }

    for i, attachment in enumerate(email.attachments):
        fields['attachments[%d]' % i] = (
            attachment['filename'],
            base64.b64decode(attachment['payload']),
            attachment['mail_content_type'],
        )

    multipart = MultipartEncoder(fields=fields)

    response = requests.post(
        IMAP_POST_TO_URL,
        data=multipart,
        headers={'Content-Type': multipart.content_type}
    )
    print(response)
    return response.status_code < 299

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        idle_loop(
            IMAP_SERVER,
            IMAP_USER,
            IMAP_PASSWORD,
        )
    )
