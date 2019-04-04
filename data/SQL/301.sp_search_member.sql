DELIMITER //

DROP PROCEDURE IF EXISTS sp_search_member //

/* アサインした社員のコスト */
CREATE PROCEDURE sp_search_member (
    in_keyword char(30)
)
BEGIN

select m.id
     , m.name
     , t.member_type
     , t.join_date
     , t.end_date
     , sales.id as salesperson_id
	 , concat(sales.first_name, ' ', sales.last_name) as salesperson_name
     , division.id as division_id
     , division.name as division_name
     , department.id as department_id
     , department.name as department_name
     , section.id as section_id
     , section.name as section_name
     , t.partner_id
     , t.partner_name
  from (
        select m1.id as id
             , concat(m1.first_name, ' ', m1.last_name) as name
		  from eb_member m1
		 where m1.is_deleted = 0
		   and (m1.first_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
			or m1.last_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
			or concat(m1.first_name, ' ', m1.last_name) collate utf8_unicode_ci like concat('%', in_keyword, '%')
		   )
  ) m
  left join (
    select t1.member_id
         , t1.name
         , t1.member_type as member_type
         , ifnull(max(join_date), min(t1.start_date)) as join_date
         , max(end_date) as end_date
         , t1.partner_id
         , t1.partner_name
      from (
            -- ＥＢ契約
            select distinct c.id
                 , concat(m.first_name, ' ', m.last_name) as name
                 , m.id as member_id
                 , c.member_type
                 , c.join_date
                 , c.start_date
                 , ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31') as end_date
                 , null as partner_id
                 , null as partner_name
              from eb_member m
              join eb_contract c on c.is_deleted = 0 and c.member_id = m.id and c.status <> '04'
             where m.is_deleted = 0
               and (m.first_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
                or m.last_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
                or concat(m.first_name, ' ', m.last_name) collate utf8_unicode_ci like concat('%', in_keyword, '%')
               )
            UNION ALL
			-- ＢＰ契約
            select distinct c.id
                 , concat(m.first_name, ' ', m.last_name) as name
                 , m.id as member_id
                 , 4 as member_type
                 , c.start_date as join_date
                 , c.start_date
                 , ifnull(c.end_date, '9999-12-31') as end_date
                 , c.company_id as partner_id
                 , s1.name as partner_name
              from eb_member m
              join eb_bp_contract c on c.is_deleted = 0 and c.member_id = m.id and c.status <> '04'
              left join eb_subcontractor s1 on s1.id = c.company_id
             where m.is_deleted = 0
               and (m.first_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
                or m.last_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
                or concat(m.first_name, ' ', m.last_name) collate utf8_unicode_ci like concat('%', in_keyword, '%')
               )
      ) t1
     where t1.member_type is not null
     group by t1.member_id
            , t1.name
            , t1.member_type
  ) t on m.id = t.member_id
  left join eb_membersalespersonperiod msp1 on msp1.is_deleted = 0 and msp1.member_id = t.member_id and t.end_date between msp1.start_date and ifnull(msp1.end_date, '9999-12-31')
  left join eb_salesperson sales on sales.id = msp1.salesperson_id
  left join eb_membersectionperiod msp2 on msp2.is_deleted = 0 and msp2.member_id = t.member_id and t.end_date between msp2.start_date and ifnull(msp2.end_date, '9999-12-31')
  left join eb_section division on division.id = msp2.division_id
  left join eb_section department on department.id = msp2.section_id
  left join eb_section section on division.id = msp2.subsection_id
 order by m.id
        , t.join_date
;

END //

DELIMITER ;
