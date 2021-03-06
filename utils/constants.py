from decimal import Decimal


REG_TEL = REG_FAX = r'^\d+[0-9-]+\d+$'
REG_POST_CODE = r"\d{3}[-]?\d{4}"
REG_PHONE = r'\d{3}[-]?\d{4}[-]?\d{4}'

MIME_TYPE_EXCEL = 'application/excel'
MIME_TYPE_PDF = 'application/pdf'
MIME_TYPE_ZIP = 'application/zip'
MIME_TYPE_HTML = 'text/html'
MIME_TYPE_STREAM = 'application/octet-stream'

CHOICE_ORG_TYPE = (
    ('01', "事業部"),
    ('02', "部署"),
    ('03', "課"),
)
CHOICE_RESIDENCE_TYPE = (
    ('01', "特定活動"),
    ('02', "企業内転勤"),
    ('03', "技術・人文知識・国際業務"),
    ('04', "高度専門職1号"),
    ('09', "高度専門職2号"),
    ('05', "永住者"),
    ('06', "永住者の配偶者"),
    ('07', "日本人の配偶者"),
    ('08', "日本籍"),
)
CHOICE_GENDER = (
    ('1', "男"),
    ('2', "女"),
)
CHOICE_MARRIED = (
    ('0', "未婚"),
    ('1', "既婚"),
)
CHOICE_PAYMENT_MONTH = (
    ('1', "翌月"),
    ('2', "翌々月"),
    ('3', "３月"),
    ('4', "４月"),
    ('5', "５月"),
    ('6', "６月")
)
CHOICE_PAYMENT_DAY = (
    ('01', '1日'),
    ('02', '2日'),
    ('03', '3日'),
    ('04', '4日'),
    ('05', '5日'),
    ('06', '6日'),
    ('07', '7日'),
    ('08', '8日'),
    ('09', '9日'),
    ('10', '10日'),
    ('11', '11日'),
    ('12', '12日'),
    ('13', '13日'),
    ('14', '14日'),
    ('15', '15日'),
    ('16', '16日'),
    ('17', '17日'),
    ('18', '18日'),
    ('19', '19日'),
    ('20', '20日'),
    ('21', '21日'),
    ('22', '22日'),
    ('23', '23日'),
    ('24', '24日'),
    ('25', '25日'),
    ('26', '26日'),
    ('27', '27日'),
    ('28', '28日'),
    ('29', '29日'),
    ('30', '30日'),
    ('99', '月末')
)
CHOICE_TAX_RATE = (
    (Decimal('0.00'), "税なし"),
    (Decimal('0.05'), "5％"),
    (Decimal('0.08'), "8％"),
    (Decimal('0.10'), "10％"),
)
CHOICE_DECIMAL_TYPE = (
    ('0', "四捨五入"),
    ('1', "切り捨て"),
    ('2', '切り上げ'),
)
CHOICE_PROJECT_STATUS = (
    ('1', "提案"),
    ('2', "予算審査"),
    ('3', "予算確定"),
    ('4', "実施中"),
    ('5', "完了")
)
CHOICE_PROJECT_BUSINESS_TYPE = (
    ('01', "金融（銀行）"),
    ('02', "金融（保険）"),
    ('03', "金融（証券）"),
    ('04', "製造"),
    ('05', "サービス"),
    ('06', "その他")
)
CHOICE_ATTENDANCE_TYPE = (
    ('1', "１５分ごと"),
    ('2', "３０分ごと"),
    ('3', "１時間ごと")
)
CHOICE_PROJECT_MEMBER_STATUS = (
    ('1', "提案中"),
    ('2', "作業確定")
)
CHOICE_PROJECT_ROLE = (
    ("OP", "OP：ｵﾍﾟﾚｰﾀｰ"),
    ("PG", "PG：ﾌﾟﾛｸﾞﾗﾏｰ"),
    ("SP", "SP：ｼｽﾃﾑﾌﾟﾛｸﾞﾗﾏｰ"),
    ("SE", "SE：ｼｽﾃﾑｴﾝｼﾞﾆｱ"),
    ("SL", "SL：ｻﾌﾞﾘｰﾀﾞｰ"),
    ("L", "L：ﾘｰﾀﾞｰ"),
    ("M", "M：ﾏﾈｰｼﾞｬｰ")
)
CHOICE_CUSTOMER_CONTRACT_TYPE = (
    ('01', "業務委託"),
    ('02', "準委任"),
    ('03', "派遣"),
    ('04', "一括"),
    # ('05', "ソフト加工"),
    ('10', "出向"),
    # ('11', "出向（在籍）"),
    # ('12', "出向（完全）"),
    ('99', "その他"),
)
CHOICE_BP_CONTRACT_TYPE = (
    ('01', "業務委託"),
    ('02', "準委任"),
    ('03', "派遣"),
    ('04', "一括"),
    # ('05', "ソフト加工"),
    # ('10', "出向"),
    ('11', "出向（在籍）"),
    ('12', "出向（完全）"),
    ('99', "その他"),
)
CHOICE_CALCULATE_TYPE = (
    ('01', '固定１６０時間'),
    ('02', '営業日数 × ８'),
    ('03', '営業日数 × ７.９'),
    ('04', '営業日数 × ７.７５'),
    ('99', "その他（任意）"),
)
CHOICE_BOOLEAN = (
    (True, 'はい'),
    (False, 'いいえ'),
)
CHOICE_BANK_ACCOUNT_TYPE = (
    ('1', "普通預金"),
    ('2', "定期預金"),
    ('3', "総合口座"),
    ('4', "当座預金"),
    ('5', "貯蓄預金"),
    ('6', "大口定期預金"),
    ('7', "積立定期預金")
)
CHOICE_MEMBER_TYPE = (
    ('1', "正社員"),
    ('2', "契約社員"),
    ('3', "個人事業者"),
    ('4', "他社技術者"),
    ('5', "パート"),
    ('6', "アルバイト"),
    ('7', "正社員（試用期間）")
)
CHOICE_SALESPERSON_TYPE = (
    ('0', "営業部長"),
    ('1', "その他"),
    ('5', "営業担当"),
    ('6', "取締役"),
    ('7', "代表取締役社長")
)
CHOICE_BUSINESS_TYPE = (
    ('01', "業務の種類（プログラマー）"),
    ('02', "業務の種類（シニアプログラマー）"),
    ('03', "業務の種類（システムエンジニア）"),
    ('04', "業務の種類（シニアシステムエンジニア）"),
    ('05', "業務の種類（課長）"),
    ('06', "業務の種類（部長）"),
    ('07', "業務の種類（営業担当）"),
    ('08', "業務の種類（マネージャー）"),
    ('09', "業務の種類（新規事業推進部担当）"),
    ('10', "業務の種類（一般社員）"),
    ('11', "業務の種類（担当課長）"),
    ('12', "業務の種類（担当部長）"),
    ('13', "業務の種類（シニアコンサルタント兼中国現地担当）"),
    ('14', "業務の種類（営業アシスタント事務）"),
    ('15', "業務の種類（経営管理業務及び管理）"),
    ('17', "業務の種類（システムエンジニア業務および課内の管理）"),
    ('18', "業務の種類（システムエンジニア業務および課内の管理補佐）"),
    ('16', "その他")
)
CHOICE_INSURANCE = (
    ('1', "加入する"),
    ('0', "加入しない")
)
CHOICE_MONTH_LIST = (
    ('01', '1月'),
    ('02', '2月'),
    ('03', '3月'),
    ('04', '4月'),
    ('05', '5月'),
    ('06', '6月'),
    ('07', '7月'),
    ('08', '8月'),
    ('09', '9月'),
    ('10', '10月'),
    ('11', '11月'),
    ('12', '12月')
)
CHOICE_POSITION = (
    (Decimal('1.0'), "代表取締役"),
    (Decimal('1.1'), "取締役"),
    (Decimal('3.0'), "事業部長"),
    (Decimal('3.1'), "副事業部長"),
    (Decimal('4.0'), "部長"),
    (Decimal('5.0'), "担当部長"),
    (Decimal('6.0'), "課長"),
    (Decimal('7.0'), "担当課長"),
    (Decimal('8.0'), "PM"),
    (Decimal('9.0'), "リーダー"),
    (Decimal('10.0'), "サブリーダー"),
    (Decimal('11.0'), "勤務統計者")
)
CHOICE_PARTNER_POSITION = (
    ('01', "代表取締役社長"),
    ('02', "取締役"),
    ('03', "営業"),
    ('99', "その他"),
)
CHOICE_CONTRACT_STATUS = (
    ('01', "登録済み"),
    ('02', "承認待ち"),
    ('03', "承認済み"),
    ('04', "廃棄"),
    ('05', "自動更新")
)
CHOICE_MAIL_GROUP = (
    ('0400', '注文書と注文請書の送付'),
)
CHOICE_CONTRACT_COMMENT = (
    ('0001', '雇用期間'),
    ('0002', '職位'),
    ('0003', '就業の場所'),
    ('0004', '業務の種類'),
    ('0005', '業務の種類その他'),
    ('0006', '業務のコメント'),
    ('0007', '就業時間'),
    ('0200', '給与締め切り日及び支払日'),
    ('0201', '昇給及び降給'),
    ('0202', '賞与'),
    ('0300', '休日'),
    ('0301', '有給休暇'),
    ('0302', '無給休暇'),
    ('0800', '退職に関する項目'),
    ('9999', 'その他備考'),
)
CHOICE_CONTRACT_ALLOWANCE = (
    ('0001', '基本給（税抜）'),
    ('0002', '基本給（税金）'),
    ('0003', '基本給その他'),
    ('0100', '下限時間'),
    ('0101', '上限時間'),
    ('0102', '計算用下限時間'),
    ('0103', '計算用上限時間'),
    ('1000', '現場手当'),
    ('1001', '役職手当'),
    ('1002', '職務手当'),
    ('1003', '精勤手当'),
    ('1004', '安全手当'),
    ('1005', '資格手当'),
    ('1006', '通勤手当'),
    ('1007', '残業手当'),
    ('1008', '欠勤控除'),
    ('9999', 'その他手当'),
)
CHOICE_ALLOWANCE_UNIT = (
    ('01', '円/月'),
    ('02', '円/年'),
    ('03', '円/時間'),
    ('10', '時間'),
)

