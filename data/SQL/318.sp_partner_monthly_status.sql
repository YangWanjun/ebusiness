DELIMITER //

DROP PROCEDURE IF EXISTS sp_partner_monthly_status //

/* 協力会社の月別状況 */
CREATE PROCEDURE sp_partner_monthly_status (
	in_partner_id integer
)
BEGIN

select id
     , year
     , month
     , concat(year, '年', month, '月') as name
     , member_count
     , request_count
     , division_count
     , sent_count
     , if(division_count <> 0 and division_count = sent_count, true, false) as is_all_sent
     , t.amount
  from (
select dates.ym as id
     , dates.year
	 , dates.month
     , count(distinct c.member_id) as member_count
     , count(distinct sr.id) as request_count
     , count(distinct get_division_new(ifnull(msp.division_id, ifnull(msp.section_id, msp.subsection_id)))) as division_count
     , count(distinct if(sr.is_sent, sr.id, null)) as sent_count
     , (select sum(s1.amount) from eb_subcontractorrequest s1 where find_in_set(s1.id, group_concat(distinct sr.id separator ',')) <> 0) as amount
  from eb_subcontractor s
  join v_turnover_dates dates
  left join eb_bp_contract c on c.is_deleted = 0
                            and c.company_id = s.id
                            and DATE_FORMAT(c.start_date, '%Y%m') <= dates.ym
                            and (DATE_FORMAT(c.end_date, '%Y%m') >= dates.ym or c.end_date is null)
  left join eb_member m on m.is_deleted = 0
                       and m.id = c.member_id
  left join eb_membersectionperiod msp on msp.is_deleted = 0
                                      and msp.member_id = m.id
                                      and DATE_FORMAT(msp.start_date, '%Y%m') <= dates.ym
                                      and (DATE_FORMAT(msp.end_date, '%Y%m') >= dates.ym or msp.end_date is null)
  left join eb_subcontractorrequest sr on sr.subcontractor_id = s.id
                                      and sr.year = dates.year
                                      and sr.month = dates.month
 where s.is_deleted = 0
   and s.id = in_partner_id
   and dates.ym >= (
       select DATE_FORMAT(min(c1.start_date), '%Y%m') 
         from eb_bp_contract c1 
		where c1.is_deleted = 0 
          and c1.company_id = in_partner_id
   )
 group by dates.ym, dates.year, dates.month
 order by dates.ym desc
) t
;

END //

DELIMITER ;