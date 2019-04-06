import os


def main(path, user, pwd, db, host):
    if os.path.exists(path):
        path_win = os.path.join(path, 'sql_win.bat')
        path_mac = os.path.join(path, 'sql_mac.sh')
        with open(path_win, 'w') as f_win, open(path_mac, 'w') as f_mac:
            f_mac.write('#!/bin/sh' + '\n')
            f_mac.write('\n')
            for filename in sorted(os.listdir(path)):
                if os.path.splitext(filename)[1].upper() == '.SQL':
                    s = get_cmd(filename, user, pwd, db, host)
                    f_win.write(s + '\n')
                    s = get_cmd(filename, user, pwd, db, host)
                    f_mac.write(s + '\n')


def get_cmd(filename, user, pwd, db, host=None):
    return 'mysql {host} {user} {pwd} --default-character-set=utf8 {database} < {filename}'.format(
        host=('-h {}'.format(host) if host else ''),
        user=('-u {}'.format(user) if user else ''),
        pwd=('-p{}'.format(pwd) if pwd else ''),
        database=(db if db else ''),
        filename=(filename if filename else ''),
    )


if __name__ == '__main__':
    ddl_path = os.path.join(os.path.dirname(__file__), 'SQL')
    in_user = input('ユーザー名を入力してください(default: root)：') or 'root'
    in_pwd = input('パスワードを入力してください(default: root)：') or 'root'
    in_db = input('データベースを入力してください(default: eb_sales)：') or 'eb_sales'
    in_host = input('ホストを入力してください(default: 192.168.99.100)：') or '192.168.99.100'
    main(ddl_path, in_user, in_pwd, in_db, in_host)
