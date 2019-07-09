import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ebusiness.settings")
django.setup()

from django.db import connection
from utils.common import dictfetchall


def main():
    print(len(get_members_contracts()))


def get_members_contracts():
    with connection.cursor() as cursor:
        cursor.execute("""
        select c.id
     , ct2.id as company_content_type_id
     , c.company_id as company_object_id
     , ct1.id as content_type_id
     , c.member_id as object_id
     , c.contract_no
     , c.contract_date
     , c.start_date
     , c.end_date
     , c.member_type
     , c.endowment_insurance as insurance
     , c.is_loan
     , '01' as calculate_type
  from eb_contract c
  join django_content_type ct1 on ct1.app_label = 'eb' and ct1.model = 'member'
  join django_content_type ct2 on ct2.app_label = 'eb' and ct2.model = 'company'
 where c.status not in ('04', '05')
   and c.is_deleted = 0
        """)
        return dictfetchall(cursor)


if __name__ == '__main__':
    main()
