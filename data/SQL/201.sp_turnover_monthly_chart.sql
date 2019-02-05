delimiter //

DROP PROCEDURE IF EXISTS sp_turnover_monthly_chart //

/* 最近一年間の月別売上
 */
CREATE PROCEDURE sp_turnover_monthly_chart(
)
BEGIN

select year
     , month
     , turnover_amount
  from v_turnover_monthly
 where concat(year, month) >= date_format(date_add(current_date(), interval -1 year), '%Y%m')
 order by year, month
;

END