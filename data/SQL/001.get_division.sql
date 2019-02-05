DELIMITER //

DROP FUNCTION IF EXISTS get_division //

/* 部署の所属している事業部を取得 */
CREATE FUNCTION get_division (
    in_organization_id integer
)
RETURNS INTEGER
BEGIN

    DECLARE ret_value integer;            /* 戻り値 */
    DECLARE tmp_org_type char(2);               /* 組織類別 */
    
    SELECT org_type into tmp_org_type FROM eb_section where id = in_organization_id and is_deleted = 0;
    
    IF tmp_org_type = '01' THEN
        -- 事業部の場合
        SET ret_value = in_organization_id;
    ELSEIF tmp_org_type = '02' THEN
        -- 部署の場合
        SELECT s1.id into ret_value 
          FROM eb_section s1
          join eb_section s2 on s2.is_deleted = 0 and s1.parent_id = s2.id
		 where s1.is_deleted = 0
           and s1.id = in_organization_id;
	ELSEIF tmp_org_type = '03' THEN
        -- 課の場合
        SELECT s2.id into ret_value 
          FROM eb_section s1
          JOIN eb_section s2 on s2.is_deleted = 0 and s1.parent_id = s2.id
          JOIN eb_section s3 on s3.is_deleted = 0 and s2.parent_id = s3.id
		 where s1.is_deleted = 0
           and s1.id = in_organization_id;
	ELSE
        SET ret_value = in_organization_id;
    END IF;
    
    RETURN ret_value;
 
END //

DELIMITER ;