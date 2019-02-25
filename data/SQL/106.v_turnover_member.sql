CREATE OR REPLACE VIEW v_turnover_member AS
select m.id
     , concat(m.first_name, ' ', m.last_name) as name
     , prd.member_section_id
     , s.name as org_name
     , pm.project_id
     , p.client_id
     , pr.year
     , pr.month
     , prd.cost as cost
     , prd.total_price as turnover_amount
     , prd.expenses_price as expenses_amount
     , prd.total_price - prd.cost as profit_amount
     , round((prd.total_price - prd.cost) / prd.total_price, 1) * 100 as profit_rate
  from eb_projectrequestdetail prd
  join eb_projectrequest pr on pr.id = prd.project_request_id
  join eb_projectmember pm on pm.id = prd.project_member_id
  join eb_member m on m.id = pm.member_id
  join eb_project p on p.is_deleted = 0 and p.id = pm.project_id
  join eb_client c on c.id = p.client_id
  left join eb_section s on s.id = prd.member_section_id
;
