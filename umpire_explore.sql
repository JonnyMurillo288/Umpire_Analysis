use baseball2026;

DELETE FROM ump_scorecard
WHERE game_pk = 0;

-- For each team, and each season, get their average total_run_impact
-- CREATE TEMPORARY TABLE ump_favor_season_by_team AS

DROP TABLE ump_favor_season_by_team;
CREATE TEMPORARY TABLE ump_favor_season_by_team AS
SELECT 
    ROUND(favor,2) AS favor,
    home_team AS team,
    date,
    ROUND(overall_accuracy,2) AS overall_accuracy,
    'home' AS team_type
FROM ump_scorecard

UNION ALL

SELECT
    ROUND(favor,2) * -1 AS favor, -- Reverse the favor, since favor is displayed positive for home team
    away_team AS team,
    date,
    ROUND(overall_accuracy,2) AS overall_accuracy,
    'away' AS team_type
FROM ump_scorecard;

select * from ump_favor_season_by_team;

CREATE TABLE avg_factor_team_season AS
SELECT ROUND(AVG(favor),2) as avg_factor_year,count(favor) as num_games, team, YEAR(date) as year 
FROM ump_favor_season_by_team
GROUP BY team, year
ORDER BY avg_factor_year DESC;

SELECT DISTINCT YEAR(date)
FROM ump_scorecard;