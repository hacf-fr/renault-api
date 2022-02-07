import srp
import os
import time

# As per PySRP sample: Consider enabling RFC5054 compatibility for interoperation with non pysrp SRP-6a implementations
srp.rfc5054_enable()


class AuthenticationFailed(Exception):
    pass


# UserID is presumably gigya_person_id that can be found if execute "renault-api settings". The same ID is sent at the srp-set endpoint by android app, so probably that the right one
UserID = "aaaaa11-2222-3333-4444-abcabcabc123"
# AccountId is what returned if execute "renault-api accounts"
AccountId = "eeeaa11-2222-3333-4444-abcabcabc000"
# PinCode is the password used in SRP, and the only password that is requested in android in this flow is the Pin code.
PinCode = "0000"
# vin of the car
vin = "X7LHABC1234567890"

usr = srp.User(UserID, PinCode)

uname, A = usr.start_authentication()
ParsedID = ""
ParsedA = ""
ParsedB = ""
ParsedSalt = ""
ParsedResponse = ""
M = b""


def res_state():
    print("")
    print("========================")
    print("1. RES-STATE")
    print("========================")
    strExec = (
        'renault-api --debug http get "/commerce/v1/accounts/'
        + AccountId
        + "/kamereon/kca/car-adapter/v1/cars/"
        + vin
        + '/res-state?country=RU"'
    )
    stream = os.popen(strExec)


def srp_set():
    ParseList1 = []
    ParseList2 = []
    global ParsedID
    print("")
    print("========================")
    print("2. SRP-SET ")
    print("========================")

    strExec = (
        "renault-api --debug http post '/commerce/v1/accounts/"
        + AccountId
        + "/kamereon/kca/car-adapter/v1/cars/"
        + vin
        + '/actions/srp-sets?country=RU\' \'{"data":{"type":"SrpSets","attributes":{"a":"'
        + A.hex().upper()
        + '","i":"'
        + UserID
        + "\"}}}'"
    )

    stream = os.popen(strExec)
    # output = stream.read()
    time.sleep(5)

    output = " ".join(stream)
    output = output.replace('"', "")
    output = output.replace("'", "")
    output = output.replace(" ", "")

    ParseList1 = output.split("SrpSets,id:")

    if len(ParseList1) < 2:
        print("")
        print("Smth went wrong, that's what I sent:")
        print(strExec)
        print("Received:")
        print(output)
        print("")

    ParseList2 = ParseList1[1].split(",attributes")
    ParsedID = ParseList2[0]
    print("")
    print("")
    print("Parsed Notif ID: " + ParsedID)
    print("waiting 10s for server to prepare response")
    time.sleep(10)


def kmr_first():
    ParseList1 = []
    ParseList2 = []
    global ParsedID
    global ParsedB
    global ParsedSalt
    global M
    print("========================")
    print("3. KMR Notification " + ParsedID)
    print("========================")

    strExec = (
        'renault-api --debug http get "/commerce/v1/persons/'
        + UserID
        + "/notifications/kmr?&notificationId="
        + ParsedID
        + '" 2>&1'
    )

    time.sleep(1)
    stream = os.popen(strExec)
    output = " ".join(stream)

    print("")
    print("OutPut:")
    print(output)
    print("")

    output = output.replace('"', "")
    output = output.replace("'", "")
    output = output.replace(" ", "")

    ParseList1 = output.split("loginB:")
    if (len(ParseList1)) < 2:
        print("Failed to parse loginB")
        return 1
        exit

    ParseList2 = ParseList1[1].split(",loginSalt:")
    ParsedB = ParseList2[0]
    ParseList3 = ParseList2[1].split("}")
    ParsedSalt = ParseList3[0]
    print("")
    print("Parsed B: " + ParsedB)
    print("Parsed Salt: " + ParsedSalt)

    s = bytes.fromhex(ParsedSalt.lower())
    B = bytes.fromhex(ParsedB.lower())

    print("Calculated M:")
    M = usr.process_challenge(s, B)

    print(M.hex().upper())
    if M is None:
        raise AuthenticationFailed()


def engine_start():
    ParseList1 = []
    ParseList2 = []
    global ParsedID
    global M
    print("========================")
    print("4. ENGINE START")
    print("========================")
    print("Will try to send M = " + M.hex().upper())

    strExec = (
        "renault-api --debug http post '/commerce/v1/accounts/"
        + AccountId
        + "/kamereon/kca/car-adapter/v1/cars/"
        + vin
        + '/actions/engine-start?country=RU\' \'{"data":{"type":"EngineStart","attributes":{"action":"start","srp":"'
        + M.hex().upper()
        + "\"}}}'"
    )

    stream = os.popen(strExec)
    time.sleep(1)
    output = " ".join(stream)
    output = output.replace('"', "")
    output = output.replace("'", "")
    output = output.replace(" ", "")

    ParseList1 = output.split("EngineStart,id:")
    ParseList2 = ParseList1[1].split(",attributes")
    ParsedID = ParseList2[0]
    print("")
    print("Sent request: " + strExec)
    print("")
    print("Parsed Notif ID: " + ParsedID)
    print("waiting 10s for server to prepare response")
    time.sleep(10)


def kmr_second():
    ParseList1 = []
    ParseList2 = []
    global ParsedID
    global M
    print("========================")
    print("5. KMR Notification " + ParsedID)
    print("========================")

    strExec = (
        'renault-api --debug http get "/commerce/v1/persons/'
        + UserID
        + "/notifications/kmr?&notificationId="
        + ParsedID
        + '" 2>&1'
    )

    time.sleep(5)
    stream = os.popen(strExec)

    output = " ".join(stream)
    output = output.replace('"', "")
    output = output.replace("'", "")
    output = output.replace(" ", "")

    ParseList1 = output.split("actionType:")
    if len(ParseList1) < 2:
        return 1
        exit
    ParseList2 = ParseList1[1].split(",commandResponse:")
    ParsedResponse = ParseList2[0]
    print("")
    print("Parsed Response: " + ParsedResponse)
    print(output)


res_state()
srp_set()
for x in range(1, 10):
    if kmr_first() != 1:
        break

engine_start()
for x in range(1, 10):
    if kmr_second() != 1:
        break


# Server => Client: HAMK
# usr.verify_session(HAMK)

# At this point the authentication process is complete.

# assert usr.authenticated()
# assert svr.authenticated()
