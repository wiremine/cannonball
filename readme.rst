Cannonball
----------

Cannonball is a django-based git repository viewer. 


Where'd the name come from?
---------------------------

Like all good Django project, this one is named after a Jazz great, Julian "Cannonball" Adderley. 

http://en.wikipedia.org/wiki/Cannonball_Adderley


Status
------

The tool is very basic, but usable at this point. We're looking for feedback, so let us know if you
have any fixes or ideas!


Motivation 
----------

Github and other git hosting services are great. But sometimes you want to add custom functionality
on top of git, and/or host your repos internally without spending extra cash. In the case of 
Cannonball's authors, we wanted a simple way to conduct code reviews using a web-based git viewer. 

gitweb is a handy tool, but wasn't designed for customization. At least... not that we could see ;-)

Cannonball uses the excellent Dulwich library to parse git repos and display them via a website. 

Since it's based on Django, it provides a variety of hooks to customize the experience, using the 
common MVC pattern. 


Install
-------

Requirements:

* Python (I'm using 2.6, milage will vary on other versions)
* Django 1.2 - http://www.djangoproject.com/
* South - http://south.aeracode.org/
* Dulwich - http://samba.org/~jelmer/dulwich/
* Pygments - http://pygments.org/

After you install the dependencies, you can install Cannnonball:

* Clone the repo: git clone git@github.com:wiremine/cannonball.git
* Customize settings.py as needed. By default it uses Sqlite, so no other requirements are needed.
* Run 'python manage.py syncdb' 
* Run 'python manage.py migrate' 
* Run 'python manage.py runserver'
* At this point you can login into http://localhost:8000/admin/ and add some projects. 
* Then navigate to http://localhost:8000/ to view your repos

Cannonball is a read-only tool: it doesn't write to your repositories.



