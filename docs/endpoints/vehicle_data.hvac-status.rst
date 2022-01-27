hvac-status
'''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/hvac-status``

Samples return:
   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/hvac-status.spring.json
      :language: JSON

   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/hvac-status.zoe.json
      :language: JSON

   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/hvac-status.zoe_50.json
      :language: JSON

.. note::
   On Zoe40 (model code X101VE):
      ``hvacStatus`` seems to always report ``off``, even when preconditioning is in progress.
