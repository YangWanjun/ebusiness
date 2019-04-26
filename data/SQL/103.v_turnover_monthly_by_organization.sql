CREATE OR REPLACE VIEW v_turnover_monthly_by_organization AS
select concat(pr.year, pr.month) as id
     , pr.year
     , pr.month
     , get_division_new(p.department_id) as division_id
     -- , (select name from eb_section where id = get_division(p.department_id)) as name1
     , p.department_id  -- 部署
     -- , (select name from eb_section where id = p.department_id) as name2
     , sum(pr.cost) as cost
     , sum(pr.amount) as amount
     , sum(pr.turnover_amount) as turnover_amount
     , sum(pr.tax_amount) as tax_amount
     , sum(pr.expenses_amount) as expenses_amount
     , sum(pr.turnover_amount) - sum(pr.cost) as profit_amount
     , round((sum(pr.turnover_amount) - sum(pr.cost)) / sum(pr.turnover_amount), 1) * 100 as profit_rate
  from eb_projectrequest pr
  join eb_projectrequestheading prh on prh.project_request_id = pr.id
  join eb_project p on p.is_deleted = 0 and p.id = pr.project_id
 where p.department_id is not null
 group by pr.year, pr.month, p.department_id
 order by pr.year, pr.month
