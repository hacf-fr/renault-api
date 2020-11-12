"""Mock Kamereon responses."""
import json
from dataclasses import dataclass
from typing import Any

from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN


@dataclass
class MockKamereonResponse:
    """Mock Kamereon response."""

    status: int
    response: Any

    def get_body(self) -> str:
        """Get body as json string."""
        return json.dumps(self.response)


MOCK_PERSONS = MockKamereonResponse(
    status=200,
    response={
        "accounts": [
            {
                "accountId": TEST_ACCOUNT_ID,
                "accountType": "MYRENAULT",
                "accountStatus": "ACTIVE",
                "country": TEST_COUNTRY,
                "personId": TEST_PERSON_ID,
                "relationType": "OWNER",
            },
            {
                "accountId": "account-id-2",
                "externalId": "external-id-1",
                "accountType": "SFDC",
                "accountStatus": "ACTIVE",
                "country": TEST_COUNTRY,
                "personId": TEST_PERSON_ID,
                "relationType": "OWNER",
            },
        ]
    },
)
MOCK_ACCOUNTS_VEHICLES = MockKamereonResponse(
    status=200,
    response={
        "vehicleLinks": [
            {
                "brand": "RENAULT",
                "vin": TEST_VIN,
                "status": "ACTIVE",
                "linkType": "OWNER",
                "garageBrand": "RENAULT",
                "annualMileage": 16000,
                "mileage": 26464,
                "startDate": "2017-08-07",
                "createdDate": "2019-05-23T21:38:16.409008Z",
                "lastModifiedDate": "2020-11-09T08:35:37.287173Z",
                "ownershipStartDate": "2017-08-01",
                "cancellationReason": {},
                "connectedDriver": {
                    "role": "MAIN_DRIVER",
                    "createdDate": "2019-06-17T09:49:06.880627Z",
                    "lastModifiedDate": "2019-06-17T09:49:06.880627Z",
                },
                "vehicleDetails": {
                    "vin": TEST_VIN,
                    "registrationDate": "2017-08-01",
                    "firstRegistrationDate": "2017-08-01",
                    "engineType": "5AQ",
                    "engineRatio": "601",
                    "modelSCR": "ZOE",
                    "deliveryCountry": {"code": TEST_COUNTRY, "label": "FRANCE"},
                    "family": {"code": "X10", "label": "FAMILLE X10", "group": "007"},
                    "tcu": {
                        "code": "TCU0G2",
                        "label": "TCU VER 0 GEN 2",
                        "group": "E70",
                    },
                    "navigationAssistanceLevel": {
                        "code": "NAV3G5",
                        "label": "LEVEL 3 TYPE 5 NAVIGATION",
                        "group": "408",
                    },
                    "battery": {
                        "code": "BT4AR1",
                        "label": "BATTERIE BT4AR1",
                        "group": "968",
                    },
                    "radioType": {
                        "code": "RAD37A",
                        "label": "RADIO 37A",
                        "group": "425",
                    },
                    "registrationCountry": {"code": TEST_COUNTRY},
                    "brand": {"label": "RENAULT"},
                    "model": {"code": "X101VE", "label": "ZOE", "group": "971"},
                    "gearbox": {
                        "code": "BVEL",
                        "label": "BOITE A VARIATEUR ELECTRIQUE",
                        "group": "427",
                    },
                    "version": {"code": "INT MB 10R"},
                    "energy": {"code": "ELEC", "label": "ELECTRIQUE", "group": "019"},
                    "registrationNumber": "REG-NUMBER",
                    "vcd": "SYTINC/SKTPOU/SAND41/FDIU1/SSESM/MAPSUP/SSCALL/SAND88/SAND90/SQKDRO/SDIFPA/FACBA2/PRLEX1/SSRCAR/CABDO2/TCU0G2/SWALBO/EVTEC1/STANDA/X10/B10/EA2/MB/ELEC/DG/TEMP/TR4X2/RV/ABS/CAREG/LAC/VT003/CPE/RET03/SPROJA/RALU16/CEAVRH/AIRBA1/SERIE/DRA/DRAP08/HARM02/ATAR/TERQG/SFBANA/KM/DPRPN/AVREPL/SSDECA/ASRESP/RDAR02/ALEVA/CACBL2/SOP02C/CTHAB2/TRNOR/LVAVIP/LVAREL/SASURV/KTGREP/SGSCHA/APL03/ALOUCC/CMAR3P/NAV3G5/RAD37A/BVEL/AUTAUG/RNORM/ISOFIX/EQPEUR/HRGM01/SDPCLV/TLFRAN/SPRODI/SAN613/SSAPEX/GENEV1/ELC1/SANCML/PE2012/PHAS1/SAN913/045KWH/BT4AR1/VEC153/X101VE/NBT017/5AQ",  # noqa
                    "assets": [
                        {
                            "assetType": "PICTURE",
                            "renditions": [
                                {
                                    "resolutionType": "ONE_MYRENAULT_LARGE",
                                    "url": "https://3dv2.renault.com/ImageFromBookmark?configuration=SKTPOU%2FPRLEX1%2FSTANDA%2FB10%2FEA2%2FDG%2FVT003%2FRET03%2FRALU16%2FDRAP08%2FHARM02%2FTERQG%2FRDAR02%2FALEVA%2FSOP02C%2FTRNOR%2FLVAVIP%2FLVAREL%2FNAV3G5%2FRAD37A%2FSDPCLV%2FTLFRAN%2FGENEV1%2FSAN913%2FBT4AR1%2FNBT017&databaseId=1d514feb-93a6-4b45-8785-e11d2a6f1864&bookmarkSet=RSITE&bookmark=EXT_34_DESSUS&profile=HELIOS_OWNERSERVICES_LARGE",  # noqa
                                },
                                {
                                    "resolutionType": "ONE_MYRENAULT_SMALL",
                                    "url": "https://3dv2.renault.com/ImageFromBookmark?configuration=SKTPOU%2FPRLEX1%2FSTANDA%2FB10%2FEA2%2FDG%2FVT003%2FRET03%2FRALU16%2FDRAP08%2FHARM02%2FTERQG%2FRDAR02%2FALEVA%2FSOP02C%2FTRNOR%2FLVAVIP%2FLVAREL%2FNAV3G5%2FRAD37A%2FSDPCLV%2FTLFRAN%2FGENEV1%2FSAN913%2FBT4AR1%2FNBT017&databaseId=1d514feb-93a6-4b45-8785-e11d2a6f1864&bookmarkSet=RSITE&bookmark=EXT_34_DESSUS&profile=HELIOS_OWNERSERVICES_SMALL_V2",  # noqa
                                },
                            ],
                        },
                        {
                            "assetType": "PDF",
                            "assetRole": "GUIDE",
                            "title": "PDF Guide",
                            "description": "",
                            "renditions": [
                                {
                                    "url": "https://cdn.group.renault.com/ren/gb/myr/assets/x101ve/manual.pdf.asset.pdf/1558704861735.pdf"  # noqa
                                }
                            ],
                        },
                        {
                            "assetType": "URL",
                            "assetRole": "GUIDE",
                            "title": "e-guide",
                            "description": "",
                            "renditions": [
                                {"url": "http://gb.e-guide.renault.com/eng/Zoe"}
                            ],
                        },
                        {
                            "assetType": "VIDEO",
                            "assetRole": "CAR",
                            "title": "10 Fundamentals about getting the best out of your electric vehicle",  # noqa
                            "description": "",
                            "renditions": [{"url": "39r6QEKcOM4"}],
                        },
                        {
                            "assetType": "VIDEO",
                            "assetRole": "CAR",
                            "title": "Automatic Climate Control",
                            "description": "",
                            "renditions": [{"url": "Va2FnZFo_GE"}],
                        },
                        {
                            "assetType": "URL",
                            "assetRole": "CAR",
                            "title": "More videos",
                            "description": "",
                            "renditions": [
                                {"url": "https://www.youtube.com/watch?v=wfpCMkK1rKI"}
                            ],
                        },
                        {
                            "assetType": "VIDEO",
                            "assetRole": "CAR",
                            "title": "Charging the battery",
                            "description": "",
                            "renditions": [{"url": "RaEad8DjUJs"}],
                        },
                        {
                            "assetType": "VIDEO",
                            "assetRole": "CAR",
                            "title": "Charging the battery at a station with a flap",
                            "description": "",
                            "renditions": [{"url": "zJfd7fJWtr0"}],
                        },
                    ],
                    "yearsOfMaintenance": 12,
                    "connectivityTechnology": "RLINK1",
                    "easyConnectStore": False,
                    "electrical": True,
                    "rlinkStore": False,
                    "deliveryDate": "2017-08-11",
                    "retrievedFromDhs": False,
                    "engineEnergyType": "ELEC",
                    "radioCode": "0738",
                },
            }
        ],
    },
)
MOCK_QUOTA_LIMIT = MockKamereonResponse(
    status=429,
    response={
        "type": "FUNCTIONAL",
        "messages": [
            {
                "code": "err.func.wired.overloaded",
                "message": "You have reached your quota limit",
            }
        ],
        "errors": [
            {
                "errorCode": "err.func.wired.overloaded",
                "errorMessage": "You have reached your quota limit",
                "errorType": "functional",
            }
        ],
    },
)
MOCK_NOT_SUPPORTED = MockKamereonResponse(
    status=501,
    response={
        "type": "TECHNICAL",
        "messages": [
            {
                "code": "err.tech.501",
                "message": '{"errors":[{"status":"501","code":"error.internal","detail":"This feature is not technically supported by this gateway"}]}',  # noqa
            }
        ],
        "errors": [
            {
                "errorCode": "err.tech.501",
                "errorMessage": '{"errors":[{"status":"501","code":"error.internal","detail":"This feature is not technically supported by this gateway"}]}',  # noqa
            }
        ],
        "error_reference": "TECHNICAL",
    },
)
MOCK_INVALID_UPSTREAM = MockKamereonResponse(
    status=500,
    response={
        "type": "TECHNICAL",
        "messages": [
            {
                "code": "err.tech.500",
                "message": '{"errors":[{"status":"Internal Server Error","code":"500","title":"Invalid response from the upstream server (The request sent to the GDC is erroneous) ; 502 Bad Gateway"}]}',  # noqa
            }
        ],
        "errors": [
            {
                "errorCode": "err.tech.500",
                "errorMessage": '{"errors":[{"status":"Internal Server Error","code":"500","title":"Invalid response from the upstream server (The request sent to the GDC is erroneous) ; 502 Bad Gateway"}]}',  # noqa
            }
        ],
        "error_reference": "TECHNICAL",
    },
)

