actions/charging-start
''''''''''''''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/actions/charging-start``

Sample payload:
   Start charge:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "ChargingStart", 
            "attributes": {"action": "start"}
         }
      }

   Stop charge:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "ChargingStart", 
            "attributes": {"action": "stop"}
         }
      }


   Please check the `Contributor Guide`_ to provide extra samples.
