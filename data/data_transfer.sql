-- 協力会社一覧
insert into eb_sales_new.eb_business_partner
(created_dt, updated_dt, name, kana, president, found_date, capital, post_code, address1, address2, tel, fax, employee_count, sales_amount, payment_month, payment_day, middleman, comment)
SELECT current_timestamp(), current_timestamp(), name, japanese_spell, president, found_date, capital, post_code, address1, address2, tel, fax, employee_count, sale_amount, payment_month, payment_day, middleman, comment
  FROM eb_sales.eb_subcontractor
;
-- 社員一覧
insert into eb_sales_new.eb_member
(created_dt, updated_dt, last_name, first_name, last_name_ja, first_name_ja, last_name_en, first_name_en, gender, country,
birthday,graduate_date,join_date,email,private_email,post_code,address1,address2,lat,lng,nearest_station,years_in_japan,
phone,marriage,japanese_description,certificate,skill_description,comment,is_unofficial,id_number,id_card_expired_date,
visa_start_date,visa_expire_date,passport_number,passport_expired_dt,residence_type,pay_owner,pay_owner_kana,
pay_account,avatar_url,pay_bank_id ,pay_branch_id)
SELECT ifnull(created_date, ifnull(updated_date, current_timestamp())) as created_date, ifnull(updated_date, current_timestamp()) as updated_date, first_name, last_name, first_name_ja, last_name_ja, first_name_en, last_name_en, sex, country,
birthday, graduate_date, join_date, email, private_email, post_code, address1, address2, lat, lng, nearest_station, years_in_japan,
phone, is_married, japanese_description, certificate, skill_description, comment, is_unofficial,id_number,id_card_expired_date,
visa_start_date,visa_expire_date,passport_number,passport_expired_dt,residence_type,pay_owner,pay_owner_kana,
pay_account,avatar_url,null as pay_bank_id , null as pay_branch_id
  from eb_sales.eb_member
 where member_type in (1, 2, 5, 6, 7)
;