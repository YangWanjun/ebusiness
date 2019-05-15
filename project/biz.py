from django.db import connection

from utils import common


def get_project_attendance_list(project_id):
    """案件の月ごと出勤リスト

    :param project_id: 案件ＩＤ
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_project_attendance_list', (project_id,))
        data = common.dictfetchall(cursor)
    for row in data:
        row['url'] = '/project/{pk}/attendance/{year}/{month}'.format(
            pk=project_id,
            year=row['year'],
            month=row['month'],
        )
    return data
