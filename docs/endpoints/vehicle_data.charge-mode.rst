charge-mode
'''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/charge-mode``

Sample return:
   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/charge-mode.json
      :language: JSON

.. note::
   On older vehicles, such as Zoe40 (model code X101VE):
      The return values appear to be ``always_charging`` and ``schedule_mode``. This matches the ``vehicle_action.charge-mode`` action attributes.

   On newer vehicles, such as Zoe50 (model code X102VE):
      The return values appear to be ``always`` and ``scheduled``. This DOES NOT match the ``vehicle_action.charge-mode`` action attributes.
