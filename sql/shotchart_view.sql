drop view sr_nba.shot_chart;
create view sr_nba.shot_chart as
select game_id, period_number, event_clock, 
event_coord_x,
event_coord_y,
-- event_coord_y - 300 as coord_x,
-- case when event_coord_x > 500 and event_action_area <> 'backcourt' then  event_coord_x - 1100 else event_coord_x end as coord_y,
event_action_area,
es_player,
es_team,
non_es_team,
case when es_team = home_name then TRUE else FALSE end as es_team_home,
es_type,
es_made, 
es_shot_distance
from
sr_nba.parsed_pbp
where es_type = 'fieldgoal'