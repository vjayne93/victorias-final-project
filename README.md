**Philadelphia Free Food Site Analysis and Web Application**
------------------------------------------------------------

My project analyzes a list of 286 free food sites within the City of Philadelphia and the surronding counties obtained from the City's [Food and Meal Finder](https://www.phila.gov/food/) site and Share Food Program's [Find Food Tool](https://www.sharefoodprogram.org/find-food).

**Part I** of my project uses K-Means Cluster Analysis to create recommendations for areas of the city where new free food sites should be opened.

**Part II** of my project is the development of a web application called [Philly Food Finder](https://philly-food-finder-5ea79faeb9e3.herokuapp.com/) which tells the user where their nearest open free food site is, based on their address. The application works for addresses within twelve miles of Philadelphia. This web application is live now.

## Part I: K-Means Cluster Analysis
The K-Means Cluster Analysis classifies each census tract in Philadelphia as least need, average need, and highest need for additional food sites. This classification is based upon the following features: the percentage of people with low access to healthy food, the percentage of people living under the poverty line in each census tract, the number of food sites within one mile of each census tract, and the total food site operating hours within one mile of each census tract. 

I completed two K-Means Cluster Analyses. The first weighted all features with the same importance. My first analysis indicated many census tracts in wealthy neighborhoods as part of the highest need group, because these neighborhoods have few free food sites. <br><br>
<img src="https://github.com/vjayne93/victorias-final-project/blob/main/cluster_analysis/maps/unweighted_analysis_image.png" alt="Unweighed Cluster Analysis Image" width="500">
<br><br>
<img src="https://github.com/vjayne93/victorias-final-project/blob/main/cluster_analysis/maps/detail_unweighted_analysis.png" alt="Detail Unweighed Cluster Analysis" width="500">
<br><br>
My second analysis weighed the percentage of people living under the poverty line as three-times more significant than all other features. This second analysis indicated primarily high-poverty census tracts as the areas of highest need. 
<img src="https://github.com/vjayne93/victorias-final-project/blob/main/cluster_analysis/maps/weighted_analysis_image.png" alt="Weighted Cluster Analysis Image" width="500">
<br><br>
The process of my K-Means Cluster Analysis is described below: 
* Clean datasets downloaded from the City of Philadelphia and Share Food Program to standardize addresses and hours of operation for all sites. Record cleaned data in a new spreadsheet. Filter data to Philadelphia sites only. 
* Load cleaned data into a Jupyter Notebook data frame. Due to the size of the dataset, I did not use a database tool to store the data. 
* Use OpenCageGeoCode API to assign a latitude and longitude value to all food sites. Create new data frame with these coordinates.
* Create a function to parse the operating days and hours of each site.
* Load GEOJSON from USDA on food availability by census tract & CSV from US Census Bureau on poverty levels by census tract to notebook.
* Create BallTree to do spacial analysis of food sites and determine the number of food sites within a one-mile radius of each census tract.
* Complete K-Means Cluster Analysis of the features of each census tract. Sort data into three clusters indicating least need, normal need, and highest need.
* Complete second K-Means Cluster Analysis which weighs poverty as three-times more significant than the other features to create a more accurate assesment of need. 


## Data Sources

* [City of Philadelphia: Food and Meal Finder](https://www.phila.gov/food)
* [US Census Bureau: Poverty Status in the Last 12 Months, 2020](https://data.census.gov/table?q=Poverty&g=050XX00US42101,42101$1400000)
* [USDA ERS: Understanding Low-Income and Low-Access Census Tracts Across the Nation: Subnational and Subpopulation Estimates of Access to Healthy Food, May 2019](https://www.ers.usda.gov/publications/pub-details/?pubid=93140)
* [My Sidewalk: Food Insecurity- An analysis of food insecurity and its impact in your community](https://reports.mysidewalk.com/e3daa45043)
* [US Census Bureau: TIGER/Line Shapefile, 2019, county, Philadelphia County, PA](https://catalog.data.gov/dataset/tiger-line-shapefile-2019-county-philadelphia-county-pa-topological-faces-polygons-with-all-geo)

## Acknowledgements
This project was possible through the work of the 100% volunteer team at [South Philadelphia Community Fridge](www.southphillyfridge.com). Special thanks to volunteer Doron Shore for data entry and application testing. 
