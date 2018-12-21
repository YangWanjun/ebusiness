CREATE OR REPLACE VIEW v_turnover_monthly AS
select concat(pr.year, pr.month) as id
     , concat(pr.year, '年', pr.month, '月') as ym
     , pr.year
     , pr.month
     , sum(pr.amount) as amount
     , sum(pr.turnover_amount) as turnover_amount
     , sum(pr.tax_amount) as tax_amount
     , sum(pr.expenses_amount) as expenses_amount
  from eb_projectrequest pr
  join eb_projectrequestheading prh on prh.project_request_id = pr.id
 group by pr.year, pr.month
 order by pr.year desc, pr.month desc
