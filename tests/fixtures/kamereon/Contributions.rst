Contributing
============
- grab a trace.
- add the json file to the correct `test/fixtures/kamereon` subfolder.
- ensure that `vin` starts with `VF1AAAA-`
- ensure that `vehicleDetails.vin` also starts with `VF1AAAA-`
- ensure that `vehicleDetails.registrationNumber` starts with `REG-`
- ensure that the json file passes pre-commit (can be parsed online via https://codebeautify.org/jsonviewer)
- update this file to indicate what is interesting about the sample provided
- create a pull request


Sample vehicles
===============

captur_ii.1.json
----------------
First fuel vehicle.
Cockpit data has extra attributes fuelAutonomy and fuelQuantity that are not available on electric vehicles.

zoe_40.1.json
-------------
Navigation is available in the vehicle, but the location is not available through the API (NotSupported error).

zoe_40.2.json
-------------
Navigation is not available in the vehicle.
