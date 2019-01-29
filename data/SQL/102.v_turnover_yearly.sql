CREATE OR REPLACE VIEW v_turnover_yearly AS
select pr.year
     , sum(pr.amount) as amount
     , sum(pr.turnover_amount) as turnover_amount
     , sum(pr.tax_amount) as tax_amount
     , sum(pr.expenses_amount) as expenses_amount
  from eb_projectrequest pr
  join eb_projectrequestheading prh on prh.project_request_id = pr.id
 group by pr.year
 order by pr.year