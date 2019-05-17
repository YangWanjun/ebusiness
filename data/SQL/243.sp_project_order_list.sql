DELIMITER //

DROP PROCEDURE IF EXISTS sp_project_order_list //

/* 案件の注文履歴 */
CREATE PROCEDURE sp_project_order_list (
    in_project_id integer           -- 案件ＩＤ
)
BEGIN

select co.id
     , co.name
     , concat(dates.year, '年', dates.month, '月') as ym
     , dates.year
     , dates.month
     , co.start_date
     , co.end_date
     , co.order_no
     , co.order_date
     , co.contract_type
     , pr.id as request_id
     , pr.request_no
     , co.bank_info_id as bank_account
  from eb_clientorder co
  join eb_clientorder_projects cop on cop.clientorder_id = co.id
  join v_turnover_dates dates on date_format(co.start_date, '%Y%m') <= dates.ym 
							 and date_format(co.end_date, '%Y%m') >= dates.ym
  left join eb_projectrequest pr on pr.project_id = in_project_id
                                and pr.client_order_id = co.id
                                and pr.year = dates.year
                                and pr.month = dates.month
 where co.is_deleted = 0
   and cop.project_id = in_project_id
 order by dates.year desc, dates.month desc
;

END //

DELIMITER ;