CREATE OR REPLACE VIEW v_project AS
select p.id
     , p.name
     , c.id as customer_id
     , c.name as customer_name
     , p.business_type
     , p.salesperson_id
     , concat(s.first_name, ' ', s.last_name) as salesperson_name
     , (
	   select concat(m.first_name, ' ', m.last_name)
         from eb_projectmember pm
         join eb_member m on m.id = pm.member_id
		where pm.is_deleted = 0
          and pm.project_id = p.id
          and pm.status = '2'
          and pm.end_date >= current_date()
		order by pm.id
        limit 1
     ) as member_name
     , p.start_date
     , p.end_date
     , p.status
     , p.updated_date
  from eb_project p
  left join eb_client c on c.id = p.id
  left join eb_salesperson s on s.id = p.salesperson_id
 order by p.name
;
