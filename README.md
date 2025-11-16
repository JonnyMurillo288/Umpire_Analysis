# Umpire_Analysis 

## Overview  
**Umpire_Analysis** is an interactive dashboard and data-analysis repository designed to explore umpire bias and team favor factors in baseball.  
The project includes:  
- Time-series and distribution visuals for “favor factor” by team and season  
- A sortable table of umpires showing which umpires favor or hurt each team  
- Filtering by team and year, and a progressive “Load More” interface for deeper exploration  
- Designed for both exploratory analysis and public dashboard deployment  

## Features  
- Interactive switching between “worst for my team” and “best for my team” scenarios  
- Full dataset ingestion from MySQL (or compatible) database via SQLAlchemy  
- Smooth, configurable visualizations built with Plotly Express and Dash  
- Deployable as a web service (e.g., on Render.com)  
- Presented in a clean, mobile-friendly layout  
- Easily extensible for further deep dives (game-level detail, sparkline views, color-coded bias heat-maps)  

## Quick Demo  
> [Live Dashboard URL] – *Updating soon*  
*(Once deployed, insert the live app link here)*  

## Getting Started  

### Prerequisites  
- Python 3.8+  
- MySQL (or other supported relational DB) with the schema containing table `avg_factor_team_season` and `ump_favor_by_team`  
- Git  

### Installation  
1. Clone the repository  
   ```bash
   git clone https://github.com/JonnyMurillo288/Umpire_Analysis.git
   cd Umpire_Analysis
