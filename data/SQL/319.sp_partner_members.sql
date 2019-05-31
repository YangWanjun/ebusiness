DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_members //

/* 協力会社の作業メンバー一覧 */
CREATE PROCEDURE sp_partner_members (
	in_partner_id       integer
)
BEGIN

select m.*
     , concat(m.first_name, ' ', m.last_name) as name
     , division.id as division_id
     , division.name as division_name
     , department.id as department_id
     , department.name as department_name
     , section.id as section_id
     , section.name as section_name
     , min(c.start_date) as start_date
     , max(c.end_date) as end_date
     , if(pm.id is null, false, true) as is_working
     , if(ifnull(max(c.end_date), '9999-12-31') < current_date(), true, false) as is_contract_retired
  from eb_subcontractor s
  left join eb_bp_contract c on c.is_deleted = 0
                            and c.company_id = s.id
  left join eb_member m on m.is_deleted = 0
                       and m.id = c.member_id
  left join eb_membersectionperiod msp1 on msp1.is_deleted = 0
                                       and msp1.member_id = m.id
                                       and msp1.start_date <= current_date()
                                       and (msp1.end_date >= current_date() or msp1.end_date is null)
  left join eb_section division on division.id = msp1.division_id
  left join eb_section department on department.id = msp1.section_id
  left join eb_section section on section.id = msp1.subsection_id
  left join eb_projectmember pm on pm.is_deleted = 0
                               and pm.member_id = m.id
                               and pm.end_date >= current_date()
                               and pm.id = (
                                   select id
                                     from eb_projectmember s1 
                                    where s1.is_deleted = 0 
                                      and s1.member_id = m.id 
                                      and s1.end_date >= current_date()
                                    order by s1.end_date desc
                                    limit 1
                               )
 where s.is_deleted = 0
   and s.id = in_partner_id
 group by m.id, m.first_name, m.last_name
 order by concat(m.first_name, ' ', m.last_name)
;

END //

DELIMITER ;