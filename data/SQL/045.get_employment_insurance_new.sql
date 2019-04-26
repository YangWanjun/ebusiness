DELIMITER //

DROP FUNCTION IF EXISTS get_employment_insurance_new //

/* 雇用保険を取得する */
CREATE FUNCTION get_employment_insurance_new (
    member_type integer,
    cost integer,
    allowance integer,
    night_allowance integer,
    overtime_cost integer,
    traffic_cost integer
) RETURNS integer
BEGIN

    DECLARE ret_value float;            /* 戻り値 */
    DECLARE employment_insurance_rate float;    /* 雇用保険率 */
    
    IF member_type = 1 or member_type = 2 or member_type = 7 THEN
        /* 深夜手当をマスタテーブルから取得する */
        SELECT value INTO employment_insurance_rate FROM mst_config WHERE name = 'employment_insurance_rate';
        
        SET ret_value = (cost + allowance + night_allowance + overtime_cost + traffic_cost) * employment_insurance_rate;
    ELSE
        SET ret_value = 0;
    END IF;
    
    RETURN truncate(ret_value, 0);
 
END //

DELIMITER ;