Python Linalg
===============


A simple numpy based simulator for the QLM platform.


installation
----------------

It is good practice to install packages inside a virtualenv:

Create a fresh virtual env:

$ virtualenv qlm_env

Activate the environment:

$ source ./qlm_env/bin/activate

Finally install the package:

$ python3 setup.py install

Running tests
-------------------

You might want to run pylinalg's test to check that everything is correctly installed.
This command will install pytest and run the tests:

$ python3 setup.py test
