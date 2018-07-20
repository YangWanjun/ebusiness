# coding: utf-8
import os
import sys
import getpass
import MySQLdb
import django
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ebusiness.settings")
django.setup()

if sys.platform == 'win32' and getpass.getuser() == 'EB097':
    user = 'root'
    password = 'root'
    host = 'localhost'
elif sys.platform in ('linux2', 'linux'):
    user = 'root'
    password = os.environ['MYSQL_ENV_MYSQL_ROOT_PASSWORD']
    host = os.environ['MYSQL_PORT_3306_TCP_ADDR']
else:
    user = 'root'
    password = 'root'
    host = '127.0.0.1'


def main():
    del_migration_records()
    del_migration_files()
    migrate()


def migrate():
    call_command('migrate', '--fake')
    call_command('makemigrations')
    call_command('migrate', '--fake')


def del_migration_records():
    con = MySQLdb.connect(user=user, passwd=password, db='eb_sales_new', host=host)
    cursor = con.cursor()
    try:
        cnt = cursor.execute("delete from django_migrations")
        print('EXEC: delete from django_migrations. %s rows deleted' % cnt)
        con.commit()
    except Exception as e:
        con.roolback()
        raise e
    finally:
        cursor.close()
        con.close()


def del_migration_files():
    root_path = os.path.dirname(os.path.realpath(__file__))
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            if filename in ('__init__.py', '__init__.pyc'):
                continue
            if os.path.basename(root) == 'migrations':
                path = os.path.join(root, filename)
                os.remove(path)
                print('DEL: %s' % path)


if __name__ == '__main__':
    main()
