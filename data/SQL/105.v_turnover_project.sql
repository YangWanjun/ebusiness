CREATE OR REPLACE VIEW v_turnover_project AS
select p.id
     , p.name as project_name
     , p.client_id
     , c.name as customer_name
     , pr.year
     , pr.month
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
  join eb_client c on c.id = p.client_id
 group by c.id, p.id, pr.year, pr.month
;
