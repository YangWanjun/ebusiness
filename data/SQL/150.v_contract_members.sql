CREATE OR REPLACE VIEW v_contract_members AS
select m.id
     , m.employee_id as code
     , concat(m.first_name, ' ', m.last_name) as name
     , m.sex as gender
     , m.birthday
     , m.join_date
     , ifnull(c.end_date2, if(c.id is not null, ifnull(c.end_date, '9999-12-31'), null)) as end_date
     , c.id as contract_id
     , c.contract_no
     , c.employment_date  -- 雇用日
     , if(c.endowment_insurance = '1', true, false) as has_insurance  -- 保険加入
     , case
           when c.id is null and bp_c.id is null then true
	       else m.is_retired
       end as is_retired
     , case
           when c.id is not null then c.member_type
           when bp_c.id	is not null then 4
           else null
       end as member_type
  from eb_member m
  left join eb_contract c on c.is_deleted = 0
						 and c.member_id = m.id
                         and c.status <> '04'
                         and ifnull(c.end_date2, ifnull(c.end_date, '9999-12-31')) >= current_date()
                         and c.id = (
                             select max(id)
                               from eb_contract c1
						      where c1.is_deleted = 0
                                and c1.member_id = m.id
                                and c1.status <> '04'
                                and ifnull(c1.end_date2, ifnull(c1.end_date, '9999-12-31')) >= current_date()
                         )
  left join eb_bp_contract bp_c on bp_c.is_deleted = 0
                               and bp_c.member_id = m.id
                               and ifnull(bp_c.end_date, '9999-12-31') >= current_date()
 where m.is_deleted = 0
--   and m.id = 506
 group by m.id
 order by concat(m.first_name, ' ', m.last_name)
