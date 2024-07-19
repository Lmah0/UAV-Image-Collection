# UAV-Image-Collection

Simple repository used for aerial vehicle (copter, fixed-wing, or VTOL) geotagged image collection. Transmitter ode is developed for Raspberry Pi and assumes a valid connection to a Pixhawk running ArduPilot. Receiver code can be ran locally.

This does not include the required MAVProxy script used to pull flight coordinates on the flight controller. It assumes the SUAV MAVProxy script is already running and begins listening on a separate thread from the main server itself.

Additionally, this assumes a valid connection via RocketM5 to the temporary ground control station running on this laptop (under receiver).

Primary Uses:
- AI Training
- Camera Testing