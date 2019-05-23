DELIMITER //

DROP PROCEDURE IF EXISTS sp_organization_dashboard //

/* 社員の所属部署履歴 */
CREATE PROCEDURE sp_organization_dashboard (
    in_member_id integer           -- 社員ＩＤ
)
BEGIN

select msp.id
     , division.id as division_id
     , division.name as division_name
     , department.id as department_id
     , department.name as department_name
     , section.id as section_id
     , section.name as section_name
     , msp.start_date
     , msp.end_date
  from eb_membersectionperiod msp
  left join eb_section division on division.id = msp.division_id
  left join eb_section department on department.id = msp.section_id
  left join eb_section section on section.id = msp.subsection_id
 where msp.is_deleted = 0
   and msp.member_id = in_member_id
 order by msp.start_date
;

END //

DELIMITER ;