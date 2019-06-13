DELIMITER //

DROP PROCEDURE IF EXISTS sp_member_working_status //

/* 社員の稼働状況 */
CREATE PROCEDURE sp_member_working_status (
)
BEGIN

select concat(dates.month, '月') as ym
     , (select count(distinct m.id)
		  from eb_member m
		  join eb_projectmember pm on pm.is_deleted = 0 
                                  and m.id = pm.member_id 
                                  and pm.status = 2
		  join eb_project p on p.is_deleted = 0 and p.id = pm.project_id and p.is_reserve = 0
		 where m.is_deleted = 0
		   and DATE_FORMAT(pm.start_date, '%Y%m') <= dates.ym
		   and DATE_FORMAT(pm.end_date, '%Y%m') >= dates.ym
		   and exists (
			   select 1 
				 from eb_contract c 
				where c.is_deleted = 0 
				  and c.status <> '04'
				  and c.member_id = m.id
                  and DATE_FORMAT(c.start_date, '%Y%m') <= dates.ym 
				  and DATE_FORMAT(ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31'), '%Y%m') >= dates.ym
           )
     ) as working_count
	 , (select count(distinct m.id)
		  from eb_member m
		 where m.is_deleted = 0
		   and not exists(
               select 1
				 from eb_projectmember pm 
				where pm.is_deleted = 0
				  and pm.member_id = m.id
				  and DATE_FORMAT(pm.start_date, '%Y%m') <= dates.ym 
                  and DATE_FORMAT(pm.end_date, '%Y%m') >= dates.ym 
		   )
		   and exists (
			   select 1 
				 from eb_contract c 
				where c.is_deleted = 0 
				  and c.status <> '04'
				  and c.member_id = m.id
                  and DATE_FORMAT(c.start_date, '%Y%m') <= dates.ym 
				  and DATE_FORMAT(ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31'), '%Y%m') >= dates.ym
           )
	 ) as waiting_count
  from v_turnover_dates dates
 where concat(dates.year , '-', dates.month, '-01') >= date_add(current_date(), interval -1 year)

;

END //

DELIMITER ;
