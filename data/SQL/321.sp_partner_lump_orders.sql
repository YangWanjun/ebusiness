DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_lump_orders //

/* ＢＰ一括契約一覧 */
CREATE PROCEDURE sp_partner_lump_orders (
	in_partner_id       integer
)
BEGIN

select c.*
     , partner.name as company_name
     , p.name as project_name
	 , p.salesperson_id
     , concat(s.first_name, ' ', s.last_name) as salesperson_name
     , bp_order.id as order_id
     , bp_order.order_no
     , bp_order.is_sent
     , bp_order.filename as order_file
     , bp_order.filename_request as order_request_file
  from eb_bp_lump_contract c
  join eb_subcontractor partner on partner.is_deleted = 0
							   and partner.id = c.company_id
  left join eb_project p on p.is_deleted = 0
                        and p.id = c.project_id
  left join eb_salesperson s on s.is_deleted = 0
                            and s.id = p.salesperson_id
  left join eb_bplumporder bp_order on bp_order.is_deleted = 0
                                   and bp_order.contract_id = c.id
 where c.is_deleted = 0
   and c.company_id = in_partner_id
 order by c.start_date desc
;

END //

DELIMITER ;