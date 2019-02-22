DELIMITER //

DROP FUNCTION IF EXISTS get_health_insurance //

/* 健康保険を取得する */
CREATE FUNCTION get_health_insurance (
    endowment_insurance integer,
    cost integer,
    allowance integer,
    night_allowance integer,
    overtime_cost integer,
    traffic_cost integer,
    in_member_id integer,
    in_ym char(6)
) RETURNS integer
BEGIN

    DECLARE ret_value integer;                  /* 戻り値 */
    DECLARE health_insurance_rate float;        /* 健康保険率 */
    
    IF (select count(1) from v_member_insurance v where v.member_id = in_member_id and v.ym = in_ym) > 0 THEN
        select health_insurance into ret_value from v_member_insurance v where v.member_id = in_member_id and v.ym = in_ym;
    ELSEIF endowment_insurance = '1' THEN
        /* 深夜手当をマスタテーブルから取得する */
        SELECT value INTO health_insurance_rate FROM mst_config WHERE name = 'health_insurance_rate';
        
        SET ret_value = truncate((cost + allowance + night_allowance + overtime_cost + traffic_cost) * health_insurance_rate, 0);
    ELSE
        SET ret_value = 0;
    END IF;
    
    RETURN ret_value;
 
END //

DELIMITER ;