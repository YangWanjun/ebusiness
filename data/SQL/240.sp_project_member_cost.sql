DELIMITER //

DROP PROCEDURE IF EXISTS sp_project_member_cost //

/* アサインした社員のコスト */
CREATE PROCEDURE sp_project_member_cost (
    in_member_id integer,           -- 社員ＩＤ
    in_project_member_id integer,   -- アサインＩＤ
    in_year char(4),                -- 対象年
    in_month char(2),               -- 対象月
    in_total_hours decimal(5,2),    -- 出金時間
    in_allowance integer,           -- 手当
    in_night_days integer,          -- 深夜日数
    in_traffic_cost integer,        -- 交通費
    in_expenses integer             -- 経費
)
BEGIN

DECLARE tmp_cost integer;
DECLARE tmp_member_type tinyint;
DECLARE tmp_is_hourly_pay boolean;
DECLARE tmp_salary integer;
DECLARE tmp_allowance_other integer;
DECLARE tmp_total_hours decimal(5,2);
DECLARE tmp_night_allowance integer;
DECLARE tmp_overtime_cost integer;
DECLARE tmp_traffic_cost integer;
DECLARE tmp_expenses integer;
DECLARE tmp_employment_insurance integer;
DECLARE tmp_health_insurance integer;
DECLARE tmp_endowment_insurance char(1);

select get_attendance_total_hours(in_total_hours) into tmp_total_hours;
select get_night_allowance(in_night_days) into tmp_night_allowance;
-- 契約から給料を取得
select t.member_type
     , t.is_hourly_pay
     , sum(t.salary)
     , sum(t.allowance_other)
     , sum(t.overtime_cost)
     , sum(t.traffic_cost)
     , sum(t.expenses)
  into tmp_member_type
     , tmp_is_hourly_pay
     , tmp_salary
     , tmp_allowance_other
     , tmp_overtime_cost
     , tmp_traffic_cost
     , tmp_expenses
  from (
        select c.member_id
             , c.member_type
             , c.is_hourly_pay
             , 0 AS is_fixed_cost
             , CASE c.member_type
                   WHEN 1 THEN truncate((c.allowance_base + 
                                      c.allowance_base_other + 
                                      c.allowance_work + 
                                      c.allowance_director + 
                                      c.allowance_position + 
                                      c.allowance_diligence +
                                      c.allowance_security +
                                      c.allowance_qualification +
                                      c.allowance_other) * 14 / 12, 0)
                   ELSE truncate((c.allowance_base + 
                               c.allowance_base_other + 
                               c.allowance_work + 
                               c.allowance_director + 
                               c.allowance_position + 
                               c.allowance_diligence +
                               c.allowance_security +
                               c.allowance_qualification +
                               c.allowance_other), 0)
               END AS salary
             , c.allowance_time_min 
             , c.allowance_time_max 
             , c.allowance_absenteeism 
             , c.allowance_overtime
             , c.allowance_other
             , c.endowment_insurance
             , in_traffic_cost as traffic_cost
             , get_bp_expenses(in_project_member_id, in_year, in_month) as expenses
             , get_overtime_cost(tmp_total_hours, IFNULL(bp_h.allowance_time_min, c.allowance_time_min), c.allowance_time_max, c.is_hourly_pay, 0, p.is_reserve, c.allowance_absenteeism, c.allowance_overtime) as overtime_cost
          FROM eb_contract c
          join eb_projectmember pm on c.member_id = pm.member_id and pm.id = in_project_member_id
          join eb_project p on p.id = pm.project_id
          left join eb_bpmemberorder bp_o on bp_o.project_member_id = in_project_member_id and bp_o.is_deleted = 0 and bp_o.year = in_year and bp_o.month = in_month
          left join eb_bpmemberorderheading bp_h on bp_h.bp_order_id = bp_o.id
         WHERE c.status <> '04'
           and c.is_deleted = 0
           and c.member_id = in_member_id
           and (SELECT MAX(c1.contract_no)
                  FROM eb_contract c1
                 WHERE c1.start_date = c.start_date
                   AND c1.member_id = c.member_id
                   AND c1.is_deleted = 0
                   AND c1.status <> '04'
           ) = c.contract_no
           and extract(year_month from(c.start_date)) <= concat(in_year, in_month)
           and (extract(year_month from(CASE WHEN (c.end_date2 IS NOT NULL) THEN c.end_date2 ELSE c.end_date END)) >= concat(in_year, in_month) 
            or (CASE WHEN (c.end_date2 IS NOT NULL) THEN c.end_date2 ELSE c.end_date END) is null
           )
        UNION ALL
        SELECT c.member_id
             , 4 as member_type
             , c.is_hourly_pay
             , c.is_fixed_cost
             , IF(c.is_hourly_pay or c.is_fixed_cost, c.allowance_base, c.allowance_base + c.allowance_other) AS salary
             , c.allowance_time_min 
             , c.allowance_time_max 
             , c.allowance_absenteeism 
             , c.allowance_overtime
             , c.allowance_other
             , '0' as endowment_insurance
			 , 0 as traffic_cost
             , IFNULL(in_expenses, 0) as expenses
             , get_overtime_cost(tmp_total_hours, IFNULL(bp_h.allowance_time_min, c.allowance_time_min), c.allowance_time_max, c.is_hourly_pay, c.is_fixed_cost, p.is_reserve, c.allowance_absenteeism, c.allowance_overtime) as overtime_cost
          from eb_bp_contract c
          join eb_projectmember pm on c.member_id = pm.member_id and pm.id = in_project_member_id
          join eb_project p on p.id = pm.project_id
          left join eb_bpmemberorder bp_o on bp_o.project_member_id = in_project_member_id and bp_o.is_deleted = 0 and bp_o.year = in_year and bp_o.month = in_month
          left join eb_bpmemberorderheading bp_h on bp_h.bp_order_id = bp_o.id
         WHERE c.status <> '04'
           AND c.is_deleted = 0
           and c.member_id = in_member_id
           and extract(year_month from(c.start_date)) <= concat(in_year, in_month)
           and (extract(year_month from(c.end_date)) >= concat(in_year, in_month) or c.end_date is null)
  ) t
 group by t.member_id
;

IF tmp_is_hourly_pay is true THEN
    set tmp_salary = tmp_salary * in_total_hours + tmp_allowance_other;
END IF;
IF tmp_member_type <> 4 THEN
    select get_health_insurance(tmp_endowment_insurance, tmp_salary, in_allowance, tmp_night_allowance, tmp_overtime_cost, tmp_traffic_cost, in_member_id, concat(in_year, in_month)) into tmp_health_insurance;
ELSE
    set tmp_health_insurance = 0;
END IF;

select get_employment_insurance(tmp_member_type, tmp_salary, in_allowance, tmp_night_allowance, tmp_overtime_cost, tmp_traffic_cost) into tmp_employment_insurance;
SET tmp_cost = tmp_salary + in_allowance + tmp_night_allowance + tmp_overtime_cost + tmp_traffic_cost + tmp_expenses + tmp_employment_insurance + tmp_health_insurance;

select tmp_salary as `salary`
     , tmp_overtime_cost as `overtime_cost`
     , tmp_cost as `cost`
;

END //

DELIMITER ;