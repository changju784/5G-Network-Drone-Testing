## AT&T 5G Network Drone Testing  - Red Team - Project Description

## Visions and Goals of the Project

Our machine learning model will be used to model 5G network performance for use with commercial drone fleets. High level goals of this project include:

  - Developing a ML model in Python to predict network performance at different altitudes based on network performance on the ground
  - Using the ML model to build a 3D map of AT&T's 5G network (network performance based on GPS coordinates (2 dimensions) + altitude (3rd dimension)

## Users and Personas of this Project

The main beneficiaries of our project are AT&T, who will be able to learn more about the performance of their network in the air to measure the feasibility of deploying a commercial drone fleet connected to AT&T's network.

Additionally any company that doesn't have the ability to implement their own satellite network will be able to use our models to show weather it makes sense to deploy a drone fleet connected to a major ISP's 5G network.

## Scope and Features of the Project

  Collect data used to model 5G network performance:
  
  - Build hardware for data collection
    - Sensors + processor
    - Install hardware on a drone
  - Store data in cloud database
  
  Build machine learning model to model 5G performance with drones
  
  - Predict air performance based on ground performance
  - Predict ground performance based on air performance
  - Use GPS coordinates to build 3D map of network
 
## Solution Concept

!{Image](solution_concept.png)

