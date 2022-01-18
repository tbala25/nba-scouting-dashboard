drop view sr_nba.opp_boxscore_lineup;
create view sr_nba.opp_boxscore_lineup as 
select
game_id,
non_es_team as team,
es_player as player,
case when non_es_team = home_name then home_on_court_players else away_on_court_players end as lineup,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as opp_FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as opp_FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as opp_3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as opp_3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as opp_FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as opp_FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as opp_ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as opp_DRB,
sum(case when es_type='rebound' then 1 else 0 end) as opp_REB,
sum(case when es_type='assist' then 1 else 0 end) as opp_AST,
sum(case when es_type='steal' then 1 else 0 end) as opp_STL,
sum(case when es_type='block' then 1 else 0 end) as opp_BLK,
sum(case when es_type='turnover' then 1 else 0 end) as opp_TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as opp_PF,
sum(es_points) as opp_PTS

from sr_nba.parsed_pbp 
group by game_id, team , player, lineup
order by game_id, team, player, lineup;


drop view sr_nba.opp_boxscore;
create view sr_nba.opp_boxscore as 
select
game_id,
non_es_team as team,
es_player as player,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as opp_FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as opp_FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as opp_3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as opp_3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as opp_FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as opp_FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as opp_ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as opp_DRB,
sum(case when es_type='rebound' then 1 else 0 end) as opp_REB,
sum(case when es_type='assist' then 1 else 0 end) as opp_AST,
sum(case when es_type='steal' then 1 else 0 end) as opp_STL,
sum(case when es_type='block' then 1 else 0 end) as opp_BLK,
sum(case when es_type='turnover' then 1 else 0 end) as opp_TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as opp_PF,
sum(es_points) as opp_PTS

from sr_nba.parsed_pbp 
group by game_id, team , player;

drop view sr_nba.opp_team_boxscore;
create view sr_nba.opp_team_boxscore as 
select
game_id,
non_es_team as team,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as opp_FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as opp_FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as opp_3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as opp_3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as opp_FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as opp_FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as opp_ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as opp_DRB,
sum(case when es_type='rebound' then 1 else 0 end) as opp_REB,
sum(case when es_type='assist' then 1 else 0 end) as opp_AST,
sum(case when es_type='steal' then 1 else 0 end) as opp_STL,
sum(case when es_type='block' then 1 else 0 end) as opp_BLK,
sum(case when es_type='turnover' then 1 else 0 end) as opp_TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as opp_PF,
sum(es_points) as opp_PTS

from sr_nba.parsed_pbp 
group by game_id, team ;