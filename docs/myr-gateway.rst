MyRenault app gateway ("myr")
=============================

The official MyRenault mobile app (6.13.x–6.14.x) talks to two backends:

.. list-table::
   :header-rows: 1

   * - Backend
     - Base URL
     - Role
   * - Kamereon (legacy)
     - ``https://api-wired-prod-1-euw1.wrd-aws.com/commerce/v1``
     - Vehicle data, actions, notifications. This is what this library implements
       (see :doc:`endpoints`).
   * - myr gateway
     - ``https://apis.renault.com``
     - App dashboard, remote-feature mapping, connected maintenance, KYC.

The ``myr`` gateway was observed in official-app traffic (iOS 6.13.1, TLS capture)
and cross-checked against the Android APK 6.13.4 (``com.renault.myrenault.one.fr``,
jadx decompilation). Endpoint availability varies by model and contract: the
observations below come from three vehicles, all in country ``FR``:

* a 2025 Renault Espace VI E-Tech full hybrid (XHN1ML), referred to as the HEV;
* a full-EV vehicle (XCB1VE);
* a 2017 Renault ZOE (X101VE, TCU gen 2), referred to as the ZOE.

Unless stated otherwise, observations come from the HEV.

Authentication
--------------

The gateway accepts the same Gigya JWT used by Kamereon:

.. code-block:: text

   GET /myr/api/v1/... HTTP/1.1
   Host: apis.renault.com
   apikey: <kamereon api key>
   x-gigya-id_token: <Gigya JWT>

* ``apikey`` is required (same key as Kamereon). Without it:
  ``401 {"errorCode": "10.01.02.01", "errorMessage": "Missing apikey."}``.
* The JWT goes in the ``x-gigya-id_token`` header. The same legacy JWT sent as
  ``Authorization: Bearer`` is rejected (401 ``err.func.wired.unauthorized``).
* ``/ccx/garage-center/v1/...`` was reported to reject the legacy Gigya JWT and
  to require the OIDC access token described below. However, on the ZOE
  account it accepted the legacy JWT in ``x-gigya-id_token`` (200).

For reference, the official app itself sends an OIDC access token
(``Authorization: Bearer at+JWT``, TTL 300 s) minted by:

.. code-block:: text

   https://gigya-prod-eu1.idconnect.renaultgroup.com/oidc/op/v1.0/{gigya_api_key}/

