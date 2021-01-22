battery-status
''''''''''''''

Base url:
    /commerce/v1/accounts/{account_id}/kamereon/kca/car-adapter/v2/cars/{vin}/battery-status

Sample data:
    A `battery-status sample return <https://github.com/hacf-fr/renault-api/blob/main/tests/fixtures/kamereon/vehicle_data/battery-status.2.json>`_ is available in the `fixtures`_ folder

Special notes:
    * ``batteryTemperature`` is not always present.
    * ``batteryCapacity`` appears to always return ``0``.

    On Zoe40 (model code X101VE)
        * ``chargingInstantaneousPower`` gives value in watts.
        * ``chargingStatus`` uses only a subset of `ChargeStatus`_ enum (NOT_IN_CHARGE = 0.0, CHARGE_IN_PROGRESS = 1.0, CHARGE_ERROR = -1.0)

    On Zoe50 (model code X102VE)
        * ``batteryTemperature`` appears completely wrong.
        * ``chargingInstantaneousPower`` seems to return values in kilowatts, but the values still appear completely wrong.
