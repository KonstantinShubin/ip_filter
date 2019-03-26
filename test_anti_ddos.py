import anti_ddos
import time


# unit tests on pytest module
def test_check_ip_switch_off():
    anti_ddos.check_ip_switch = False
    assert anti_ddos.check_ip("192.0.0.0") == (anti_ddos.OK, "")


def test_check_ip_switch_on():
    anti_ddos.check_ip_switch = True
    assert anti_ddos.check_ip("192.0.0.1") == (anti_ddos.OK, "")


def test_adding_new_ip():
    anti_ddos.check_ip("192.0.0.2")
    assert time.time() + 1 >= anti_ddos.ip_filter_table["192.0.0.2"][0]["TIME"]
    assert time.time() - 1 <= anti_ddos.ip_filter_table["192.0.0.2"][0]["TIME"]
