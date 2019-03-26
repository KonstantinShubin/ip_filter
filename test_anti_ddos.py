import anti_ddos as anti
import time


# unit tests on pytest module
def test_check_ip_switch_off():
    anti.check_ip_switch = False
    assert anti.check_ip("192.0.0.0") == (anti.OK, "Website is currently disabled")


def test_check_ip_switch_on():
    anti.check_ip_switch = True
    assert anti.check_ip("192.0.0.1") == (anti.OK, "Welcome")


def test_adding_new_ip():
    anti.check_ip("192.0.0.2")
    assert time.time() + 1 >= anti.ip_filter_table["192.0.0.2"]["TIME"]
    assert time.time() - 1 <= anti.ip_filter_table["192.0.0.2"]["TIME"]
