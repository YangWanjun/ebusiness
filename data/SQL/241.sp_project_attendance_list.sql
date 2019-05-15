DELIMITER //

DROP PROCEDURE IF EXISTS sp_project_attendance_list //

/* 案件の月ごと勤務リスト */
CREATE PROCEDURE sp_project_attendance_list (
    in_project_id integer           -- 案件ＩＤ
)
BEGIN

select concat(dates.year, dates.month) as id
     , dates.year
     , dates.month
     , concat(dates.year, dates.month) as ym
     , if(count(distinct pm.id) = count(distinct ma.id), true, false) is_inputted
  from eb_projectmember pm
  join v_turnover_dates dates on date_format(pm.start_date, '%Y%m') <= dates.ym 
							 and date_format(pm.end_date, '%Y%m') >= dates.ym 
                             and concat(dates.year, dates.month) <= date_format(current_date(), '%Y%m')
  left join eb_memberattendance ma on ma.is_deleted = 0 
                                  and ma.project_member_id = pm.id 
                                  and ma.year = dates.year 
                                  and ma.month = dates.month
 where pm.is_deleted = 0
   and pm.project_id = in_project_id
 group by dates.year, dates.month
 order by dates.year desc, dates.month desc
;

END //

DELIMITER ;