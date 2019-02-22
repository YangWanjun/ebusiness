#!/bin/sh

mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 001.get_division.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 040.get_attendance_total_hours.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 041.get_night_allowance.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 042.get_bp_expenses.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 043.get_overtime_cost.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 044.get_health_insurance.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 045.get_employment_insurance.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 101.v_turnover_monthly.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 102.v_turnover_yearly.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 103.v_turnover_monthly_by_organization.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 104.v_turnover_clients_by_month.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 105.v_turnover_client_by_month.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 201.sp_turnover_monthly_chart.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 202.sp_turnover_monthly_by_division_chart.sql
mysql -h 127.0.0.1 -u root -proot --default-character-set=utf8 eb_sales < 240.sp_project_member_cost.sql