MOCK_VEHICLE_BATTERY_STATUS = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "Car",
            "id": TEST_VIN,
            "attributes": {
                "timestamp": "2020-11-09T07:41:49+01:00",
                "batteryLevel": 34,
                "batteryTemperature": 10,
                "batteryAutonomy": 88,
                "batteryCapacity": 0,
                "batteryAvailableEnergy": 0,
                "plugStatus": 0,
                "chargingStatus": -1.0,
            },
        }
    },
)
MOCK_VEHICLE_CHARGE_MODE_INVALID_UPSTREAM = MOCK_INVALID_UPSTREAM
MOCK_VEHICLE_CHARGE_HISTORY_EMPTY = MockKamereonResponse(
    status=200,
    response={
        "data": {"type": "Car", "id": TEST_VIN, "attributes": {"chargeSummaries": []}}
    },
)
MOCK_VEHICLE_CHARGES_EMPTY = MockKamereonResponse(
    status=200,
    response={"data": {"type": "Car", "id": TEST_VIN, "attributes": {"charges": []}}},
)
MOCK_VEHICLE_CHARGING_SETTINGS_INVALID_UPSTREAM = MOCK_INVALID_UPSTREAM
MOCK_VEHICLE_COCKPIT = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "Car",
            "id": TEST_VIN,
            "attributes": {"totalMileage": 49011.09},
        }
    },
)
MOCK_VEHICLE_HVAC_STATUS = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "Car",
            "id": TEST_VIN,
            "attributes": {"hvacStatus": "off", "externalTemperature": 5.0},
        }
    },
)
MOCK_VEHICLE_HVAC_HISTORY_INVALID_UPSTREAM = MOCK_INVALID_UPSTREAM
MOCK_VEHICLE_HVAC_SESSIONS_INVALID_UPSTREAM = MOCK_INVALID_UPSTREAM
MOCK_VEHICLE_LOCATION_NOT_SUPPORTED = MOCK_NOT_SUPPORTED
MOCK_VEHICLE_LOCK_STATUS_NOT_SUPPORTED = MOCK_NOT_SUPPORTED
MOCK_VEHICLE_NOTIFICATION_SETTINGS_INVALID_UPSTREAM = MOCK_INVALID_UPSTREAM

