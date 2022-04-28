actions/charging-start
''''''''''''''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/actions/charging-start``

Sample payload:
   Start charge:
      ```json
      {
         "data": {
            "type": "ChargingStart", 
            "attributes": {"action": "start"}
         }
      }
       ```

   Stop charge:
      ```json
      {
         "data": {
            "type": "ChargingStart", 
            "attributes": {"action": "stop"}
         }
      }
       ```


   Please check the `Contributor Guide`_ to can provide a sample.
