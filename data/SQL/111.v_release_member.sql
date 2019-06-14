CREATE OR REPLACE VIEW v_release_member AS
select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     , min(pm.start_date) as start_date
     , max(pm.end_date) as end_date
     , date_format(max(pm.end_date), '%Y') as release_year
     , date_format(max(pm.end_date), '%m') as release_month
  from eb_member m
  join eb_projectmember pm on pm.is_deleted = 0
						  and pm.member_id = m.id
                          and pm.status = 2
                          and pm.end_date > LAST_DAY(date_add(current_date(), interval -1 month))
                          and pm.end_date <= LAST_DAY(date_add(current_date(), interval 2 month))
  join eb_project p on p.is_deleted = 0
                   and p.id = pm.project_id
                   and p.is_reserve = 0
 where m.is_deleted = 0
   and not exists (
           select 1
             from eb_projectmember s1 
			where s1.member_id = m.id
              and s1.is_deleted = 0
              and s1.status = 2
              and s1.start_date between pm.end_date and date_add(pm.end_date, interval 1 month)
       )
 group by m.id, m.first_name, m.last_name
