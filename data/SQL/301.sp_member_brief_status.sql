DELIMITER //

DROP PROCEDURE IF EXISTS sp_member_brief_status //

/* 社員の稼働状況 */
CREATE PROCEDURE sp_member_brief_status (
)
BEGIN

DECLARE curr_month char(6);
DECLARE prev_month char(6);
DECLARE next_month char(6);

SET curr_month = DATE_FORMAT(current_date(), '%Y%m');
SET prev_month = DATE_FORMAT(date_add(current_date(), interval -1 month), '%Y%m');
SET next_month = DATE_FORMAT(date_add(current_date(), interval 1 month), '%Y%m');

select 'curr' as category
     , count(distinct m.id) as member_count
     , count(distinct pm.member_id) as working_count
     , count(distinct if(pm.id is null, m.id, null)) as waiting_count
  from eb_member m
  left join eb_projectmember pm on pm.is_deleted = 0 
							   and pm.member_id = m.id
							   and DATE_FORMAT(pm.start_date, '%Y%m') <= curr_month
                               and DATE_FORMAT(ifnull(pm.end_date, '9999-12-31'), '%Y%m') >= curr_month
 where m.is_deleted = 0
   and m.is_retired = 0
   and (
       exists (
		   select 1 
             from eb_contract c 
            where c.is_deleted = 0 
              and c.status <> '04'
			  and c.member_id = m.id
              and DATE_FORMAT(ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31'), '%Y%m') >= curr_month
       )
    or exists (
           select 1 
             from eb_bp_contract c
            where c.is_deleted = 0
              and c.member_id = m.id
              and DATE_FORMAT(ifnull(c.end_date, '9999-12-31'), '%Y%m') >= curr_month
       )
   )
UNION ALL
select 'prev' as category
     , count(distinct m.id) as member_count
     , count(distinct pm.member_id) as working_count
     , count(distinct if(pm.id is null, m.id, null)) as waiting_count
  from eb_member m
  left join eb_projectmember pm on pm.is_deleted = 0 
							   and pm.member_id = m.id
							   and DATE_FORMAT(pm.start_date, '%Y%m') <= prev_month
                               and DATE_FORMAT(ifnull(pm.end_date, '9999-12-31'), '%Y%m') >= prev_month
 where m.is_deleted = 0
   and m.is_retired = 0
   and (
       exists (
		   select 1 
             from eb_contract c 
            where c.is_deleted = 0 
              and c.status <> '04'
			  and c.member_id = m.id
              and DATE_FORMAT(ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31'), '%Y%m') >= prev_month
       )
    or exists (
           select 1 
             from eb_bp_contract c
            where c.is_deleted = 0
              and c.member_id = m.id
              and DATE_FORMAT(ifnull(c.end_date, '9999-12-31'), '%Y%m') >= prev_month
       )
   )
UNION ALL
select 'next' as category
     , count(distinct m.id) as member_count
     , count(distinct pm.member_id) as working_count
     , count(distinct if(pm.id is null, m.id, null)) as waiting_count
  from eb_member m
  left join eb_projectmember pm on pm.is_deleted = 0 
							   and pm.member_id = m.id
							   and DATE_FORMAT(pm.start_date, '%Y%m') <= next_month
                               and DATE_FORMAT(ifnull(pm.end_date, '9999-12-31'), '%Y%m') >= next_month
 where m.is_deleted = 0
   and m.is_retired = 0
   and (
       exists (
		   select 1 
             from eb_contract c 
            where c.is_deleted = 0 
              and c.status <> '04'
			  and c.member_id = m.id
              and DATE_FORMAT(ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31'), '%Y%m') >= next_month
       )
    or exists (
           select 1 
             from eb_bp_contract c
            where c.is_deleted = 0
              and c.member_id = m.id
              and DATE_FORMAT(ifnull(c.end_date, '9999-12-31'), '%Y%m') >= next_month
       )
   )

;

END //

DELIMITER ;
