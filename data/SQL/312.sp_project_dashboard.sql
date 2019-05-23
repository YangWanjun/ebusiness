DELIMITER //

DROP PROCEDURE IF EXISTS sp_project_dashboard //

/* 案件の月ごと勤務リスト */
CREATE PROCEDURE sp_project_dashboard (
    in_member_id integer           -- 社員ＩＤ
)
BEGIN

select p.id
     , p.name
     , pm.start_date
     , pm.end_date
     , (select name from eb_section where id = get_division_new(p.department_id)) as division_name
  from eb_project p
  join eb_projectmember pm on pm.is_deleted = 0
                          and pm.project_id = p.id
 where p.is_deleted = 0
   and pm.member_id = in_member_id
 order by pm.start_date, pm.end_date
;

END //

DELIMITER ;