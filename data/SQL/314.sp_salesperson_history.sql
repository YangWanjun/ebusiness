DELIMITER //

DROP PROCEDURE IF EXISTS sp_salesperson_history //

/* 社員の営業担当履歴 */
CREATE PROCEDURE sp_salesperson_history (
    in_member_id integer           -- 社員ＩＤ
)
BEGIN

select msp.id
     , s.id as salesperson_id
     , concat(s.first_name, ' ', s.last_name) as salesperson_name
     , msp.start_date
     , msp.end_date
  from eb_membersalespersonperiod msp
  left join eb_salesperson s on s.id = msp.salesperson_id
 where msp.is_deleted = 0
   and msp.member_id = in_member_id
 order by msp.start_date
;

END //

DELIMITER ;