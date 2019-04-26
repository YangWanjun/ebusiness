/* ＢＰメンバーの諸経費を取得する。
 *
 */

DELIMITER //

DROP FUNCTION IF EXISTS get_bp_expenses_new //

/* ＢＰメンバーの諸経費を取得する */
CREATE FUNCTION get_bp_expenses_new (
    in_project_member_id integer,
    in_year char(4),
    in_month char(2)
) 
RETURNS integer
BEGIN

    DECLARE ret_value integer;          /* 戻り値 */
    
    select sum(sme.price) into ret_value
      from eb_subcontractormemberexpenses sme
     where sme.project_member_id = in_project_member_id
       and sme.year = in_year 
       and sme.month = in_month
       and sme.is_deleted = 0;
    
    RETURN IFNULL(ret_value, 0);
 
END //

DELIMITER ;