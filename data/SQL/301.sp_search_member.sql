DELIMITER //

DROP PROCEDURE IF EXISTS sp_search_member //

/* アサインした社員のコスト */
CREATE PROCEDURE sp_search_member (
    in_keyword char(30)
)
BEGIN

select t.member_id
     , t.name
     , t.member_type
     , max(join_date) as join_date
     , max(end_date) as end_date
  from (
        select distinct c.id
             , concat(m.first_name, ' ', m.last_name) as name
             , c.member_id
             , c.member_type
             , c.join_date
             , c.start_date
             , ifnull(ifnull(c.end_date2, c.end_date), '9999-12-31') as end_date
          from eb_member m
          left join eb_contract c on c.is_deleted = 0 and c.member_id = m.id and c.status <> '04'
         where m.is_deleted = 0
           and (m.first_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
            or m.last_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
            or concat(m.first_name, ' ', m.last_name) collate utf8_unicode_ci like concat('%', in_keyword, '%')
           )
        UNION ALL
        select distinct c.id
             , concat(m.first_name, ' ', m.last_name) as name
             , c.member_id
             , 4 as member_type
             , null as join_date
             , c.start_date
             , ifnull(c.end_date, '9999-12-31') as end_date
          from eb_member m
          left join eb_bp_contract c on c.is_deleted = 0 and c.member_id = m.id and c.status <> '04'
         where m.is_deleted = 0
           and (m.first_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
            or m.last_name collate utf8_unicode_ci like concat('%', in_keyword, '%')
            or concat(m.first_name, ' ', m.last_name) collate utf8_unicode_ci like concat('%', in_keyword, '%')
           )
  ) t
 where t.member_id is not null
 group by t.member_id
;

END //

DELIMITER ;
