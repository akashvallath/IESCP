It's a platform to connect Sponsors and Influencers so that sponsors can get their 
product/service advertised and influencers can get monetary benefit.

For this Application I have used flask framework to create the backend of the application. 
The Frontend is purely made through HTML, and CSS. Only a very small amount of JavaScript has 
been used in the project. No Asynchronous function are used anywhere. Every request has to go 
to the Flask backend server, which then renders the appropriate content back to the browser after 
performing s all calculations and interactions with the database.

Technologies Used 
1. Flask : Backend Framework for building the application 
2. SQL-ALCHEMY : ORM(object-Relational-Mapping) tool for database Interaction 
3. SQLite : Database Management system for storing Application Data 
4. HTML/CSS/JavaScript : Frontend Technologies for User Interface design and Interactivity. Also 
used Bootstrap for styling. 
5. Flask-restful : Used for creating API for Flask Application  
6. Datetime : python library for managing date and time 
7. OS : python library that provides a way to interact with the operating system , files etc… 
8. Functools : python library. Used to create decorators 
9. Jinja2 : Template engine for rendering dynamic content 
10. Werkzeug : utility for securely managing passwords and authentication 
11. ChartJs : Used for creating charts

API
SponsorAPI : For getting sponsor detail for a given id 
End Point :  /api/<int:id>/sponsor 
InfluencerAPI : For getting Influencer detail for a given id 
End Point :  /api/<int:id>/influencer 
CampaignAPI : For getting Campaign details for a given id 
End Point :  /api/<int:id>/campaign 

YOUTUBE
https://www.youtube.com/watch?v=W8pO828mPK4&list=PLzCyUSjRa8prdNTZjEB6swq8zRWBEVo5V 
