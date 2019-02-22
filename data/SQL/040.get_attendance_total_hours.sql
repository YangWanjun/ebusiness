DELIMITER //

DROP FUNCTION IF EXISTS get_attendance_total_hours //

CREATE FUNCTION get_attendance_total_hours (total_hours decimal(5, 2)) RETURNS DECIMAL(5, 2)
BEGIN

    DECLARE ret_value DECIMAL(5, 2);    /* 戻り値 */
    DECLARE attendance_type CHAR(1);    /* 出勤区分 */
    DECLARE float_part float;
    DECLARE int_part float;

    IF ifnull(total_hours, 0) = 0 THEN 
        /* 時間が設定してない場合、0を返す */
        SET ret_value = 0;
    ELSEIF MOD(total_hours, 1) = 0 THEN 
        /* 整数の場合、そのまま返す */
        SET ret_value = total_hours;
    ELSE
        /* 出勤区分をマスタテーブルから取得する */
        SELECT value INTO attendance_type FROM mst_config WHERE name = 'bp_attendance_type';
        SET float_part = MOD(total_hours, 1);
        SET int_part = total_hours - float_part;
        
        IF attendance_type = '1' THEN
            /* １５分ごと */
            IF 0 <= float_part and float_part < 0.25 THEN 
                SET ret_value = int_part;
            ELSEIF 0.25 <= float_part and float_part < 0.5 THEN 
                SET ret_value = int_part + 0.25;
            ELSEIF 0.5 <= float_part and float_part < 0.75 THEN 
                SET ret_value = int_part + 0.5;
            ELSE 
                SET ret_value = int_part + 0.75;
            END IF;
        ELSEIF attendance_type = '2' THEN
            /* ３０分ごと */
            IF 0 <= float_part and float_part < 0.5 THEN 
                SET ret_value = int_part;
            ELSE 
                SET ret_value = int_part + 0.5;
            END IF;
        ELSE
            /* １時間ごと */
            SET ret_value = int_part;
        END IF;
        
        
    END IF;
    
    RETURN ret_value;

END //

DELIMITER ;