actions/charge-mode
'''''''''''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/actions/charge-mode``

Sample payload:
   Use instant charging:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "ChargeMode",
            "attributes": {"action": "always_charging"}
         }
      }

   Use scheduled charging:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "ChargeMode",
            "attributes": {"action": "schedule_mode"}
         }
      }


   Please check the `Contributor Guide`_ to provide extra samples.

.. note::
   All vehicles seem to use `always_charging` and `schedule_mode`.

   On older vehicles, such as Zoe40 (model code X101VE):
      This matches the ``vehicle_data.charge-mode`` return values: ``always_charging`` and ``schedule_mode``.

   On newer vehicles, such as Zoe50 (model code X102VE):
      This DOES NOT match the ``vehicle_data.charge-mode`` return values which are: ``always`` and ``scheduled``.
