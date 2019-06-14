CREATE OR REPLACE VIEW v_partner_cost_monthly AS
select min(r.id) as id
     , s.id as partner_id
     , s.name as partner_name
     , r.year
     , r.month
     , concat(r.year, r.month) as ym
     -- , min(r.month) as min_month
     -- , max(r.month) as max_month
     , sum(r.turnover_amount) as turnover_amount  -- 売上金額（基本単価＋残業料）（税抜き）
     , sum(r.tax_amount) as tax_amount
     , sum(r.expenses_amount) as expenses_amount  -- 精算金額
     , sum(r.amount) as amount
  from eb_subcontractor s
  join eb_subcontractorrequest r on r.subcontractor_id = s.id
 where s.is_deleted = 0
 group by s.id, s.name, r.year, r.month