DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_contracts_by_month //

/* 協力会社の指定年月の事業部別支払通知書及び請求書の作成状況 */
CREATE PROCEDURE sp_partner_contracts_by_month (
	in_partner_id       integer,
    in_year             char(4),
    in_month            char(2)
)
BEGIN

select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     ,  case
           when division.id is not null then division.id
           when department.id is not null then department.id
           when section.id is not null then section.id
           else null
	   end as division_id
     , case
           when division.id is not null then division.name
           when department.id is not null then department.name
           when section.id is not null then section.name
           else null
	   end as division_name
     , p.id as project_id
     , p.name as project_name
	 , r.id as request_id
     , r.request_no
     , r.pay_notify_no
     , r.filename_pdf
     , r.pay_notify_filename_pdf
     , r.is_sent
     , null as parent
  from eb_subcontractor s
  join eb_bp_contract c on c.is_deleted = 0
					   and c.company_id = s.id
					   and DATE_FORMAT(c.start_date, '%Y%m') <= concat(in_year, in_month)
					   and (c.end_date is null or DATE_FORMAT(c.end_date, '%Y%m') >= concat(in_year, in_month))
  join eb_member m on m.is_deleted = 0
                  and m.id = c.member_id
  left join eb_membersectionperiod msp1 on msp1.is_deleted = 0
                                       and msp1.member_id = m.id
                                       and DATE_FORMAT(msp1.start_date, '%Y%m') <= concat(in_year, in_month)
                                       and (msp1.end_date is null or DATE_FORMAT(msp1.end_date, '%Y%m') >= concat(in_year, in_month))
  left join eb_section division on division.id = msp1.division_id
  left join eb_section department on department.id = msp1.section_id
  left join eb_section section on section.id = msp1.subsection_id
  left join eb_subcontractorrequest r on r.subcontractor_id = 1
                                     and r.section_id in (division.id, department.id, section.id)
                                     and r.year = in_year
                                     and r.month = in_month
  left join eb_projectmember pm on pm.is_deleted = 0
                               and pm.member_id = m.id
                               and DATE_FORMAT(pm.end_date, '%Y%m') >= concat(in_year, in_month)
                               and pm.id = (
                                   select id
                                     from eb_projectmember s1 
                                    where s1.is_deleted = 0 
                                      and s1.member_id = m.id 
                                      and DATE_FORMAT(s1.end_date, '%Y%m') >= concat(in_year, in_month)
                                    order by s1.end_date desc
                                    limit 1
                               )
  left join eb_project p on p.is_deleted = 0
						and p.id = pm.project_id
 where s.id = in_partner_id
   and s.is_deleted = 0
UNION ALL
select 0 as id
     , null as name
     , get_division_new(p.department_id) as division_id
     , (select name from eb_section where id = get_division_new(p.department_id)) as division_name
     , p.id as project_id
     , p.name as project_name
	 , r.id as request_id
     , r.request_no
     , r.pay_notify_no
     , r.filename_pdf
     , r.pay_notify_filename_pdf
     , r.is_sent
     , null as parent
  from eb_subcontractor s
  join eb_bp_lump_contract c on c.is_deleted = 0
                            and c.company_id = s.id
						    and DATE_FORMAT(c.start_date, '%Y%m') <= concat(in_year, in_month)
						    and (c.end_date is null or DATE_FORMAT(c.end_date, '%Y%m') >= concat(in_year, in_month))
  left join eb_project p on p.id = c.project_id
  left join eb_subcontractorrequest r on r.subcontractor_id = in_partner_id
                                     and get_division_new(r.section_id) = get_division_new(p.department_id)
                                     and r.year = in_year
                                     and r.month = in_month
 where s.id = in_partner_id
   and s.is_deleted = 0
;

END //

DELIMITER ;