with ``client_id: qiXX6GdXSgerKxYqvdAblK_M`` and scopes
``openid email personId lang renaultGroupFull`` (``authorization_code`` + PKCE,
no password grant). The ``{gigya_api_key}`` EU value appears in the issuer path.
These constants are extracted from the app binaries. For first-party use of
``/myr/api/v1/*``, the legacy Gigya JWT in ``x-gigya-id_token`` is sufficient.

Endpoints
---------

Verified live:

.. list-table::
   :header-rows: 1

   * - Method
     - Path
     - Notes
   * - GET
     - ``/myr/api/v1/accounts/{account_id}/connected-vehicles?vin={vin}&country={country}``
     - Returns ``vehicleLinks`` per vehicle: ``vehicleDetails`` and
       ``connectedStatus`` (``services``, ``applicableFeatures``,
       ``remoteSecurityProtocol``, ``privacyModeStatus``, ...).
       ``applicableFeatures`` is absent on the ZOE. ``vin``,
       ``locale`` and ``oms`` query params are optional; without ``vin`` the
       whole garage is returned.
   * - GET
     - ``/myr/api/v1/accounts/{account_id}/vehicles/{vin}/dashboard?country={country}&type={type}&paired={bool}``
     - Observed ``type=HEV&paired=true``; returns ``cockpit`` (fuelAutonomy,
       fuelQuantity, totalMileage, timestamp). ``type`` is a fixed server-side
       enum, independent of the vehicle powertrain: ``HEV`` is accepted even on
       a full-EV vehicle, while ``EV`` is rejected on both an EV and an HEV
       vehicle (400 ``err.func.carpage.unknown.dashboard``). On the ZOE,
       ``cockpit`` only contains ``totalMileage`` and ``timestamp``.
   * - GET
     - ``/myr/api/v1/accounts/{account_id}/vehicles/{vin}/remotes?country={country}``
     - Returns ``[{featureId, securityProtocol: [...]}, ...]`` with door
       statuses and optional business fields (``status``, ``hvacThreshold``,
       ``internalTemperature``), e.g. feature 366 reported
       ``{"featureId": 366, "securityProtocol": ["SRP"], "status": "off",
       "hvacThreshold": 8, "internalTemperature": 41}`` on the XCB1VE at
       rest. On the ZOE, every entry reports ``securityProtocol: ["UNKNOWN"]``
       and feature 366 has no ``internalTemperature``.
   * - POST
     - ``/myr/api/v1/accounts/{account_id}/vehicles/{vin}/state?country={country}``
     - See `POST /state`_ below
   * - GET
     - ``/myr/mybrand/kyc/v1/transactions/last?country={country}``
     - Vehicle-dependent: 200 with an empty body on the HEV, 404
       (``err.func.wired.not-found``) on the XCB1VE and the ZOE
   * - GET
     - ``/ccx/garage-center/v1/vehicles/{vin}/connected-users?country={country}``
     - Returns ``{"connectedUsers": [{firstName, lastName, currentUser}]}``.
       Verified on the ZOE with the legacy JWT (see `Authentication`_).

Present in the APK but not verified live:

.. list-table::
   :header-rows: 1

   * - Method
     - Path
   * - POST
     - ``/myr/api/v1/connection``
   * - POST
     - ``/myr/api/v1/integrity/init``, ``/myr/api/v1/integrity/check``
   * - GET
     - ``/myr/api/v2/accounts/{account_id}/vehicles/{vin}/maintenance-history``
   * - GET
     - ``/myr/api/v2/accounts/{account_id}/vehicles/{vin}/upcoming-maintenance``
   * - GET
     - ``/myr/api/v1/accounts/{account_id}/vehicles/{vin}/digital-maintenance-booklet``
   * - GET
     - ``/myr/api/v1/accounts/{person_id}/vehicles/{vin}/batteries-certificates``
   * - GET
     - ``/myr/api/v2/eguides``

All of the paths above are still present in APK 6.14.2. That version also
contains the following ``apis.renault.com`` paths. They were found by string
extraction only, so the HTTP method was not determined, and they were not
verified live:

* ``/mybrand/kyc/v1/links``
* ``/mybrand/connected-vehicle/v1/vehicles/{vin}/certificates-status``
* ``/mybrand/connected-vehicle/v1/vehicles/{vin}/release-notes``
* ``/ccx/uac/v1/sessions/fcm-token`` (push-notification token registration)
* ``/s13/vkm/vk/v1/`` (virtual key base path)

POST /state
-----------

.. code-block:: json

   {
     "uidveh": [202, 345],
     "deliveryDate": "YYYY-MM-DD"
   }

* ``uidveh`` is a list of featureIds (same namespace as ``/remotes`` and
  ``applicableFeatures``) whose state is requested.
* ``deliveryDate`` is the vehicle delivery (in-service) date.
* The call is asynchronous: it returns ``200`` with an empty body, and the data
  surfaces through the app afterwards. Transient ``502`` responses
  (``errorCode 12.00.00.03``) were observed on the Renault side.
* Response blocks (per the APK): ``sohBlms`` (hybrid battery health
  ``soheRef``/``sohStatus``), ``tirePressure`` (TPMS), ``mileage``,
  ``connectedMaintenance``.
* An ``ACTIVATED`` featureId does not guarantee its block is served: on a
  tested full-EV (XCB1VE) with ``uidveh: [345, 202, 831, 820, 204]``, only
  ``mileage`` came back (no ``sohBlms``, no ``tirePressure``, no error). The
  ``mileage`` block matches the Kamereon ``/cockpit`` value and timestamp.
* The APK filters the requested ids against ``{820, 204, 831, 202, 345}``
  before calling this endpoint, so those five ids are known-accepted
  (read-only queries: no physical action is triggered).

Vehicle-level attributes
------------------------

* ``connectedStatus.remoteSecurityProtocol`` (``/connected-vehicles``) is a
  per-vehicle attribute with values ``JWT``, ``SRP`` or ``UNKNOWN``: ``JWT`` on
  the HEV, ``SRP`` on the XCB1VE, ``UNKNOWN`` on the ZOE. On an SRP-protocol
  vehicle, direct Kamereon remote commands were refused (``errorCode 6``,
  CONTACT_SRC), while the APK carries SRP-6a remote-service actions
  (``srp-initiates``, ``srp-sets``) as the alternative path.
* The three id representations coincide per vehicle, without any deviation
  (observed on the HEV and the XCB1VE): ``connectedStatus.services`` (ids as
  strings), ``applicableFeatures`` filtered to ``status: ACTIVATED``, and the
  ``/remotes`` id list. On the ZOE, ``applicableFeatures`` is absent, and
  ``services`` matches the ``/remotes`` id list. The app itself reads
  ``services`` only (a plain presence check); the ACTIVATED filtering is done
  server-side.
* ``connectedStatus.privacyModeStatus`` / ``privacyModeLastUpdate`` (observed
  under ``connectedStatus`` and reported under ``vehicleDetails`` on another
  vehicle) reflect the MyRenault privacy mode. When active, it cuts data
  reporting and is an explicit cause of unavailability, distinct from a
  contract or account/link issue.

featureIds
----------

``featureId`` values are shared by three sources that use the same namespace:
``applicableFeatures`` (``/connected-vehicles``), ``featureId``
(``/remotes``) and ``uidveh`` (``POST /state``).

Ids explicitly interpreted by the app 6.13.4 (evidence: jadx decompilation):

.. list-table::
   :header-rows: 1

   * - featureId
     - Meaning
   * - 97
     - Horn and lights (``POST /actions/horn-lights``, orders
       ``/RHL/Start/HornOnly|LightOnly|HornLight``)
   * - 202
     - Mileage (``POST /state`` response block ``mileage``)
   * - 345
     - Hybrid battery health, SOH (``POST /state`` response block ``sohBlms``)
   * - 299
     - Instant charge (legacy generation)
   * - 362
     - Charging spots on the map
   * - 366
     - Instant HVAC (``POST /actions/hvac-start``)
   * - 701
     - V2G (vehicle-to-grid)
   * - 740
     - V2L (vehicle-to-load)
   * - 743
     - Plug & Charge
   * - 801
     - Virtual key ONBOARD pairing
   * - 806
     - Instant HVAC with adjustable temperature (requires 806 + 366)
   * - 820 (+ 204)
     - Connected maintenance / vehicle alerts
   * - 831
     - Tyre pressure (TPMS)
   * - 833
     - Pause/resume instant charging
   * - 952 / 953
     - EV programmes (variants, role not discriminated)
   * - 954
     - HVAC preconditioning (EV programmes)
   * - 955
     - Scheduled charge programmes + preconditioning; V2G section visibility
   * - 2021
     - Cloud lock-status (``POST /actions/lock-unlock``, orders
       ``/RLU/Lock``, ``/RLU/Unlock``, target ``doors_hatch``)
   * - 3205
     - V2G charge history

Ids relayed by the app without interpretation (server-side semantics only):
``4, 12, 21, 107, 200, 315, 323, 344, 419, 724, 729, 730, 748, 815, 818, 826,
830, 846, 847, 912, 920, 927, 966, 967, 2852, 3302, 1710040``. Observed on the
tested HEV (28 ids ``ACTIVATED``) and full-EV (21 ids, adding ``315``, ``344``
and ``724``); none of them has a literal reference in the APK 6.13.4, so their
semantics live server-side only.

The ZOE reports 12 ids in ``services`` and ``/remotes``: ``202, 288, 311, 315,
317, 319, 322, 362, 366, 408, 723, 725``. The ids ``288, 311, 317, 319, 322,
408, 723, 725`` appear in neither list above.

Discovery method
----------------

* Android APK 6.13.4 (XAPK from apkcombo, sha256
  ``15e02d50c0b06f55b0c1f4a3824449f21ca2530124d3c6d74834d7956aef552c``),
  decompiled with jadx 1.5.6. The app is native Kotlin plus a Flutter module
  and Cordova (ScanMy only); it is not React Native.
* iOS 6.13.1 traffic captured through a TLS proxy to confirm live hosts,
  paths, headers and payloads.
* Android APK 6.14.2 (XAPK from apkcombo, sha256
  ``6681863aa4074a035451bf9024c6f48b3a2bdc9e730020466e0a74ab423dcc55``),
  checked by string extraction from the dex files (no decompilation).
* Direct read-only HTTP probes on the tested vehicles, cross-checked with the
  app's own traffic for the HEV.
