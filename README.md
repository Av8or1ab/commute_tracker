Description: Commute tracking application written in python 3.5, flask, MySQL, javascript, html and css (Bootstrap). The version is forked from DanielOrf/commute_tracker. I thought the fork was necessary since the data mechanism uses SQL alchemy instead of pymysql calling directly. The server stuff is just to adapt to having a seperate location table instead of just two locations. 

This application is designed to be run on AWS lambda or other serverless architecture to gather commute times using Google Maps at set intervals using 'data_collection.py'.  

A flask server (using 'ct_server.py') is used to display the data in a web page with the help of Bootstrap and Plotly(Javascript). Data can be displayed with a history of up to 10 days.  It can also be broken down per day of the week as well as all weekdays and weekends.  The original motivation was to visialize commute times between two destinations in a congested city to discern optimal travel times.

The file 'tokens_and_addresses.py' must be filled out with MySQL server login details, Google Maps API key, and optionally location data before data collection and webserver can function.

Installation requirements listed in 'requirements.txt'.

The result is currently on Amazon lambda and a locally managed MariaDB instance.  It will occasionally be taken down for updates.
