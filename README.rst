Renault API
===========

|PyPI| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/renault-api.svg
   :target: https://pypi.org/project/renault-api/
   :alt: PyPI
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/renault-api
   :target: https://pypi.org/project/renault-api
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/renault-api
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/renault-api/latest.svg?label=Read%20the%20Docs
   :target: https://renault-api.readthedocs.io/
   :alt: Read the documentation at https://renault-api.readthedocs.io/
.. |Tests| image:: https://github.com/hacf-fr/renault-api/workflows/Tests/badge.svg
   :target: https://github.com/hacf-fr/renault-api/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/hacf-fr/renault-api/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/hacf-fr/renault-api
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

This Python package manages the communication with the private Renault API used by the official MyRenault application.

The client is able to read various vehicle attributes, such as:

* mileage
* GPS location
* fuel autonomy (for fuel vehicles)
* battery autonomy (for electric vehicles)
* contracts associated to the vehicle (warranty and connected services)

For some vehicles, it is also possible to manage:

* hvac/pre-conditionning of the vehicle
* charge schedule

This package has been developed to be used with Home-Assistant, but it can be used in other contexts


Requirements
------------

* Python (>= 3.7.1)

API Usage
---------

You can install *Renault API* via pip_ from PyPI_:

.. code:: console

   $ pip install renault-api

.. code:: python

   import aiohttp
   import asyncio

   from renault_api.renault_client import RenaultClient

   async def main():
      async with aiohttp.ClientSession() as websession:
         client = RenaultClient(websession=websession, locale="fr_FR")
         await client.session.login('email', 'password')
         print(f"Accounts: {await client.get_person()}") # List available accounts, make a note of kamereon account id

         account_id = "Your Kamereon account id"
         account = await client.get_api_account(account_id)
         print(f"Vehicles: {await account.get_vehicles()}") # List available vehicles, make a note of vehicle VIN

         vin = "Your vehicle VIN"
         vehicle = await account.get_api_vehicle(vin)
         print(f"Cockpit information: {await vehicle.get_cockpit()}")
         print(f"Battery status information: {await vehicle.get_battery_status()}")

   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())

CLI Usage
---------

The renault-api is also available through a CLI, which requires additional dependencies.
For the added dependencies, you can install *Renault API* via pip_ from PyPI_:

.. code:: console

   $ pip install renault-api[cli]

Once installed, the following command prompts for credentials and settings, displays basic vehicle status information, and generates traces:

.. code:: console

   $ renault-api --log status

* Credentials will automatically be stored in the user home directory (~/.credentials/renault-api.json)
* Logs will automatically be generated in `logs` subfolder

Please see the `Command-line Reference <Usage_>`_ for full details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the MIT_ license,
*Renault API* is free and open source software.


Disclaimer
----------

This project is not affiliated with, endorsed by, or connected to Renault. I accept no responsibility for any consequences, intended or accidental, as a as a result of interacting with Renault's API using this project.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.
This project was heavily based on `@jamesremuscat`_'s `PyZE`_ python client for the Renault ZE API.


.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _@jamesremuscat: https://github.com/jamesremuscat
.. _PyZE: https://github.com/jamesremuscat/pyze
.. _MIT: http://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/hacf-fr/renault-api/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://renault-api.readthedocs.io/en/latest/usage.html
