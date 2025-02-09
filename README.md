# gdb_final_project
Alex Rump, Caro Niebl

final project for geodatabases course

note to self: conda environment is called gdb_final

## how to run
1. set up your postgis database.
for this i used a docker container with the following parameters:
```
username="gdb",
port="5432",
database="gdb_db",
password="gdb",
```
use the commands in init.sql to set up the required tables

2. run the fetch.py script. This may take a while as it attempts to load all bike-box measurements on opensensemap

## functionality.
This project is to consist of 2 components:

	1. Server 
 		- Fetches sensebox:bike measurements from openSensemap. 
 		- stores measurements & trajectories in database. 
 		- provides these as usable data for the frontend. 
 		- serves frontend. 
 
  	2. Frontend 
 		- simple web viewer. web design is kept simple and lightweight. 
 		- data visualisation of stashed sensebox bike data. 
 		- basically just go wild and do what you can with leaflet. 
