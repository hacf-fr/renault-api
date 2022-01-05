hvac-status
'''''''''''

.. rst-class:: endpoint

Base url:
   ``/commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v1/cars/{vin}/hvac-status``

Samples return:
   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/hvac-status.1.json
      :language: JSON

   .. literalinclude:: /../tests/fixtures/kamereon/vehicle_data/hvac-status.2.json
      :language: JSON

.. note::
   On Zoe40 (model code X101VE):
      ``hvacStatus`` seems to always report ``off``, even when preconditioning is in progress.

   On Zoe50 (model code X102VE):
      This endpoint seem to be unavailable and returns an error ``'err.func.403': 'Operation not supported Operation not supported for this can (C1A)'``.
