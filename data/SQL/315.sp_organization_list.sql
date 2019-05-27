DELIMITER //

DROP PROCEDURE IF EXISTS sp_organization_list //

/* 部署リスト */
CREATE PROCEDURE sp_organization_list (
)
BEGIN
select s.id
     , s.name
     , count(distinct msp1.id) as member_count
     , group_concat(distinct concat(m.first_name, ' ', m.last_name, if(ps.position in (5.0, 7.0), '(担当)', '')) separator ',') as leaders
     , s.org_type
     , s.parent_id as parent
  from eb_section s
  left join eb_membersectionperiod msp1 on msp1.is_deleted = 0
									   and (msp1.division_id = s.id or msp1.section_id = s.id or msp1.subsection_id = s.id)
                                       and msp1.start_date <= current_date()
                                       and (msp1.end_date >= current_date() or msp1.end_date is null)
  left join eb_positionship ps on ps.is_deleted = 0
                              and ps.section_id = s.id
  left join eb_member m on m.id = ps.member_id
 where s.is_deleted = 0
   and s.is_on_sales = true
 group by s.id, s.name, s.org_type, s.parent_id
 order by s.name
;

END //

DELIMITER ;