DICT_MONTH_EN = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'Mai',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec',
}
DICT_PROJECT_STATUS_CLASS = {
    '1': 'lime',  # 提案
    '2': 'purple',  # 予算審査
    '3': 'blue',  # 予算確定
    '4': 'green',  # 実施中
    '5': 'grey',  # 完了
}
DICT_PROJECT_MEMBER_STATUS_CLASS = {
    '1': 'lime',  # 提案中
    '2': 'green',  # 作業確定
}

CONFIG_GROUP_EMAIL = 'email'
CONFIG_EMAIL_ADDRESS = 'admin_email_address'
CONFIG_EMAIL_SMTP_HOST = 'admin_email_smtp_host'
CONFIG_EMAIL_SMTP_PORT = 'admin_email_smtp_port'
CONFIG_EMAIL_PASSWORD = 'admin_email_password'
CONFIG_GROUP_BP_ORDER = 'bp_order'
CONFIG_BP_ORDER_DELIVERY_PROPERTIES = 'delivery_properties'
CONFIG_BP_ORDER_PAYMENT_CONDITION = 'payment_condition'
CONFIG_BP_ORDER_CONTRACT_ITEMS = 'contract_items'

ERROR_DELETE_PROTECTED = '関連付けの {name} が存在しますので、削除できません。'
ERROR_DATE_CONFLICT = '日付 {date} が重複しています。'
ERROR_DATE_CONTRADICT = '{start} と {end} の期間が不正です。'
ERROR_DATE_FINISHED_MONTH = "終了年月「{year}年{month}月」は不正です、開始年月以降に選択してください。"
ERROR_NO_SALESPERSON = '{name}の営業員は設定されていません。'
ERROR_NOT_IMPLEMENTED = '未実装です。'
ERROR_NO_ATTENDANCE = '{name} の出勤情報がありません。'
ERROR_NO_PARTNER_CONTRACT = '{name}は{company}の契約がありません。'
ERROR_MULTI_PARTNER_CONTRACT = '{name}は{company}の契約が複数あります。'
ERROR_MULTI_SALESPERSON = '{name}の営業員は複数います。'
ERROR_UNKNOWN_ATTACHMENT = '識別できないファイルです。'
ERROR_UNKNOWN_CATEGORY = '処理できません。'
ERROR_FILE_NOT_FOUND = 'ファイルは見つかりません。'
ERROR_REQUIRE_FIELD = '{name} は必須項目です。'
ERROR_ORGANIZATION_POSITION = '{org_type} の場合 {value} は選択できません。'
ERROR_DATA_DUPLICATE = 'データは重複しています。'
ERROR_MAIL_GROUP_NOT_FOUND = 'メールグループ {name} は設定されていません。'
ERROR_MAIL_GROUP_MULTI_FOUND = 'メールグループ {name} は複数設定されています。'

LABEL_BP_ORDER_DEFAULT_LOCATION = "弊社指定場所"
