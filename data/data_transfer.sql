insert into eb_sales_new.eb_business_partner
(created_dt, updated_dt, name, kana, president, found_date, capital, post_code, address1, address2, tel, fax, employee_count, sales_amount, payment_month, payment_day, middleman, comment)
SELECT current_timestamp(), current_timestamp(), name, japanese_spell, president, found_date, capital, post_code, address1, address2, tel, fax, employee_count, sale_amount, payment_month, payment_day, middleman, comment
  FROM eb_sales.eb_subcontractor
