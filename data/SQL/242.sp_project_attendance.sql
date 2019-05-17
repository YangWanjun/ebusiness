DELIMITER //

DROP PROCEDURE IF EXISTS sp_project_attendance //

/* アサインした社員のコスト */
CREATE PROCEDURE sp_project_attendance (
    in_project_id integer,           -- 社員ＩＤ
    in_year char(4),                 -- 対象年
    in_month char(2)                 -- 対象月
)
BEGIN

select dates.year
     , dates.month
     , concat(dates.year, dates.month) as ym
     , ma.id
     , pm.id as project_member
     , concat(m.first_name, ' ', m.last_name) as member_name
     , ma.total_hours
     , ma.total_hours_bp
     , ma.extra_hours
     , ma.price
     , ma.comment
     , pm.price as base_price
     , pm.min_hours
     , pm.max_hours
     , pm.minus_per_hour
     , pm.plus_per_hour
  from eb_projectmember pm
  join v_turnover_dates dates on date_format(pm.start_date, '%Y%m') <= dates.ym and date_format(pm.end_date, '%Y%m') >= dates.ym
  join eb_member m on m.id = pm.member_id
  left join eb_memberattendance ma on ma.is_deleted = 0 and ma.project_member_id = pm.id and ma.year = dates.year and ma.month = dates.month
 where pm.is_deleted = 0
   and pm.project_id = in_project_id
   and dates.year = in_year
   and dates.month = in_month
 order by dates.year desc, dates.month desc
;

END //

DELIMITER ;