drop view sr_nba.lineup_plusminus;
create view sr_nba.lineup_plusminus as
select game_id, period_number, team, lineup, sum(points) as points from (
(
select
game_id,
period_number, 
es_team as team,
case when es_team = home_name then home_on_court_players else away_on_court_players end as lineup,
es_points as points
from sr_nba.parsed_pbp
where es_points is not null
)  
union all
(select
game_id,
period_number,
case when es_team = home_name then away_name else home_name end as team,
case when es_team = home_name then away_on_court_players else home_on_court_players end as lineup,
-es_points as points
from sr_nba.parsed_pbp
where es_points is not null
)
)a
group by game_id, period_number, team, lineup
