Renault endpoints
=================


This is a list of the endpoints available, and their characteristics.

.. _fixtures: https://github.com/hacf-fr/renault-api/blob/main/tests/fixtures/kamereon/vehicle_data/
.. _chargestatus: https://github.com/hacf-fr/renault-api/blob/main/src/renault_api/kamereon/enums.py
.. _Contributor Guide: contributing.html


Vehicle information endpoints
-----------------------------

.. include:: endpoints/vehicle_data.alerts.rst


Vehicle data endpoints
----------------------

.. include:: endpoints/vehicle_data.battery-status.rst
.. include:: endpoints/vehicle_data.charge-history.rst
.. include:: endpoints/vehicle_data.charge-mode.rst
.. include:: endpoints/vehicle_data.charge-schedule.rst
.. include:: endpoints/vehicle_data.charges.rst
.. include:: endpoints/vehicle_data.charging-settings.rst
.. include:: endpoints/vehicle_data.charge-soclevels.rst
.. include:: endpoints/vehicle_data.cockpit.rst
.. include:: endpoints/vehicle_data.hvac-history.rst
.. include:: endpoints/vehicle_data.hvac-sessions.rst
.. include:: endpoints/vehicle_data.hvac-status.rst
.. include:: endpoints/vehicle_data.hvac-settings.rst
.. include:: endpoints/vehicle_data.location.rst
.. include:: endpoints/vehicle_data.lock-status.rst
.. include:: endpoints/vehicle_data.notification-settings.rst
.. include:: endpoints/vehicle_data.pressure.rst
.. include:: endpoints/vehicle_data.res-state.rst

Vehicle KCM data endpoints
--------------------------

.. include:: endpoints/vehicle_kcm_data.ev-settings.rst
.. include:: endpoints/vehicle_kcm_data.soc-levels.rst


Action endpoints
----------------

.. include:: endpoints/vehicle_action.charge-mode.rst
.. include:: endpoints/vehicle_action.charge-schedule.rst
.. include:: endpoints/vehicle_action.charging-start.rst
.. include:: endpoints/vehicle_action.horn-lights.rst
.. include:: endpoints/vehicle_action.hvac-start.rst
.. include:: endpoints/vehicle_action.hvac-schedule.rst


KCM Action endpoints
--------------------

.. include:: endpoints/vehicle_kcm_actions.charge-pause-resume.rst
