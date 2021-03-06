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
     , (
         select concat('[', group_concat(concat('{"value": ', s1.id, ', "display_name":"', s1.name, '"}') separator ','), ']')
           from eb_project s1
           join eb_clientorder_projects s2 on s2.project_id = s1.id
		  where s2.clientorder_id = co.id
     ) as projects
     , a.uuid
     , a.name as filename
  from eb_clientorder co
  join eb_clientorder_projects cop on cop.clientorder_id = co.id
  join v_turnover_dates dates on date_format(co.start_date, '%Y%m') <= dates.ym 
							 and date_format(co.end_date, '%Y%m') >= dates.ym
  left join django_content_type ct on ct.app_label = 'project' and ct.model = 'projectrequest'
  left join eb_projectrequest pr on pr.project_id = in_project_id
                                and pr.client_order_id = co.id
                                and pr.year = dates.year
                                and pr.month = dates.month
  left join mst_attachment a on a.content_type_id = ct.id and a.object_id = pr.id
 where co.is_deleted = 0
   and cop.project_id = in_project_id
 order by dates.year desc, dates.month desc
;

END //

DELIMITER ;