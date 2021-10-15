from abc import abstractmethod
import serial
import serial.tools.list_ports as ports
import time
from collections import namedtuple
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE


class SerialCommands:
    """Class containing serial port commands"""
    PB7200COMPort = serial.Serial()
    TEMPERATURE_M = 427.36
    TEMPERATURE_B = 35.13
    CURRENT_REV2 = 213.33
    list_temperatures = []

    def __init__(self):
        """Reads available com ports from windows"""
        PORTS = list(ports.comports())
        for p in PORTS:
            print(p)
        print("PB7200 Python Command Module v0.01")
        com_select = input("Specify COM port selection: ")

        print("Select a command to send to the PB7200 from the list:")
        print("1: Read Firmware version")
        print("2: Read lock-in 1st harmonic output")
        print("3: Read lock-in and LD0, LD1 temps")
        command_select = input("Selection: ")

        """Opens serial port with set properties"""
        self.PB7200COMPort.port = com_select
        self.PB7200COMPort.baudrate = 56000
        self.PB7200COMPort.parity = PARITY_NONE
        self.PB7200COMPort.bytesize = EIGHTBITS
        self.PB7200COMPort.stopbits = STOPBITS_ONE
        self.PB7200COMPort.rtscts = True
        self.PB7200COMPort.write_timeout = 5
        try:
            self.PB7200COMPort.open()
            print("Succeded in opening PB7200 port")
        except:
            print("Failed to open port")

    def build_tx_bytes(self, hex_list):
        """ Builds the 6 bytes to send from a hex values list"""

        sync_byte = hex_list[0]
        command_byte = hex_list[1]
        third_byte = hex_list[2]
        fourth_byte = hex_list[3]
        fifth_byte = hex_list[4]
        sixth_byte = hex_list[5]

        tx_bytes_hex = f"{sync_byte} {command_byte} {third_byte} {fourth_byte} {fifth_byte} {sixth_byte}"

        tx_byte_array = bytearray.fromhex(tx_bytes_hex)
        return tx_byte_array

    def write_serial(self, tx_bytes):
        """Function recieves tx_bytes list to send, returns rxBytes bytearray"""
        print("Writing to PB7200")
        self.PB7200COMPort.reset_input_buffer()
        # rxBytes = []
        # send the character to the device
        self.PB7200COMPort.write(tx_bytes)

        # let's wait one second before reading output (let's give device time to answer)
        print("Awaiting response")
        time.sleep(1)

        print("Bytes in buffer to read: ")
        print(self.PB7200COMPort.in_waiting)

        while self.PB7200COMPort.in_waiting > 0:
            print("Reading Bytes")
            rx_bytes = self.PB7200COMPort.read(10)

            print(rx_bytes)

        return rx_bytes

    def close_port(self):
        """Closes com port at end of program"""
        self.PB7200COMPort.close()

    def convert_hex_and_split_bytes(self, unsplit):
        """Converts bytes to hex list"""
        version_hex = unsplit.hex()

        char_count = 2

        split_hex_version = [version_hex[i:i+char_count]
                             for i in range(0, len(version_hex), char_count)]

        print(split_hex_version)

        return split_hex_version

    def split_hex(self, unsplit):
        """splits hex string every 2 chars to list"""
        char_count = 2

        split_hex_version = [unsplit[i:i+char_count]
                             for i in range(0, len(unsplit), char_count)]

        print(split_hex_version)

        return split_hex_version

    def convert_hex_to_dec(self, raw_bytes):
        """converts list of 10 hex bytes to decimal returns decimal list"""

        converted_version_list = []

        for i in range(10):
            converted_version_list.append(int(raw_bytes[i], 16))

        return converted_version_list

    def convert_hex_to_dec_values(self, hex_value):
        """converts individual values to decimal"""

        dec_value = int(hex_value, 16)

        return dec_value

    def read_version(self):
        """reads firmware version installed"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("C6")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        version_bytes = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(version_bytes)

        converted_list = self.convert_hex_to_dec(split_hex_list)

        print(converted_list)

        version_first_half = str(converted_list[6])

        version_second_half = str(converted_list[8])

        print("Version number is: " + version_first_half +
              "." + version_second_half)

    def read_lockin_1st_harmonic(self):
        """reads lock-in 1st harmonic"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("50")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_bytes = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(lockin_bytes)

        lock_in_1st_msb = split_hex_list[2]

        lock_in_2nd_msb = split_hex_list[3]

        lock_in_3rd_msb = split_hex_list[4]

        lock_in_lsb = split_hex_list[5]

        lock_in_lsb_full_decimal = int(lock_in_lsb, 16)

        lock_in_msb_full = f"{lock_in_1st_msb}{lock_in_2nd_msb}{lock_in_3rd_msb}"

        lock_in_msb_full_decimal = int(lock_in_msb_full, 16)

        lock_in_full_decimal = f"{lock_in_msb_full_decimal}.{lock_in_lsb_full_decimal}"

        print(lock_in_full_decimal)

    def read_lockin_1st_and_both_temps(self):
        """Reads lock-in 1st harmonic, LD0 temp, LD1 temp"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("60")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_and_temps_bytes = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(
            lockin_and_temps_bytes)

        lockin_values = namedtuple('lockin_values', [
            'lock_in_1st_msb_hex', 'lock_in_2nd_msb_hex',
            'lock_in_3rd_msb_hex', 'lock_in_lsb_hex'])

        lockin_values = lockin_values(split_hex_list[2], split_hex_list[3],
                                      split_hex_list[4], int(split_hex_list[5]))

        temp_values = namedtuple('temp_values', [
            'temp_1_msb_hex', 'temp_1_lsb_hex', 'temp_2_msb_hex', 'temp_2_lsb_hex'])

        temp_values = temp_values(
            split_hex_list[6], split_hex_list[7], split_hex_list[8], split_hex_list[9])

        lock_in_1st_msb_hex = split_hex_list[2]

        lock_in_2nd_msb_hex = split_hex_list[3]

        lock_in_3rd_msb_hex = split_hex_list[4]

        lock_in_lsb_hex = split_hex_list[5]

        temp_1_msb_hex = split_hex_list[6]

        temp_1_lsb_hex = split_hex_list[7]

        temp_2_msb_hex = split_hex_list[8]

        temp_2_lsb_hex = split_hex_list[9]

        lock_in_lsb_full_decimal = int(lock_in_lsb_hex, 16)

        lock_in_msb_full_test = f"{lockin_values.lock_in_1st_msb_hex}{lockin_values.lock_in_2nd_msb_hex}{lockin_values.lock_in_3rd_msb_hex}"

        lock_in_msb_full = f"{lock_in_1st_msb_hex}{lock_in_2nd_msb_hex}{lock_in_3rd_msb_hex}"

        lock_in_msb_full_decimal = int(lock_in_msb_full, 16)

        lock_in_full_decimal = f"{lock_in_msb_full_decimal}.{lock_in_lsb_full_decimal}"

        # laser 1

        temp_1_msb_decimal = self.convert_hex_to_dec_values(temp_1_msb_hex)

        temp_1_msb_decimal_float = float(temp_1_msb_decimal)

        temp_1_lsb_decimal = self.convert_hex_to_dec_values(temp_1_lsb_hex)

        temp_1_lsb_decimal_float = float(temp_1_lsb_decimal)

        temp_1_full_decimal_unscaled = (
            (((((2**8) * temp_1_msb_decimal_float)+temp_1_lsb_decimal_float)/self.TEMPERATURE_M)) - self.TEMPERATURE_B)

        # laser 2

        temp_2_msb_decimal = self.convert_hex_to_dec_values(temp_2_msb_hex)

        temp_2_msb_decimal_float = float(temp_2_msb_decimal)

        temp_2_lsb_decimal = self.convert_hex_to_dec_values(temp_2_lsb_hex)

        temp_2_lsb_decimal_float = float(temp_2_lsb_decimal)

        temp_2_full_decimal_unscaled = (
            (((((2**8) * temp_2_msb_decimal_float)+temp_2_lsb_decimal_float)/self.TEMPERATURE_M)) - self.TEMPERATURE_B)

        print(f"Lock in output: {lock_in_full_decimal}")
        print(f"Laser 1 temp: {temp_1_full_decimal_unscaled}")
        print(f"Laser 2 temp: {temp_2_full_decimal_unscaled}")

    def fan_on_high(self):
        """Turns the fan on to high setting"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("C4")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("01")
        hex_list.append("01")

        tx_bytes = self.build_tx_bytes(hex_list)

        print("Turning fan on....")

        fan_state_and_speed_bytes = self.write_serial(tx_bytes)

        fan_state_and_speed_hex = self.convert_hex_and_split_bytes(
            fan_state_and_speed_bytes)

        fan_state_and_speed_decimal = self.convert_hex_to_dec(
            fan_state_and_speed_hex)

        fan_state_decimal = fan_state_and_speed_decimal[8]

        fan_speed_decimal = fan_state_and_speed_decimal[9]

        print(
            f"Fan state is : {fan_state_decimal} and speed is: {fan_speed_decimal}")

    def fan_off(self):
        """Turns the fan off"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("C4")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        print("Turning fan off....")

        fan_state_and_speed_bytes = self.write_serial(tx_bytes)

        fan_state_and_speed_hex = self.convert_hex_and_split_bytes(
            fan_state_and_speed_bytes)

        fan_state_and_speed_decimal = self.convert_hex_to_dec(
            fan_state_and_speed_hex)

        fan_state_decimal = fan_state_and_speed_decimal[8]

        fan_speed_decimal = fan_state_and_speed_decimal[9]

        print(
            f"Fan state is : {fan_state_decimal} and speed is: {fan_speed_decimal}")

    def read_temp_LD0(self):
        """Reads the LD0 temperature"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("20")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_and_temps_bytes = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(
            lockin_and_temps_bytes)

        temp_1_msb_hex = split_hex_list[6]

        temp_1_lsb_hex = split_hex_list[7]

        # laser 1

        temp_1_msb_decimal = self.convert_hex_to_dec_values(temp_1_msb_hex)

        temp_1_msb_decimal_float = float(temp_1_msb_decimal)

        temp_1_lsb_decimal = self.convert_hex_to_dec_values(temp_1_lsb_hex)

        temp_1_lsb_decimal_float = float(temp_1_lsb_decimal)

        temp_1_full_decimal_unscaled = (
            (((((2**8) * temp_1_msb_decimal_float)+temp_1_lsb_decimal_float)/427.36)) - 35.13)

        print(f"Laser 1 temp: {temp_1_full_decimal_unscaled}")

    def read_temp_LD1(self):
        """Reads the LD1 temp"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("20")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        echo_temps = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(echo_temps)

        temp_2_msb_hex = split_hex_list[6]

        temp_2_lsb_hex = split_hex_list[7]

        # laser 1

        temp_2_msb_decimal = self.convert_hex_to_dec_values(temp_2_msb_hex)

        temp_2_msb_decimal_float = float(temp_2_msb_decimal)

        temp_2_lsb_decimal = self.convert_hex_to_dec_values(temp_2_lsb_hex)

        temp_2_lsb_decimal_float = float(temp_2_lsb_decimal)

        temp_2_full_decimal_unscaled = (
            (((((2**8) * temp_2_msb_decimal_float)+temp_2_lsb_decimal_float)/self.TEMPERATURE_M)) - self.TEMPERATURE_B)

        print(f"Laser 2 temp: {temp_2_full_decimal_unscaled}")

    def set_LD0_Temperature(self):
        """Sets the LD0 temperature"""

        TEST_TEMP = 25

        temp_scaled = int((TEST_TEMP + self.TEMPERATURE_B)*self.TEMPERATURE_M)

        temp_hex = hex(temp_scaled)

        n = 2

        split_hex_list = [temp_hex[i:i+n]
                          for i in range(0, len(temp_hex), n)]

        temp_msb = str(split_hex_list[1])

        temp_lsb = str(split_hex_list[2])

        hex_list = []
        hex_list.append("AA")
        hex_list.append("10")
        hex_list.append(temp_msb)
        hex_list.append(temp_lsb)
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_and_temps_bytes = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(
            lockin_and_temps_bytes)

        temp_1_msb_hex = split_hex_list[6]

        temp_1_lsb_hex = split_hex_list[7]

        # laser 1

        temp_1_msb_decimal = self.convert_hex_to_dec_values(temp_1_msb_hex)

        temp_1_msb_decimal_float = float(temp_1_msb_decimal)

        temp_1_lsb_decimal = self.convert_hex_to_dec_values(temp_1_lsb_hex)

        temp_1_lsb_decimal_float = float(temp_1_lsb_decimal)

        temp_1_full_decimal_unscaled = (
            (((((2**8) * temp_1_msb_decimal_float)+temp_1_lsb_decimal_float)/self.TEMPERATURE_M)) - self.TEMPERATURE_B)

        print(f"Laser 1 temp: {temp_1_full_decimal_unscaled}")

    def set_LD1_Temperature(self):
        """Sets the LD0 temperature"""

        TEST_TEMP = 25

        temp_scaled = int((TEST_TEMP + self.TEMPERATURE_B)*self.TEMPERATURE_M)

        temp_hex = hex(temp_scaled)

        n = 2

        split_hex_list = [temp_hex[i:i+n]
                          for i in range(0, len(temp_hex), n)]

        temp_msb = str(split_hex_list[1])

        temp_lsb = str(split_hex_list[2])

        hex_list = []
        hex_list.append("AA")
        hex_list.append("11")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append(temp_msb)
        hex_list.append(temp_lsb)

        tx_bytes = self.build_tx_bytes(hex_list)

        echo_temps = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(echo_temps)

        temp_2_msb_hex = split_hex_list[8]

        temp_2_lsb_hex = split_hex_list[9]

        # laser 2

        temp_2_msb_decimal = self.convert_hex_to_dec_values(temp_2_msb_hex)

        temp_2_msb_decimal_float = float(temp_2_msb_decimal)

        temp_2_lsb_decimal = self.convert_hex_to_dec_values(temp_2_lsb_hex)

        temp_2_lsb_decimal_float = float(temp_2_lsb_decimal)

        temp_2_full_decimal_unscaled = (
            (((((2**8) * temp_2_msb_decimal_float)+temp_2_lsb_decimal_float)/self.TEMPERATURE_M)) - self.TEMPERATURE_B)

        print(f"Laser 1 temp: {temp_2_full_decimal_unscaled}")

    def set_LD0_Power(self):
        """Sets the LD0 power"""

        TEST_CURRENT = 100

        temp_scaled = int(TEST_CURRENT * self.CURRENT_REV2)

        temp_hex = hex(temp_scaled)

        n = 2

        split_hex_list = [temp_hex[i:i+n]
                          for i in range(0, len(temp_hex), n)]

        current_msb = str(split_hex_list[1])

        current_lsb = str(split_hex_list[2])

        hex_list = []
        hex_list.append("AA")
        hex_list.append("80")
        hex_list.append(current_msb)
        hex_list.append(current_lsb)
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        echo_current = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(echo_current)

        current_1_msb_hex = split_hex_list[6]

        current_1_lsb_hex = split_hex_list[7]

        # laser 1

        current_1_msb_decimal = self.convert_hex_to_dec_values(
            current_1_msb_hex)

        current_1_msb_decimal_float = float(current_1_msb_decimal)

        current_1_lsb_decimal = self.convert_hex_to_dec_values(
            current_1_lsb_hex)

        current_1_lsb_decimal_float = float(current_1_lsb_decimal)

        current_1_full_decimal_unscaled = (
            (((2**8) * current_1_msb_decimal_float)+current_1_lsb_decimal_float)/self.CURRENT_REV2)

        print(current_1_full_decimal_unscaled)

    def set_LD1_Power(self):
        """Sets the LD1 power"""

        TEST_CURRENT = 100

        temp_scaled = int(TEST_CURRENT * self.CURRENT_REV2)

        temp_hex = hex(temp_scaled)

        n = 2

        split_hex_list = [temp_hex[i:i+n]
                          for i in range(0, len(temp_hex), n)]

        current_msb = str(split_hex_list[1])

        current_lsb = str(split_hex_list[2])

        hex_list = []
        hex_list.append("AA")
        hex_list.append("80")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append(current_msb)
        hex_list.append(current_lsb)

        tx_bytes = self.build_tx_bytes(hex_list)

        echo_current = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(echo_current)

        current_2_msb_hex = split_hex_list[8]

        current_2_lsb_hex = split_hex_list[9]

        # laser 1

        current_2_msb_decimal = self.convert_hex_to_dec_values(
            current_2_msb_hex)

        current_2_msb_decimal_float = float(current_2_msb_decimal)

        current_2_lsb_decimal = self.convert_hex_to_dec_values(
            current_2_lsb_hex)

        current_2_lsb_decimal_float = float(current_2_lsb_decimal)

        current_2_full_decimal_unscaled = (
            (((2**8) * current_2_msb_decimal_float)+current_2_lsb_decimal_float)/self.CURRENT_REV2)

        print(current_2_full_decimal_unscaled)

    def PCS_enable(self):
        """Enables the PCS"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("A0")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        PCS_enable_command = self.write_serial(tx_bytes)

        print(PCS_enable_command)

    def PCS_disable(self):
        """Disables the PCS"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("A1")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        PCS_disable_command = self.write_serial(tx_bytes)

        print(PCS_disable_command)

    def TEC_enable(self):
        """Enables the TEC"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("90")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        TEC_enable_comm = self.write_serial(tx_bytes)

        print(TEC_enable_comm)

    def TEC_disable(self):
        """Disables the TEC"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("91")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        TEC_disable_comm = self.write_serial(tx_bytes)

        print(TEC_disable_comm)

    def set_lockin_Timeconstant(self):
        """Sets the lockin time constant"""

        TIME_CONSTANT = 100

        time_scaled = int(TIME_CONSTANT / 3)

        time_hex = hex(time_scaled)

        split_hex_list = self.split_hex(time_hex)

        time_msb = str(split_hex_list[1])

        time_lsb = str(split_hex_list[2])

        hex_list = []
        hex_list.append("AA")
        hex_list.append("CB")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append(time_msb)
        hex_list.append(time_lsb)

        tx_bytes = self.build_tx_bytes(hex_list)

        echo_time = self.write_serial(tx_bytes)

        split_hex_list = self.convert_hex_and_split_bytes(echo_time)

        time_msb_hex = split_hex_list[8]

        time_lsb_hex = split_hex_list[9]

        time_msb_decimal = self.convert_hex_to_dec_values(time_msb_hex)

        time_msb_decimal_float = float(time_msb_decimal)

        time_lsb_decimal = self.convert_hex_to_dec_values(time_lsb_hex)

        time_lsb_decimal_float = float(time_lsb_decimal)

        time_full_decimal_unscaled = (
            (((2**8) * time_msb_decimal_float)+time_lsb_decimal_float)*3)

        print(f"Lock in time constants: {time_full_decimal_unscaled}")

    def set_lockin_gain(self):
        """Sets the lockin gain"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("CE")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("01")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_gain_bytes = self.write_serial(tx_bytes)

        lockin_gain_hex = lockin_gain_bytes.hex()

        lockin_gain_dec = self.convert_hex_to_dec_values(lockin_gain_hex)

        print(f"Lockin gain set to: {lockin_gain_dec}")

    def lockin_enable(self):
        """Enables Lock-in"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("C7")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("01")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_enable_comm = self.write_serial(tx_bytes)

        lockin_enable_hex = lockin_enable_comm.hex()

        lockin_enable_dec = self.convert_hex_to_dec_values(lockin_enable_hex)

        print(f"Lockin enable set to: {lockin_enable_dec}")

    def lockin_disable(self):
        """Disables Lock-in"""

        hex_list = []
        hex_list.append("AA")
        hex_list.append("C7")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")
        hex_list.append("00")

        tx_bytes = self.build_tx_bytes(hex_list)

        lockin_disable_comm = self.write_serial(tx_bytes)

        lockin_disable_hex = lockin_disable_comm.hex()

        lockin_disable_dec = self.convert_hex_to_dec_values(lockin_disable_hex)

        print(f"Lockin enable set to: {lockin_disable_dec}")

    def dwell(self):
        """Runs the dwell operation mode in the future"""
        self.set_LD0_Temperature()
        self.set_LD1_Temperature()
        self.fan_on_high()
