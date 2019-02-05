delimiter //

DROP PROCEDURE IF EXISTS sp_turnover_monthly_by_division_chart //

/* 最近一年間の事業部別、かつ月別売上
 */
CREATE PROCEDURE sp_turnover_monthly_by_division_chart(
)
BEGIN

select v.year
     , v.month
     , v.division_id
     , s.name as division_name
     , sum(v.turnover_amount) as turnover_amount
  from v_turnover_monthly_by_organization v
  join eb_section s on s.id = v.division_id
  /*right join (select date_format(m1, '%Y') as year
                   , date_format(m1, '%m') as month
                from (
                      select (current_date() - INTERVAL 365 DAY) + INTERVAL m MONTH as m1
                        from (select @rownum:=@rownum+1 as m 
                                from (select 1 union select 2 union select 3 union select 4) t1
                                   , (select 1 union select 2 union select 3 union select 4) t2
                                   , (select @rownum:=-1) t0
                        ) d1
                ) d2 
               where m1 < current_date()
			   order by m1
  ) T on T.year = v.year and T.month = v.month*/
 where concat(v.year, v.month) >= date_format(date_add(current_date(), interval -1 year), '%Y%m')
 group by division_id, v.year, v.month
 order by v.year, v.month
;

END