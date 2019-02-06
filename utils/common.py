from urllib.parse import urlparse


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict

    :param cursor:
    :return:
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def to_relative_url(absolute_url):
    """絶対URLを相対URLに変換

    :param absolute_url:
    :return:
    """
    result = urlparse(absolute_url)
    return result.path
