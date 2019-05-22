import xlsxwriter
from io import BytesIO


def generate_request(data, request_no):
    if 'detail_all' in data and data.get('detail_all'):
        is_lump = True
        is_bp_request = False
    else:
        is_lump = False
        is_bp_request = True
    output = BytesIO()
    book = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = book.add_worksheet()

    # タイトル設定
    title_format = book.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 18,
        'underline': 2
    })
    sheet.merge_range('A1:P1', "　　御　請　求　書　　", title_format)
    sheet.write_string('M3', "請求番号")
    sheet.write_number('O3', int(request_no))
    sheet.write_string('M4', "発  行 日")
    sheet.write_string('O4', data['heading']['PUBLISH_DATE'])
    sheet.write_string('B3', "〒" + data['heading']['CLIENT_POST_CODE'])
    sheet.write_string('B4', data['heading']['CLIENT_ADDRESS'])
    sheet.write_string('B6', "Tel: " + data['heading']['CLIENT_TEL'])
    name_format = book.add_format({
        'bold': True,
        'font_size': 12,
        'underline': 1
    })
    sheet.write_string('B8', data['heading']['CLIENT_COMPANY_NAME'] + "御中", name_format)
    sheet.write_string('B10', "　下記のとおりご請求申し上げます。")
    format1 = book.add_format({
        'bold': True,
        'font_size': 12
    })
    sheet.write_string('B12', "御請求額　 ：　", format1)
    format1 = book.add_format({
        'bold': True,
        'font_size': 14,
        'underline': 2
    })
    sheet.write_string('E12', "\\" + data['heading']['ITEM_AMOUNT_ALL_COMMA'] + "円", format1)
    sheet.write_string('B14', "作業期間　   ：")
    sheet.write_string('E14', data['heading']['WORK_PERIOD'])
    if is_bp_request:
        sheet.write_string('B16', "お支払い期限　：")
        sheet.write_string('E16', data['heading']['REMIT_DATE'])
    else:
        sheet.write_string('B16', "注文番号　   ：")
        sheet.write_string('E16', data['heading']['ORDER_NO'])
        sheet.write_string('B18', "注文日　　　  ：")
        sheet.write_string('E18', data['heading']['REQUEST_DATE'])
        sheet.write_string('B20', "契約件名　　 ：　")
        sheet.write_string('E20', data['heading']['CONTRACT_NAME'])
        sheet.write_string('B22', "お支払い期限　：")
        sheet.write_string('E22', data['heading']['REMIT_DATE'])
    sheet.write_string('M10', "〒" + data['heading']['POST_CODE'])
    sheet.write_string('M11', data['heading']['ADDRESS'])
    sheet.write_string('M12', data['heading']['COMPANY_NAME'])
    sheet.write_string('M13', "代表取締役　　%s" % data['heading']['MASTER'] or u"")
    sheet.write_string('M14', "TEL：%s" % data['heading']['TEL'])
    sheet.insert_textbox('M15', '', {
        'width': 90,
        'height': 90,
        'x_offset': 4,
        'y_offset': 6,
        'align': {'vertical': 'middle', 'horizontal': 'center'}
    })
    sheet.insert_textbox('O15', '', {
        'width': 90,
        'height': 90,
        'x_offset': 6,
        'y_offset': 6,
        'align': {'vertical': 'middle', 'horizontal': 'center'}
    })
    sheet.insert_textbox('P15', '', {
        'width': 90,
        'height': 90,
        'x_offset': -2,
        'y_offset': 6,
        'align': {'vertical': 'middle', 'horizontal': 'center'}
    })
    title_format = book.add_format({
        'font_size': 11,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })
    cell_format = book.add_format({
        'font_size': 11,
        'border': 1,
    })
    range1_format = book.add_format({
        'font_size': 11,
        'left': 1,
        'top': 1,
        'bottom': 1
    })
    range2_format = book.add_format({
        'font_size': 11,
        'top': 1,
        'bottom': 1
    })
    range3_format = book.add_format({
        'font_size': 11,
        'right': 1,
        'top': 1,
        'bottom': 1
    })
    num_format = book.add_format({'num_format': '#,###', 'border': 1})
    float_format = book.add_format({'num_format': '#,###.00', 'border': 1})
    start_row = 24

    def border_row(row_index, is_lump_temp=False):
        sheet.write_string(row_index, 1, '', cell_format)
        sheet.write_string(row_index, 14, '', cell_format)
        sheet.write_string(row_index, 15, '', cell_format)
        if is_lump_temp:
            sheet.write_string(row_index, 2, '', range1_format)
            sheet.write_string(row_index, 3, '', range2_format)
            sheet.write_string(row_index, 4, '', range2_format)
            sheet.write_string(row_index, 5, '', range2_format)
            sheet.write_string(row_index, 6, '', range2_format)
            sheet.write_string(row_index, 7, '', range2_format)
            sheet.write_string(row_index, 8, '', range2_format)
            sheet.write_string(row_index, 9, '', range2_format)
            sheet.write_string(row_index, 10, '', range3_format)
            sheet.write_string(row_index, 11, '', range1_format)
            sheet.write_string(row_index, 12, '', range2_format)
            sheet.write_string(row_index, 13, '', range3_format)
        else:
            sheet.write_string(row_index, 2, '', range1_format)
            sheet.write_string(row_index, 3, '', range2_format)
            sheet.write_string(row_index, 4, '', range2_format)
            sheet.write_string(row_index, 5, '', range2_format)
            sheet.write_string(row_index, 6, '', range3_format)
            sheet.write_string(row_index, 7, '', cell_format)
            sheet.write_string(row_index, 8, '', cell_format)
            sheet.write_string(row_index, 9, '', cell_format)
            sheet.write_string(row_index, 10, '', cell_format)
            sheet.write_string(row_index, 11, '', cell_format)
            sheet.write_string(row_index, 12, '', cell_format)
            sheet.write_string(row_index, 13, '', cell_format)

    if data['MEMBERS']:
        sheet.write_string('B24', "番号", title_format)
        sheet.merge_range('C24:G24', "項　　　　目", title_format)
        sheet.write_string('H24', "単価", title_format)
        sheet.write_string('I24', "作業H", title_format)
        sheet.write_string('J24', "率", title_format)
        sheet.write_string('K24', "Min/MaxH", title_format)
        sheet.write_string('L24', "減", title_format)
        sheet.write_string('M24', "増", title_format)
        sheet.write_string('N24', "その他", title_format)
        sheet.write_string('O24', "金額", title_format)
        sheet.write_string('P24', "備考", title_format)
        for item in data['MEMBERS']:
            sheet.write_number(start_row, 1, int(item['NO']), cell_format)
            sheet.merge_range(start_row, 2, start_row, 6, item['ITEM_NAME'], cell_format)
            sheet.write_number(start_row, 7, item['ITEM_PRICE'], num_format)
            if item['ITEM_WORK_HOURS']:
                sheet.write_number(start_row, 8, float(item['ITEM_WORK_HOURS']), float_format)
            else:
                sheet.write_string(start_row, 8, '', cell_format)
            sheet.write_number(start_row, 9, item['ITEM_RATE'], float_format)
            sheet.write_string(start_row, 10, item['ITEM_MIN_MAX'], cell_format)
            sheet.write_number(start_row, 11, item['ITEM_MINUS_PER_HOUR'], num_format)
            sheet.write_number(start_row, 12, item['ITEM_PLUS_PER_HOUR'], num_format)
            sheet.write_string(start_row, 13, item['ITEM_OTHER'], cell_format)
            sheet.write_number(start_row, 14, item['ITEM_AMOUNT_TOTAL'], num_format)
            sheet.write_string(start_row, 15, item['ITEM_COMMENT'], cell_format)
            start_row += 1
    elif data['detail_all']:
        item = data['detail_all']
        sheet.write_string('B24', "番号", title_format)
        sheet.merge_range('C24:K24', "項　　　　目", title_format)
        sheet.merge_range('L24:N24', "単位", title_format)
        sheet.write_string('O24', "金額", title_format)
        sheet.write_string('P24', "備考", title_format)
        sheet.write_number('B25', int(item['NO']), cell_format)
        sheet.merge_range('C25:K25', item['ITEM_NAME_ATTENDANCE_TOTAL'], cell_format)
        sheet.merge_range('L25:N25', item['ITEM_UNIT'], cell_format)
        sheet.write_number('O25', data['heading']['ITEM_AMOUNT_ATTENDANCE'], num_format)
        sheet.write_string('P25', item['ITEM_COMMENT'], cell_format)
        start_row += 1
    if start_row < 44:
        for i in range(start_row, 44):
            border_row(i, is_lump)
        start_row = 44
    else:
        start_row += 1
    for i in range(start_row, start_row + 5):
        border_row(i, is_lump)
    sheet.merge_range(start_row + 0, 3, start_row + 0, 5, "（小計）", range2_format)
    sheet.write_number(start_row + 0, 14, data['heading']['ITEM_AMOUNT_ATTENDANCE'], num_format)
    sheet.merge_range(start_row + 1, 3, start_row + 1, 5, "(消費税）", range2_format)
    sheet.write_number(start_row + 1, 14, data['heading']['ITEM_AMOUNT_ATTENDANCE_TAX'], num_format)
    sheet.merge_range(start_row + 2, 3, start_row + 2, 5, "(合計）", range2_format)
    sheet.write_number(start_row + 2, 14, data['heading']['ITEM_AMOUNT_ATTENDANCE_ALL'], num_format)
    sheet.merge_range(start_row + 3, 3, start_row + 3, 5, "[控除、追加]", range2_format)
    sheet.write_string(start_row + 4, 1, "控除", cell_format)
    start_row += 5
    if data['EXPENSES']:
        for i, item in enumerate(data['EXPENSES']):
            border_row(start_row, is_lump)
            if i == 0:
                sheet.write_string(start_row, 1, "追加", cell_format)
            # sheet.write_string(start_row, 3, item['ITEM_EXPENSES_CATEGORY_SUMMARY'], range2_format)
            sheet.merge_range(start_row, 3, start_row, 13, item['ITEM_EXPENSES_CATEGORY_SUMMARY'], range3_format)
            sheet.write_number(start_row, 14, item['ITEM_EXPENSES_CATEGORY_AMOUNT'], num_format)
            start_row += 1
    else:
        border_row(start_row, is_lump)
        sheet.write_string(start_row, 1, "追加", cell_format)
        start_row += 1
    border_row(start_row, is_lump)
    sheet.merge_range(start_row, 3, start_row, 4, "(総計）", range2_format)
    sheet.write_number(start_row, 14, data['heading']['ITEM_AMOUNT_ALL'], num_format)
    sheet.write_string(start_row + 1, 1, "お振込銀行口座")
    sheet.write_string(start_row + 2, 2, data['heading']['BANK_NAME'])
    sheet.write_string(start_row + 3, 2, "%s（%s）" % (data['heading']['BRANCH_NAME'], data['heading']['BRANCH_NO']))
    sheet.write_string(start_row + 4, 2, "%s　%s" % (data['heading']['ACCOUNT_TYPE'], data['heading']['ACCOUNT_NUMBER']))
    sheet.write_string(start_row + 5, 2, "名義　　　　%s" % (data['heading']['BANK_ACCOUNT_HOLDER'],))
    border_right_format = book.add_format({'right': 1})
    border_top_format = book.add_format({'top': 1})
    for i in range(start_row + 1, start_row + 6):
        sheet.write_string(i, 0, '', border_right_format)
    for i in range(start_row + 1, start_row + 6):
        sheet.write_string(i, 15, '', border_right_format)
    for i in range(1, 16):
        sheet.write_string(start_row + 6, i, '', border_top_format)

    # 全体の設定
    sheet.hide_gridlines()
    sheet.fit_to_pages(1, 1)
    sheet.set_column('A:A', 0.9)
    sheet.set_column('B:B', 4.9)
    sheet.set_column('C:C', 2.9)
    sheet.set_column('D:D', 2.9)
    sheet.set_column('E:E', 3.0)
    sheet.set_column('F:F', 3.0)
    sheet.set_column('G:G', 3.0)
    sheet.set_column('H:H', 10.3)
    sheet.set_column('I:I', 10.7)
    sheet.set_column('J:J', 4.9)
    sheet.set_column('K:K', 15.3)
    sheet.set_column('L:L', 4.9)
    sheet.set_column('M:M', 4.9)
    sheet.set_column('N:N', 6.6)
    sheet.set_column('O:O', 13.6)
    sheet.set_column('P:P', 12.4)
    sheet.set_row(0, 23.25)
    for i in range(1, 23):
        sheet.set_row(i, 15.5)
    book.close()
    return output
