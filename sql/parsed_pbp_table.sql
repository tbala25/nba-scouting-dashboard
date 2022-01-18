DROP table sr_nba.parsed_pbp;
create table sr_nba.parsed_pbp (
  game_id varchar(100),
  home_alias varchar(10),
  home_name varchar(100),
  away_alias varchar(10),
  away_name varchar(100),
  period_number int, 
  event_id varchar(100),
  event_clock varchar(100),
  event_description varchar(250),
  event_wall_clock varchar(100),
  event_type varchar(100),
  event_qualifiers varchar(500),
  event_coord_x varchar(10),
  event_coord_y varchar(10),
  event_action_area varchar(100),
  home_on_court_players varchar(100),
  away_on_court_players varchar(100),
  es_player varchar(100),
  es_team varchar(100),
  non_es_team varchar(100),
  es_type varchar(100),
  es_made varchar(10),
  es_shot_type varchar(10),
  es_shot_type_desc varchar(100),
  es_points int,
  es_shot_distance float,
  es_rebound_type varchar(10),
  es_free_throw_type varchar(10)
  )