MOCK_VEHICLEACTIONS_CHARGING_START = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "ChargingStart",
            "id": "guid",
            "attributes": {"action": "start"},
        }
    },
)
MOCK_VEHICLEACTIONS_CHARGE_MODE = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "ChargeMode",
            "id": "guid",
            "attributes": {"action": "schedule_mode"},
        }
    },
)
MOCK_VEHICLEACTIONS_CHARGE_SCHEDULE = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "ChargeSchedule",
            "id": "guid",
            "attributes": {"schedules": []},
        }
    },
)
MOCK_VEHICLEACTIONS_HVAC_START = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "HvacStart",
            "id": "guid",
            "attributes": {
                "action": "start",
                "startDateTime": "2020-11-10T23:00:00Z",
                "targetTemperature": 22.0,
            },
        }
    },
)
MOCK_VEHICLEACTIONS_HVAC_START_CANCEL = MockKamereonResponse(
    status=200,
    response={
        "data": {
            "type": "HvacStart",
            "id": "guid",
            "attributes": {"action": "cancel"},
        }
    },
)
MOCK_VEHICLEACTIONS_HVAC_START_INVALID_DATE = MockKamereonResponse(
    status=400,
    response={
        "type": "FUNCTIONAL",
        "messages": [
            {
                "code": "err.func.400",
                "message": '{"errors":[{"status":"400","code":"Future","detail":"must be a future date","source":{"pointer":"/data/attributes/startDateTime"}}]}',  # noqa
            }
        ],
        "errors": [
            {
                "errorCode": "err.func.400",
                "errorMessage": '{"errors":[{"status":"400","code":"Future","detail":"must be a future date","source":{"pointer":"/data/attributes/startDateTime"}}]}',  # noqa
            }
        ],
        "error_reference": "FUNCTIONAL",
    },
)
