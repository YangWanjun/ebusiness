from decimal import Decimal


REG_TEL = REG_FAX = r'^\d+[0-9-]+\d+$'
REG_POST_CODE = r"\d{3}[-]?\d{4}"
REG_PHONE = r'\d{3}[-]?\d{4}[-]?\d{4}'

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
CHOICE_SEX = (
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