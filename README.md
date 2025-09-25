# INFLUENCER ENGAGEMENT AND SPONSORSHIP COORDINATION PLATFORM

It's a platform to connect Sponsors and Influencers so that sponsors can get their 
product/service advertised and influencers can get monetary benefit.

---
# NOTE

For this Application I have used flask framework to create the backend of the application. 
The Frontend is purely made through HTML, and CSS. Only a very small amount of JavaScript has 
been used in the project. No Asynchronous function are used anywhere. Every request has to go 
to the Flask backend server, which then renders the appropriate content back to the browser after 
performing s all calculations and interactions with the database.

# Technologies Used 

- Flask : Backend Framework for building the application -
-  SQL-ALCHEMY : ORM(object-Relational-Mapping) tool for database Interaction 
- SQLite : Database Management system for storing Application Data 
- HTML/CSS/JavaScript : Frontend Technologies for User Interface design and Interactivity. Also 
  used Bootstrap for styling. 
- Flask-restful : Used for creating API for Flask Application  
- Datetime : python library for managing date and time 
- OS : python library that provides a way to interact with the operating system , files etc… 
- Functools : python library. Used to create decorators 
- Jinja2 : Template engine for rendering dynamic content 
- Werkzeug : utility for securely managing passwords and authentication 
- ChartJs : Used for creating charts

# API

SponsorAPI : For getting sponsor detail for a given id 
End Point :  /api/<int:id>/sponsor 
InfluencerAPI : For getting Influencer detail for a given id 
End Point :  /api/<int:id>/influencer 
CampaignAPI : For getting Campaign details for a given id 
End Point :  /api/<int:id>/campaign 

# YOUTUBE

https://www.youtube.com/watch?v=W8pO828mPK4&list=PLzCyUSjRa8prdNTZjEB6swq8zRWBEVo5V 

