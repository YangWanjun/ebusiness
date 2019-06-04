DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_member_orders //

/* ＢＰメンバーの注文書一覧 */
CREATE PROCEDURE sp_partner_member_orders (
	in_partner_id       integer,
    in_date             date
)
BEGIN

DECLARE curr_ym char(6);
DECLARE next_ym char(6);

SET curr_ym = DATE_FORMAT(in_date, '%Y%m');
SET next_ym = DATE_FORMAT(date_add(in_date, interval 1 month), '%Y%m');

select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     , min(c.start_date) as start_date
     , max(c.end_date) as end_date
     , curr_p.id as project_id
     , curr_p.name as project_name
     , if(curr_bp_order.id is null, false, true) as has_curr_order
     , if(next_bp_order.id is null, false, true) as has_next_order
     , if(max(curr_pm.id) is null, false, true) as is_working
     , if(ifnull(max(c.end_date), '9999-12-31') < current_date(), true, false) as is_retired
  from eb_subcontractor s
  left join eb_bp_contract c on c.is_deleted = 0
                            and c.company_id = s.id
  left join eb_member m on m.is_deleted = 0
                       and m.id = c.member_id
  left join eb_projectmember curr_pm on curr_pm.is_deleted = 0
                                    and curr_pm.member_id = m.id
                                    and curr_pm.end_date >= current_date()
  left join eb_project curr_p on curr_p.is_deleted = 0
                             and curr_p.id = curr_pm.project_id
  left join eb_bpmemberorder curr_bp_order on curr_bp_order.is_deleted = 0
									      and curr_bp_order.project_member_id = curr_pm.id
                                          and concat(curr_bp_order.year, curr_bp_order.month) = curr_ym
  left join eb_projectmember next_pm on next_pm.is_deleted = 0
                                    and next_pm.member_id = m.id
                                    and next_pm.end_date >= current_date()
  left join eb_bpmemberorder next_bp_order on next_bp_order.is_deleted = 0
									      and next_bp_order.project_member_id = next_pm.id
                                          and concat(next_bp_order.year, next_bp_order.month) = next_ym
 where s.is_deleted = 0
   and s.id = in_partner_id
 group by m.id, m.first_name, m.last_name
 order by max(c.end_date) desc, concat(m.first_name, ' ', m.last_name) asc
;

END //

DELIMITER ;