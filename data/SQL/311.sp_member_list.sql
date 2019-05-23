DELIMITER //

DROP PROCEDURE IF EXISTS sp_member_list //

/* 案件の月ごと勤務リスト */
CREATE PROCEDURE sp_member_list (
    in_base_date date           -- 案件ＩＤ
)
BEGIN

select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     , division.id as division_id
     , division.name as division_name
     , department.id as department_id
     , department.name as department_name
     , section.id as section_id
     , section.name as section_name
     , partner.id as partner_id
     , partner.name as partner_name
     , s.id as salesperson_id
     , concat(s.first_name, ' ', s.last_name) as salesperson_name
     , if(pm.id is null, false, true) as is_working
     , pm.end_date as release_date
     , sor.name as salesoff_reason_name
     , case
           when c.id is null and bp_c.id is null then true
           else false
       end as is_retired
  from eb_member m
  join eb_membersectionperiod msp1 on msp1.is_deleted = 0
                                   and msp1.member_id = m.id
                                   and msp1.start_date <= in_base_date
                                   and (msp1.end_date >= in_base_date or msp1.end_date is null)
  left join eb_section division on division.id = msp1.division_id
  left join eb_section department on department.id = msp1.section_id
  left join eb_section section on section.id = msp1.subsection_id
  left join eb_bp_contract bp_c on bp_c.is_deleted = 0
                               and bp_c.member_id = m.id 
                               and bp_c.start_date <= in_base_date
                               and (bp_c.end_date >= in_base_date or bp_c.end_date is null)
  left join eb_subcontractor partner on partner.id = bp_c.company_id
  left join eb_membersalespersonperiod msp2 on msp2.is_deleted = 0
                                           and msp2.member_id = m.id
                                           and msp2.start_date <= in_base_date
                                           and (msp2.end_date >= in_base_date or msp2.end_date is null)
  left join eb_salesperson s on s.id = msp2.salesperson_id
  left join eb_projectmember pm on pm.is_deleted = 0
                               and pm.member_id = m.id
                               and pm.end_date >= in_base_date
                               and pm.id = (
                                   select id
                                     from eb_projectmember s1 
                                    where s1.is_deleted = 0 
                                      and s1.member_id = m.id 
                                      and s1.end_date >= in_base_date
                                    order by s1.end_date desc
                                    limit 1
                               )
  left join eb_membersalesoffperiod msp3 on msp3.is_deleted = 0
                                        and msp3.member_id = m.id
                                        and msp3.start_date <= in_base_date
                                        and (msp3.end_date >= in_base_date or msp3.end_date is null)
  left join mst_salesofreason sor on sor.id = msp3.sales_off_reason_id
  left join eb_contract c on c.is_deleted = 0
                         and c.member_id = m.id
                         and ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31') >= in_base_date
                         and c.id = (
                             select id
                               from eb_contract s1
                              where s1.is_deleted = 0
                                and s1.member_id = m.id
                                and ifnull(ifnull(s1.end_date2, s1.end_date), '9999-12-31') >= in_base_date
                              order by s1.start_date desc, s1.contract_no desc
                              limit 1
                         )
 where m.is_deleted = 0
 order by concat(m.first_name, ' ', m.last_name)
;

END //

DELIMITER ;