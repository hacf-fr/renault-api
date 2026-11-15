charge-schedule
'''''''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/charge-schedule``

For vehicles using KCM settings, including the Mégane E-Tech (``XCB1VE``), the
endpoint is:
   ``/commerce/v1/accounts/{account_id}/kamereon/kcm/v1/vehicles/{vin}/ev/settings``

Sample return:
   Single:
      .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/charge-schedule.single.json
         :language: JSON
