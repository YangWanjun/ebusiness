DELIMITER //

DROP PROCEDURE IF EXISTS sp_organization_members //

/* 部署内のメンバー一覧を取得 */
CREATE PROCEDURE sp_organization_members (
    in_org_id integer           -- 部署ＩＤ
)
BEGIN
select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     , msp1.start_date
     , msp1.end_date
     , group_concat(ps.position separator ',') as positions
     , if(count(pm.id) = 0, false, true) as is_working
  from eb_section s
  left join eb_membersectionperiod msp1 on msp1.is_deleted = 0
									   and (msp1.division_id = s.id or msp1.section_id = s.id or msp1.subsection_id = s.id)
                                       and msp1.start_date <= current_date()
                                       and (msp1.end_date >= current_date() or msp1.end_date is null)
  left join eb_member m on m.id = msp1.member_id
  left join eb_positionship ps on ps.is_deleted = 0
                              and ps.section_id = s.id
                              and ps.member_id = m.id
  left join eb_projectmember pm on pm.is_deleted = 0
                               and pm.member_id = m.id
                               and ifnull(pm.end_date, '9999-12-31') >= current_date()
                               and pm.id = (
                                   select id
                                     from eb_projectmember s1 
                                    where s1.is_deleted = 0 
                                      and s1.member_id = m.id 
                                      and ifnull(s1.end_date, '9999-12-31') >= current_date()
                                    order by s1.end_date desc
                                    limit 1
                               )
 where s.is_deleted = 0
   and s.id = in_org_id
 group by m.id, m.first_name, m.last_name, msp1.id
 order by concat(m.first_name, ' ', m.last_name)
;

END //

DELIMITER ;