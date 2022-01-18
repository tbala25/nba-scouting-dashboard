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