# UAV-Image-Collection

Simple repository used for aerial vehicle (copter, fixed-wing, or VTOL) geotagged image collection. Code is developed for Raspberry Pi and assumes a valid connection to a Pixhawk with ArduPilot. 

This does not include the required MAVProxy script used to pull flight coordinates on the flight controller. It assumes this MAVProxy script is already running and begins listening on a separate thread from the main server itself.

Additionally, this assumes a valid connection via RocketM5 to a ground control statio (i.e. A website like 2024GCS in the SUAV repo).

Primary Uses:
- AI Training
- Camera Testing