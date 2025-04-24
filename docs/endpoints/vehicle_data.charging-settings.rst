charging-settings
'''''''''''''''''

.. rst-class:: endpoint

Base url:
   Default:
      ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/charging-settings``

   Alternate:
      ``/commerce/v1/accounts/{account_id}/kamereon/kcm/v1/vehicles/{vin}/ev/settings``

Sample return:
   Single:
      .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/charging-settings.single.json
         :language: JSON

   Multiple:
      .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/charging-settings.multi.json
         :language: JSON

   Alternate:
      .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/kcm-ev-settings.json
         :language: JSON
