drop view sr_nba.boxscore_lineup;
create view sr_nba.boxscore_lineup as 
select 
game_id,
es_team as team,
es_player as player,
case when es_team = home_name then home_on_court_players else away_on_court_players end as lineup,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as 3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as 3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as DRB,
sum(case when es_type='rebound' then 1 else 0 end) as REB,
sum(case when es_type='assist' then 1 else 0 end) as AST,
sum(case when es_type='steal' then 1 else 0 end) as STL,
sum(case when es_type='block' then 1 else 0 end) as BLK,
sum(case when es_type='turnover' then 1 else 0 end) as TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as PF,
sum(es_points) as PTS
from sr_nba.parsed_pbp 
group by game_id, es_team, es_player, lineup;


drop view sr_nba.boxscore;
create view sr_nba.boxscore as 
select 
game_id,
es_team as team,
es_player as player,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as 3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as 3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as DRB,
sum(case when es_type='rebound' then 1 else 0 end) as REB,
sum(case when es_type='assist' then 1 else 0 end) as AST,
sum(case when es_type='steal' then 1 else 0 end) as STL,
sum(case when es_type='block' then 1 else 0 end) as BLK,
sum(case when es_type='turnover' then 1 else 0 end) as TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as PF,
sum(es_points) as PTS
from sr_nba.parsed_pbp 
group by game_id, es_team, es_player;


drop view sr_nba.team_boxscore;
create view sr_nba.team_boxscore as 
select 
game_id,
es_team as team,
sum(case when es_type = 'fieldgoal' and es_made = 'True' then 1 else 0 end) as FGM,
sum(case when es_type = 'fieldgoal' then 1 else 0 end) as FGA,
sum(case when es_made = 'True' and es_points='3' then 1 else 0 end) as 3PM,
sum(case when es_type='fieldgoal' and event_type like 'threepoint%' then 1 else 0 end) as 3PA,
sum(case when es_made = 'True' and es_type='freethrow' then 1 else 0 end) as FTM,
sum(case when es_type='freethrow' then 1 else 0 end) as FTA,
sum(case when es_type='rebound' and es_rebound_type = 'offensive' then 1 else 0 end) as ORB,
sum(case when es_type='rebound' and es_rebound_type = 'defensive' then 1 else 0 end) as DRB,
sum(case when es_type='rebound' then 1 else 0 end) as REB,
sum(case when es_type='assist' then 1 else 0 end) as AST,
sum(case when es_type='steal' then 1 else 0 end) as STL,
sum(case when es_type='block' then 1 else 0 end) as BLK,
sum(case when es_type='turnover' then 1 else 0 end) as TOV,
sum(case when es_type='personalfoul' then 1 else 0 end) as PF,
sum(es_points) as PTS
from sr_nba.parsed_pbp 
group by game_id, es_team

