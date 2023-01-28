from sparkpost import SparkPost

from config import Config
from common import rollbar

__all__ = ['send_mail_html']


# sparkpost
sparky = SparkPost(Config.sparkpost_api_key)

## for prodaj logo
html_logo = ''.join([
    '<html>',
    '<body style="width: 500px;">',
    '<img src="{0}/static/img/logo.png" height="100" style="display: block; margin: 0 auto;">',
    '{1}',
    '</body>',
    '</html>'
])

async def send_mail_html(from_mail, to_mail, subject, html):

    html = html_logo.format(Config.url, html)

    try:
        res = sparky.transmissions.send(
            recipients=to_mail if isinstance(to_mail, list) or isinstance(to_mail, tuple) else [to_mail],
            html=html,
            from_email=from_mail,
            subject=subject,
            track_opens=False,
            track_clicks=False,
        )
    except Exception as e:
        rollbar.report_exc_info()
        print(e)
