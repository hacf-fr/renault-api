actions/horn-lights
'''''''''''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/actions/horn-lights``

Sample payload:
   Start horn:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "HornLights",
            "attributes": {"action": "start", "target": "horn"}
         }
      }

   Start lights:

   .. code-block:: JavaScript

      {
         "data": {
            "type": "HornLights",
            "attributes": {"action": "start", "target": "lights"}
         }
      }
