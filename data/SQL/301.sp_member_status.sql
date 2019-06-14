DELIMITER //

DROP PROCEDURE IF EXISTS sp_member_status //

/* 社員の稼働状況 */
CREATE PROCEDURE sp_member_status (
)
BEGIN

select member_count
     , working_count
     , (member_count - bp_member_count - individual_count) as employee_count
     , waiting_count
     , round(waiting_count / member_count * 100, 1) as waiting_rate
     , bp_member_count
     , round(bp_member_count / member_count * 100, 1) as bp_member_rate
     , individual_count
     , round(individual_count / member_count * 100, 1) as individual_rate
  from (
		select count(distinct m.id) as member_count
			 , count(distinct pm.member_id) as working_count
			 , count(distinct if(pm.id is null, m.id, null)) as waiting_count
			 , round(count(distinct if(pm.id is null, m.id, null)) / count(distinct m.id) * 100, 1) as waiting_rate  -- 待機率
			 , (select count(distinct s1.member_id) 
				  from eb_bp_contract s1 
				 where s1.is_deleted = 0
				   and ifnull(s1.end_date, '9999-12-31') >= current_date()
			 ) as bp_member_count  -- ＢＰ人数
             , (select count(distinct s2.member_id)
                  from eb_contract s2
				 where s2.is_deleted = 0
                   and s2.status <> '04'
                   and ifnull(ifnull(s2.end_date2, s2.end_date), '9999-12-31') >= current_date()
                   and s2.member_type = 3
             ) as individual_count  -- 個人事業主数
		  from eb_member m
		  left join eb_projectmember pm on pm.is_deleted = 0 
									   and pm.member_id = m.id
									   and pm.start_date <= current_date()
									   and ifnull(pm.end_date, '9999-12-31') >= current_date()
		 where m.is_deleted = 0
		   and m.is_retired = 0
		   and (
			   exists (
				   select 1 
					 from eb_contract c 
					where c.is_deleted = 0 
					  and c.status <> '04'
					  and c.member_id = m.id
					  and ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31') >= current_date()
			   )
			or exists (
				   select 1 
					 from eb_bp_contract c
					where c.is_deleted = 0
					  and c.member_id = m.id
					  and ifnull(c.end_date, '9999-12-31') >= current_date()
			   )
		   )
  ) T
;

END //

DELIMITER ;
