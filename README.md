App for managing invoicing of cell operator services in t-mobile VPN group.

Usage
-----

1. Add 'creditbased-vpnadmin' application in the ``INSTALLED_APPS`` settings:
   
	INSTALLED_APPS = (
	    # ...
	    'creditbased-vpnadmin',
	)

3. Run 'python manage.py migrate creditbased-vpnadmin' to create DB tables (uses django-south).