import anti_ddos as anti
import time

anti.check_ip_switch = True
anti.log_time = 20  # Number in seconds in which we check for number of logins
anti.num_softban = 20  # Number of max acceptable logins for log_time seconds
anti.threshold = 100000
anti.first_time_ban = 1800  # time is seconds (1800 = 30 minutes)
anti.ban_time_coef = 1.5
anti.max_ban_time = 21600  # time in seconds (21600 = 6 hours)


# support functions
def get_time(ip):
    return anti.ip_filter_table[ip]["TIME"]


def get_num_logins(ip):
    return anti.ip_filter_table[ip]["NUM_LOGINS"]


def get_status(ip):
    return anti.ip_filter_table[ip]["STATUS"]


def get_banned_time(ip):
    return anti.ip_filter_table[ip]["BANNED_TIME"]


def check_ip_range(ip, times):
    for i in range(times):
        check(ip)


def check(ip):
    return anti.check_ip(ip)


# unit tests on pytest module
def test_check_ip_switch_off():
    anti.check_ip_switch = False
    assert check("1") == (anti.OK, "Website is currently disabled. ")


def test_check_ip_switch_on():
    anti.check_ip_switch = True
    assert check("2") == (anti.OK, "Welcome, new user. ")


def test_threshold_overloaded():
    anti.ip_filter_table = {}
    anti.threshold = 2
    assert check("1") == (anti.OK, "Welcome, new user. ")
    assert check("2") == (anti.OK, "Welcome, new user. ")
    assert check("3") == (anti.NO_SPACE, "IP filer is overfilled. Please try again late. ")
    anti.threshold = 100000


# FIXME
def test_threshold_clear_table():
    anti.ip_filter_table = {}
    anti.threshold = 2
    anti.num_softban = 1
    anti.log_time = 3
    check_ip_range("1", 2)
    check("2"), time.sleep(3)
    check("3")
    assert "1" in anti.ip_filter_table.keys()
    assert "2" not in anti.ip_filter_table.keys()
    assert "3" in anti.ip_filter_table.keys()
    anti.threshold = 100000
    anti.num_softban = 20
    anti.log_time = 20


def test_new_ip_time():
    anti.ip_filter_table = {}
    check("3")
    assert time.time() + 1 >= get_time("3")
    assert time.time() - 1 <= get_time("3")


def test_new_ip_num_logins():
    check("4")
    assert get_num_logins("4") == 1


def test_new_ip_status():
    check("5")
    assert get_status("5") == 0


def test_new_ip_banned_time():
    check("6")
    assert get_banned_time("6") == 0
