DELIMITER //

DROP FUNCTION IF EXISTS get_night_allowance //

CREATE FUNCTION get_night_allowance (night_days integer) RETURNS integer
BEGIN

    DECLARE ret_value integer;  /* 戻り値 */
    DECLARE night_allowance integer;  /* 深夜手当 */
    
    IF IFNULL(night_days, 0) = 0 THEN
        SET ret_value = 0;
    ELSE
        /* 深夜手当をマスタテーブルから取得する */
        SELECT value INTO night_allowance FROM mst_config WHERE name = 'night_allowance';
        SET ret_value = CAST(night_days as UNSIGNED) * night_allowance;
    END IF;
    
    RETURN ret_value;
 
END //

DELIMITER ;