DELIMITER //

DROP PROCEDURE IF EXISTS sp_member_working_status //

/* 社員の稼働状況 */
CREATE PROCEDURE sp_member_working_status (
)
BEGIN

select dates.ym
     , (select count(distinct m.id)
		  from eb_member m
		  join eb_projectmember pm on m.id = pm.member_id
		  join eb_project p on p.id = pm.project_id
		 where DATE_FORMAT(pm.start_date, '%Y%m') <= dates.ym
		   and DATE_FORMAT(pm.end_date, '%Y%m') >= dates.ym
		   and m.is_deleted = 0
		   and pm.is_deleted = 0
		   and pm.status = 2
		   and p.is_reserve = 0
		   and exists(
               select 1 
                 from eb_membersectionperiod msp 
				where msp.member_id = m.id 
                and msp.is_deleted=0
		   )
		   and (m.is_retired = 0 or (m.is_retired = 1 and DATE_FORMAT(m.retired_date, '%Y%m') >= dates.ym))
     ) as working_count
	 , (select count(distinct m.id)
		  from eb_member m
		 where m.is_deleted = 0
		   and (m.is_retired = 0 or (m.is_retired = 1 and DATE_FORMAT(m.retired_date, '%Y%m') > dates.ym))
		   and m.is_on_sales = 1
		   and DATE_FORMAT(m.join_date, '%Y%m') <= dates.ym
		   and exists(
               select 1 
                 from eb_membersectionperiod msp 
                 join eb_section s on s.id = msp.section_id
				where msp.member_id = m.id 
                  and msp.is_deleted=0 
                  and s.is_on_sales = 1
		   )
		   and not exists(
               select 1
				 from eb_projectmember pm 
				where pm.member_id = m.id
				  and DATE_FORMAT(pm.start_date, '%Y%m') <= dates.ym 
                  and DATE_FORMAT(pm.end_date, '%Y%m') >= dates.ym 
                  and pm.is_deleted = 0
		   )
	 ) as waiting_count
  from v_turnover_dates dates
 where concat(dates.year , '-', dates.month, '-01') >= date_add(current_date(), interval -1 year)

;

END //

DELIMITER ;
