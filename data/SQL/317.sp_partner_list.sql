DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_list //

/* お客様一覧 */
CREATE PROCEDURE sp_partner_list (
)
BEGIN

select s.id
     , s.name
     , s.president
     , concat(s.address1, s.address2) as address
     , s.tel
     , count(distinct c.id) as member_count
     , if(count(distinct c.id) = 0, true, false) as is_retired
  from eb_subcontractor s
  left join eb_bp_contract c on c.is_deleted = 0
                            and c.company_id = s.id
                            and (c.end_date >= current_date() or c.end_date is null)
 where s.is_deleted = 0
 group by s.id, s.name, s.president, s.address1, s.address2, s.tel
 order by s.name
;

END //

DELIMITER ;