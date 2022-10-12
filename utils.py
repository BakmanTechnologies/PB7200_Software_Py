import json
import os
from cal_data import CalData
import matplotlib.pyplot as plt
import csv
from serial_commands_PB7300 import SerialCommands
import hashlib

fieldnames_dwell = ["Time", "Power"]
fieldnames_scan = ["Frequency", "Power"]
fieldnames_scanpm = ["Frequency", "First Harmonic", "Second Harmonic"]

serial_commands_class = SerialCommands()


def read_json_from_file():
    """Opens local path floder calibration and sorts them by name"""

    jsonlist = os.listdir("calibration")

    jsonlist.sort()

    if len(jsonlist) == 0:
        print("Calibration directory empty")
        recent_file_selection = "0"
    else:
        print(len(jsonlist))
        recent_file_selection = jsonlist[-1]
        print(recent_file_selection)

    if os.path.exists(f"calibration/{recent_file_selection}"):
        print("File exists.. Opening")
        with open(f"calibration/{recent_file_selection}") as json_file:
            jsondata = json.load(json_file)
        # print(jsondata["CalibrationTime"])

    else:
        print("No calibration file exists, must read EEPROM")
        # TODO: Make it create json from eeprom to initialize cal_data

    cal_data = CalData(jsondata)

    return cal_data


def get_json_string():
    """Obtains string of the JSON calibration file in the EEPROM"""

    numlist = []
    string_json = ""
    for i in range(4000):
        numlist.append(serial_commands_class.read_eeprom(i))
        if numlist[i] == "ÿ":
            break
        if i > 2:
            string_json += numlist[i]
    json = string_json

    return json


def sha1_and_string_from_json(json_string):
    """Receives json string from EEPROM, SHA1 string and boolean
    result from SHA1 comparison"""
    print(json_string)
    # Separates SHA1 from the json string,
    # calculates new SHA1 from read json and compares the two
    split2 = json_string.split("{", 1)
    sha1_from_eeprom = split2[0]
    json_string_cut = "{" + split2[1]
    json_string_cut_bytes = bytes(str(json_string_cut).encode("ascii"))
    sha1_calculate = hashlib.sha1(json_string_cut_bytes).hexdigest()
    sha1_calculate_cap = str.upper(sha1_calculate)

    return sha1_from_eeprom, sha1_calculate_cap, json_string_cut


def check_SHA1(SHA1_from_EEPROM, SHA1_calculated):
    is_SHA1_ok = False
    if SHA1_from_EEPROM == SHA1_calculated:
        is_SHA1_ok = True
        print("SHA1 is valid")
    return is_SHA1_ok


def save_json_to_file(json_string, SHA1_calculated):
    with open(f"calibration/{SHA1_calculated}.json", 'w') as outfile:
        outfile.write(json_string)


def read_json_from_eeprom():
    """Reads json from eeprom saves to /calibration"""

    json_string = get_json_string()

    SHA1_from_EEPROM, SHA1_calculated, json_string_cut = sha1_and_string_from_json(json_string)

    check_SHA1(SHA1_from_EEPROM, SHA1_calculated)

    save_json_to_file(json_string_cut, SHA1_calculated)


def create_dir():
    dir_list = os.listdir()

    if "calibration" and "data" in dir_list:
        pass
    else:
        os.mkdir("calibration")
        os.mkdir("data")


def simple_graph(x, y):
    """Outputs a simple graph at the of a scan or dwell"""

    plt.plot(x, y)

    plt.style.use('fivethirtyeight')
    plt.yscale('log')

    plt.title('Title')
    plt.xlabel('Time')
    plt.ylabel('Power')

    plt.axis([x[0], x[-1], 10e-2, 10e8])
    plt.show()


def create_csv_file(scantime):
    """Creates a file with the scantime at start of dwell"""

    with open(f"data/dwelldata_{scantime}.csv", 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_dwell)
        csv_writer.writeheader()

    csv_file.close()


def save_to_csv(info, scantime):
    """Saves to file created for dwell,
     takes a dictionary info with values to save"""

    with open(f"data/dwelldata_{scantime}.csv", 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_dwell)
        csv_writer.writerow(info)

    csv_file.close()


def create_csv_file_scan(scantime):
    """Creates a file with the scantime at start of a scan"""

    with open(f"data/dwelldata_{scantime}.csv", 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_scan)
        csv_writer.writeheader()

    csv_file.close()


def create_csv_file_scanpm(scantime):
    """Creates a file with the scantime
     at start of a phase modulated scan"""

    with open(f"data/dwelldata_{scantime}.csv", 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_scanpm)
        csv_writer.writeheader()

    csv_file.close()


def save_to_csv_scan(info, scantime):
    """Saves to file created for scan,
     takes a dictionary info with values to save"""

    with open(f"data/dwelldata_{scantime}.csv", 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_scan)
        csv_writer.writerow(info)

    csv_file.close()


def save_to_csv_scanpm(info, scantime):
    """Saves to file created for scan,
     takes a dictionary info with values to save"""

    with open(f"data/dwelldata_{scantime}.csv", 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames_scanpm)
        csv_writer.writerow(info)

    csv_file.close()

