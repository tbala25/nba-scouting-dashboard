drop view sr_nba.team_game_four_factors;
create view sr_nba.team_game_four_factors as
select 
a.game_id, a.team,
(fgm + .5*3PM)/fga as 'off_efg%',
tov /(fga + 0.44*fta + tov) as off_TOV,
orb/(orb+opp_drb) as 'off_reb%',
fta/fga as off_ftr,
(opp_fgm + .5*opp_3PM)/opp_fga as 'def_efg%',
opp_tov /(opp_fga + 0.44*opp_fta + opp_tov) as def_TOV,
drb/(opp_orb+drb) as 'def_reb%',
opp_fta/opp_fga as def_ftr
from sr_nba.team_boxscore a 
join sr_nba.opp_team_boxscore b on a.game_id = b.game_id and a.team = b.team;

drop view sr_nba.team_four_factors;
create view sr_nba.team_four_factors as
select 
a.team,
(sum(fgm) + .5*sum(3PM))/sum(fga) as 'off_efg%',
sum(tov) /(sum(fga) + 0.44*sum(fta) + sum(tov)) as off_TOV,
sum(orb)/(sum(orb)+sum(opp_drb)) as 'off_reb%',
sum(fta)/sum(fga) as off_ftr,
(sum(opp_fgm) + .5*sum(opp_3PM))/sum(opp_fga) as 'def_efg%',
sum(opp_tov) /(sum(opp_fga) + 0.44*sum(opp_fta) + sum(opp_tov)) as def_TOV,
sum(drb)/(sum(opp_orb)+sum(drb)) as 'def_reb%',
sum(opp_fta)/sum(opp_fga) as def_ftr
from sr_nba.team_boxscore a 
join sr_nba.opp_team_boxscore b on a.team = b.team
group by a.team;

drop view if exists sr_nba.team_four_factors_rank;
create view team_four_factors_rank as
select `sr_nba`.`team_four_factors`.`team`     AS `team`,
       `sr_nba`.`team_four_factors`.`off_efg%` AS `off_efg%`,
       `sr_nba`.`team_four_factors`.`off_TOV`  AS `off_TOV`,
       `sr_nba`.`team_four_factors`.`off_reb%` AS `off_reb%`,
       `sr_nba`.`team_four_factors`.`off_ftr`  AS `off_ftr`,
       `sr_nba`.`team_four_factors`.`def_efg%` AS `def_efg%`,
       `sr_nba`.`team_four_factors`.`def_TOV`  AS `def_TOV`,
       `sr_nba`.`team_four_factors`.`def_reb%` AS `def_reb%`,
       `sr_nba`.`team_four_factors`.`def_ftr`  AS `def_ftr`,
       row_number() OVER `oe`                  AS `off_efg_rank`,
       row_number() OVER `ot`                  AS `off_tov_rank`,
       row_number() OVER `ore`                 AS `off_reb_rank`,
       row_number() OVER `oft`                 AS `off_ftr_rank`,
       row_number() OVER `de`                  AS `def_efg_rank`,
       row_number() OVER `dt`                  AS `def_tov_rank`,
       row_number() OVER `dre`                 AS `def_reb_rank`,
       row_number() OVER `dft`                 AS `def_ftr_rank`
from `sr_nba`.`team_four_factors`
    window
    `oe` AS (ORDER BY `sr_nba`.`team_four_factors`.`off_efg%` desc),
    `ot` AS (ORDER BY `sr_nba`.`team_four_factors`.`off_TOV` asc),
    `ore` AS (ORDER BY `sr_nba`.`team_four_factors`.`off_reb%` desc),
    `oft` AS (ORDER BY `sr_nba`.`team_four_factors`.`off_ftr` desc),
    `de` AS (ORDER BY `sr_nba`.`team_four_factors`.`def_efg%` asc),
    `dt` AS (ORDER BY `sr_nba`.`team_four_factors`.`def_TOV` desc),
    `dre` AS (ORDER BY `sr_nba`.`team_four_factors`.`def_reb%` desc),
    `dft` AS (ORDER BY `sr_nba`.`team_four_factors`.`def_ftr` asc);

