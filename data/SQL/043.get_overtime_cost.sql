DELIMITER //

DROP FUNCTION IF EXISTS get_overtime_cost //

/* 残業時間を取得する */
CREATE FUNCTION get_overtime_cost (raw_hours DECIMAL(5, 2),
                              min_hours DECIMAL(5, 2),
                              max_hours DECIMAL(5, 2),
                              is_hourly_pay boolean,
                              is_fixed_cost boolean,
                              is_reserve boolean,
                              minus_per_hour integer,
                              plus_per_hour integer) 
RETURNS integer
BEGIN

    DECLARE ret_value integer;          /* 戻り値 */
    DECLARE overtime DECIMAL(5, 2);     /* 深夜手当 */
    
    SET overtime = get_overtime(raw_hours, min_hours, max_hours, is_hourly_pay, is_fixed_cost, is_reserve);
    
    IF overtime > 0 THEN
        SET ret_value = overtime * plus_per_hour;
    ELSEIF overtime = 0 THEN
        SET ret_value = 0;
    ELSE
        SET ret_value = overtime * minus_per_hour;
    END IF;
    
    RETURN IFNULL(ret_value, 0);
 
END //

DELIMITER ;