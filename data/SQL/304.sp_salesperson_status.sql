DELIMITER //

DROP PROCEDURE IF EXISTS sp_salesperson_status //

/* 営業員の担当状況 */
CREATE PROCEDURE sp_salesperson_status (
)
BEGIN

select id
     , name
     , member_count
     , working_count
     , (member_count - working_count) as waiting_count
     , curr_release_count
     , next_release_count
     , next_2_release_count
  from (
		select s.id
			 , concat(s.first_name, ' ', s.last_name) as name
			 , count(distinct msp.member_id) as member_count
			 , count(distinct pm.member_id) as working_count
			 , count(distinct if(release_pm.end_date <= LAST_DAY(current_date()), release_pm.member_id, null)) as curr_release_count
			 , count(distinct if(release_pm.end_date > LAST_DAY(current_date()) and release_pm.end_date <= LAST_DAY(date_add(current_date(), interval 1 month)), release_pm.member_id, null)
             ) as next_release_count
			 , count(distinct if(release_pm.end_date > LAST_DAY(date_add(current_date(), interval 1 month)) and release_pm.end_date <= LAST_DAY(date_add(current_date(), interval 2 month)), release_pm.member_id, null)
             ) as next_2_release_count
		  from eb_salesperson s
		  left join eb_membersalespersonperiod msp on msp.is_deleted = 0
												  and msp.salesperson_id = s.id
												  and ifnull(msp.end_date, '9999-12-31') >= current_date()
		  left join eb_projectmember pm on pm.is_deleted = 0
									   and pm.member_id = msp.member_id
									   and pm.start_date <= current_date()
									   and pm.end_date >= current_date()
		  left join eb_projectmember release_pm on release_pm.is_deleted = 0
											   and release_pm.member_id = msp.member_id
											   and release_pm.start_date <= current_date()
											   and release_pm.end_date >= current_date()
											   and not exists (
													   select 1
														 from eb_projectmember s1 
														where s1.member_id = msp.member_id
														  and s1.is_deleted = 0
														  and s1.status = 2
														  and s1.start_date between pm.end_date and date_add(pm.end_date, interval 1 month)
												   )
		 where s.is_deleted = 0
		   and msp.salesperson_id is not null
		 group by s.id
  ) T
 order by T.name
;

END //

DELIMITER ;
