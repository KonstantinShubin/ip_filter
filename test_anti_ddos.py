import anti_ddos as anti
import time
import pytest


# fixtures
@pytest.fixture
def reset_table():
    anti.ip_filter_table = {}
    anti.num_ips = 0
    anti.check_ip_switch = True
    anti.log_time = 60  # Number in seconds in which we check for number of logins
    anti.num_softban = 60  # Number of max acceptable logins for log_time seconds
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


def get_num_ips():
    return anti.num_ips


def check_ip_range(ip, times):
    for i in range(times):
        check(ip)


def check(ip):
    return anti.check_ip(ip)


# unit tests on pytest module
def test_check_ip_switch_off(reset_table):
    anti.check_ip_switch = False
    assert check("1") == (anti.OK, "Website is currently disabled. ")


def test_check_ip_switch_on(reset_table):
    assert check("1") == (anti.OK, "Welcome, new user. ")


def test_threshold_no_space(reset_table):
    anti.threshold = 2
    assert check("1") == (anti.OK, "Welcome, new user. ")
    assert check("2") == (anti.OK, "Welcome, new user. ")
    assert check("3") == (anti.NO_SPACE, "IP filer is overfilled. Please try again late. ")


def test_threshold_clear_table(reset_table):
    anti.threshold = 2
    anti.num_softban = 1
    anti.log_time = 3
    check_ip_range("1", 2)
    check("2"), time.sleep(anti.log_time + 1)
    check("3")

    assert get_status("1") == 1
    assert "1" in anti.ip_filter_table.keys()  # we keep banned user in table after clearing

    assert "2" not in anti.ip_filter_table.keys()  # we don't keep user, who logged long time ago

    assert get_status("3") == 0
    assert time.time() - get_time("3") <= anti.log_time
    assert "3" in anti.ip_filter_table.keys()  # we keep user who logged not long ago

    assert get_num_ips() == 2  # we hold number only of banned and recently logged user


def test_new_ip_time(reset_table):
    check("1")
    assert time.time() + 1 > get_time("1")
    assert time.time() - 1 < get_time("1")


def test_new_ip_num_logins(reset_table):
    check("1")
    assert get_num_logins("1") == 1


def test_new_ip_status(reset_table):
    check("1")
    assert get_status("1") == 0


def test_new_ip_banned_time(reset_table):
    check("1")
    assert get_banned_time("1") == 0


def test_num_ips(reset_table):
    assert get_num_ips() == 0
    check("1")
    assert get_num_ips() == 1
    check("1")
    assert get_num_ips() == 1
    check("2")
    assert get_num_ips() == 2


def test_longtime_ago_banned(reset_table):
    anti.num_softban = 2
    anti.first_time_ban = 5
    anti.log_time = 2

    check_ip_range("1", 3)
    assert anti.first_time_ban > anti.log_time
    assert get_status("1") == 1
    assert get_banned_time("1") == anti.first_time_ban
    time.sleep(anti.first_time_ban + 1)
    assert check("1") == (anti.OK, "You are unbanned now. ")
    assert time.time() + 1 > get_time("1")
    assert time.time() - 1 < get_time("1")
    assert get_num_logins("1") == 1
    assert get_status("1") == 0
    assert get_banned_time("1") == 0


def test_recently_logged_banned_user(reset_table):
    anti.num_softban = 2
    anti.first_time_ban = 30
    anti.log_time = 2
    anti.ban_time_coef = 1

    check_ip_range("1", 3)
    assert anti.first_time_ban > anti.log_time
    time.sleep(anti.first_time_ban - 25)
    check("1")
    assert round(get_banned_time("1")) == anti.ban_time_coef * (anti.first_time_ban - 5)
    assert time.time() + 1 > get_time("1")
    assert time.time() - 1 < get_time("1")
    remaining_time = time.strftime("%H hours, %M minutes and %S seconds", time.gmtime(get_banned_time("1")))
    assert check("1") == (anti.SOFT_BAN, "Your ban time was increased by {} and now is {}. Please try again later. ".format(anti.ban_time_coef, remaining_time))
    assert get_status("1") == 1

# def test_banned_time_over_max(reset_table):
