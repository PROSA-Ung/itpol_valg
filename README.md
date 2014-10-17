itpol_valg
==========

Meeting application: Lets the audience ask questions and keeps track of individual speaker times.


System Requerements
===================
The time keeper (tidstager.html) is a simple HTML page with JavaScript. It can be put on a web server, or be used directly from the local disk. Just open it in a browser.

The question application has to use a web server. It has been tested on Apache on Linux, but it should be possible to run on other webservers, too (perhaps with minor adjustments).
It also requires MySQL and Perl with the CGI, DBI, and DBD::mysql modules.


Security
========
This application is quite insecure:

* Anyone can ask questions. Spambots _will_ do this eventually if the application is publically available.
* Users can vote several times simply by changing their UID.
* Everyone can become moderator simply by guessing the moderator's UID.


How to use
==========
Simply put all files in a directory on your web server.

To configure the time keeper, edit the tidstager.html file: Replace the "Navn Navnsen" entries with the names of the different speakers.
If you add or delete speaker rows, remember to change in "function all_bars()" accordingly.

For the question application, start by creating a MySQL database. Then run the create.sql script in mysql. To do this, run "mysql -u root -p" and give the following commands:
``` sql
create database my_database;
create user 'my_user'@'localhost' identified by 'my_password';
grant all privileges on my_database.* to my_user;
use my_database;
\. /path/to/create.sql
```

Edit the files ask.cgi, index.cgi, and moderate.cgi and edit the lines containing "DBI->connect" to include the correct connection details for your database.

Edit the files index.cgi and moderate.cgi and set the moderator UIDs in the "%admins" section. You should choose some random UIDs for that.
The moderator logs in by setting his UID to one of the UIDs in the %admin section in the browser, i.g. by opening http://server.name/path/to/va/?force_uid=1234 in his browser.


You might need to add the lines
``` apache
AddHandler cgi-script .cgi
Options +ExecCgi
```

to your Apache configuration - either in a .htaccess file or in the Apache site configuration.

License
=======
The meeting application (everything in the "va" directory) is licensed under the GNU General Public License v3.

The time keeper application (tidstager.html) is licensed under a CC-By license.
