# gdb_final_project
Alex Rump, Caro Niebl

final project for geodatabases course

note to self: conda environment is called gdb_final

## functionality.
This project is to consist of 2 components:
	1. Server
 		- Fetches sensebox:bike measurements from openSensemap.
 		- stores measurements & trajectories in database.
 		- provides these as usable data for the frontend.
 		- serves frontend.
 		- uses flask or django
 			- django sounds like it has everyhing we need set up already. but i haven't used it before
 	2. Frontend
 		- simple web viewer. web design is kept simple and lightweight.
 		- data visualisation of stashed sensebox bike data.
 		- basically just go wild and do what you can with leaflet.
