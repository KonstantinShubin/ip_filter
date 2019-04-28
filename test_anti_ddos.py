import anti_ddos as anti
import time
import pytest

good_ip = 0
banned_ip = 1


# fixtures
@pytest.fixture
def reset_table():
    anti.ip_filter_table = {}
    anti.check_ip_switch = True
    anti.log_time = 60  # Number (seconds) in which number of logins is checked
    anti.num_softban = 60  # Number of max logins for log_time seconds
    anti.threshold = 100000
    anti.first_time_ban = 1800  # time is seconds (1800 = 30 minutes)
    anti.ban_time_coef = 1.5
    anti.max_ban_time = 21600  # time in seconds (21600 = 6 hours)
    anti.keep_time = 172800  # max keep time for soft banned IP (seconds)


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


def assert_current_time(ip):
    assert time.time() + 0.5 > get_time(ip)
    assert time.time() - 0.5 < get_time(ip)


def table_keys():
    return anti.ip_filter_table.keys()


def ips_count():
    return len(anti.ip_filter_table)


# unit tests on pytest module
def test_check_ip_switch_off(reset_table):
    """
    No operations with ip_table, while ip_switch is off
    """
    anti.check_ip_switch = False
    assert check("192.1.1.1") == (anti.OK, "Website is currently disabled. ")
    assert "192.1.1.1" not in table_keys()


def test_check_ip_switch_on(reset_table):
    """
    New IP is added in ip_table if ip_switch is on.
    """
    assert check("192.1.1.1") == (anti.OK, "Welcome, new user. ")
    assert "192.1.1.1" in table_keys()


def test_threshold_no_space(reset_table):
    """
    New IP can't be added if ip_table is overfilled after clearing.
    """
    anti.threshold = 2

    assert check("192.1.1.1") == (anti.OK, "Welcome, new user. ")
    assert check("192.2.2.2") == (anti.OK, "Welcome, new user. ")
    no_space_text = "IP filer is overfilled. Please try again late. "
    assert check("192.3.3.3") == (anti.NO_SPACE, no_space_text)
    assert "192.3.3.3" not in table_keys()


def test_threshold_clear_table(reset_table):
    """
    DDOS scenario:

    When clearing table:
    Soft banned IP is kept in table before max_keep_time expires.
    Good IP is kept in table if log_time didn't expire.
    Good IP is deleted from table if log_time expired.
    Soft banned IP is deleted from table if max_keep_time expired.

    After clearing table:
    New Good IP joins table.
    """
    anti.threshold = 2
    anti.num_softban = 2
    anti.log_time = 3
    anti.keep_time = 5

    check_ip_range("192.1.1.1", 3)
    check("192.2.2.2")
    time.sleep(anti.log_time + 1)
    check("192.3.3.3")
    # Table is now cleared here
    # Soft banned IP is in table after clearing before max_keep_time expires
    assert get_status("192.1.1.1") == banned_ip
    assert "192.1.1.1" in table_keys()
    # IP is deleted from ip_table if log_time expires
    assert "192.2.2.2" not in table_keys()
    # IP is kept after clearing if log_time didn't expire from last login
    assert get_status("192.3.3.3") == good_ip
    assert time.time() - get_time("192.3.3.3") <= anti.log_time
    assert "192.3.3.3" in table_keys()  # New IP joins table
    assert ips_count() == 2  # Banned and recently logged IPs
    time.sleep(anti.keep_time + 1)
    check("192.3.3.3")
    # Table is now cleared here
    assert get_status("192.3.3.3") == good_ip
    assert ips_count() == 1
    assert "192.3.3.3" in table_keys()
    assert "192.1.1.1" not in table_keys()  # Deleted after max_keep_time


def test_new_ip_time(reset_table):
    """
    Saved time of IP is in range of max 0.5 sec
    """
    check("192.1.1.1")
    assert_current_time("192.1.1.1")


def test_new_ip_num_logins(reset_table):
    """
    New IP in table has number of logins = 1
    """
    check("192.1.1.1")
    assert get_num_logins("192.1.1.1") == 1


def test_new_ip_status(reset_table):
    """
    New IP in table has status = 0 (Not soft banned)
    """
    check("192.1.1.1")
    assert get_status("192.1.1.1") == good_ip


def test_new_ip_banned_time(reset_table):
    """
    New IP in table has no ban time
    """
    check("192.1.1.1")
    assert get_banned_time("192.1.1.1") == 0


def test_count(reset_table):
    """
    Counting number of IPs in ip_table
    """
    assert ips_count() == 0
    check("192.1.1.1")
    assert ips_count() == 1
    check("192.1.1.1")
    assert ips_count() == 1
    check("192.2.2.2")
    assert ips_count() == 2


def test_longtime_ago_banned(reset_table):
    """
    Soft banner IP is unbanned when he logins after ban time expired
    """
    anti.num_softban = 2
    anti.first_time_ban = 5
    anti.log_time = 2

    check_ip_range("192.1.1.1", 3)
    assert anti.first_time_ban > anti.log_time
    assert get_status("192.1.1.1") == banned_ip
    assert get_banned_time("192.1.1.1") == anti.first_time_ban
    assert get_num_logins("192.1.1.1") == 3
    time.sleep(anti.first_time_ban + 1)
    assert check("192.1.1.1") == (anti.OK, "You are unbanned now. ")
    assert_current_time("192.1.1.1")
    assert get_num_logins("192.1.1.1") == 1
    assert get_status("192.1.1.1") == good_ip
    assert get_banned_time("192.1.1.1") == 0


def test_recently_logged_banned_ip(reset_table):
    """
    Ban time is increased, if soft banned IP returns before ban time expires
    """
    anti.num_softban = 2
    anti.first_time_ban = 30
    anti.log_time = 2
    anti.ban_time_coef = 1

    check_ip_range("192.1.1.1", 3)
    assert anti.first_time_ban > anti.log_time
    time.sleep(anti.first_time_ban - 25)
    check("192.1.1.1")
    assert round(get_banned_time("192.1.1.1")) == anti.ban_time_coef * (
                anti.first_time_ban - 5)
    assert_current_time("192.1.1.1")
    remaining_time = time.strftime("%H hours, %M minutes and %S seconds",
                                   time.gmtime(get_banned_time("192.1.1.1")))
    assert check("192.1.1.1") == (anti.BANNED,
                                  f"Ban time increased by {anti.ban_time_coef}"
                                  f" and now is {remaining_time}. ")
    assert get_status("192.1.1.1") == banned_ip


def test_banned_time_over_max(reset_table):
    """
    Ban time can't be over max_ban_time variable in config
    """
    anti.num_softban = 2
    anti.first_time_ban = 30
    anti.log_time = 2
    anti.ban_time_coef = 1000000
    anti.max_ban_time = 60

    check_ip_range("192.1.1.1", 3)
    assert anti.first_time_ban > anti.log_time
    time.sleep(anti.first_time_ban - 25)
    check("192.1.1.1")
    assert round(get_banned_time("192.1.1.1")) == anti.max_ban_time
    assert_current_time("192.1.1.1")
    remaining_time = time.strftime("%H hours, %M minutes and %S seconds",
                                   time.gmtime(get_banned_time("192.1.1.1")))
    assert check("192.1.1.1") == (anti.BANNED,
                                  f"Ban time increased by {anti.ban_time_coef}"
                                  f" and now is {remaining_time}. ")
    assert get_status("192.1.1.1") == banned_ip
    assert round(get_banned_time("192.1.1.1")) == anti.max_ban_time


def test_not_banned_ip(reset_table):
    """
    Number of logins is = 1 for good IPs which returned after log_time expired
    """
    anti.log_time = 3

    check("192.1.1.1")
    time.sleep(anti.log_time + 1)
    assert check("192.1.1.1") == (anti.OK, "Welcome back. ")
    assert get_num_logins("192.1.1.1") == 1
    assert_current_time("192.1.1.1")


def test_num_logins_over_limit(reset_table):
    """
    Ip gets soft ban if it logins more than num_softban time for a log_time
    """
    anti.num_softban = 2
    anti.ban_time_coef = 4
    anti.first_time_ban = 30

    check("192.1.1.1")
    assert get_num_logins("192.1.1.1") == 1
    check("192.1.1.1")
    assert get_num_logins("192.1.1.1") == 2
    remaining_time = time.strftime("%H hours, %M minutes and %S seconds",
                                   time.gmtime(anti.first_time_ban))
    assert check("192.1.1.1") == (anti.BANNED,
                                  f"Blocked for {remaining_time}. "
                                  f"If you return before this time ends, your "
                                  f"remaining ban time will be multiplied by "
                                  f"{anti.ban_time_coef}. ")
    assert get_num_logins("192.1.1.1") == anti.num_softban + 1
    assert get_status("192.1.1.1") == banned_ip
    assert_current_time("192.1.1.1")
    assert get_banned_time("192.1.1.1") == anti.first_time_ban


def test_good_ip_returned_again(reset_table):
    """
    Status for again logged IP is returned and num_logins increases
    """
    check("192.1.1.1")
    assert get_num_logins("192.1.1.1") == 1
    assert check("192.1.1.1") == (anti.OK, "Hi again. ")
    assert get_num_logins("192.1.1.1") == 2


def test_massive_amount(reset_table):
    """
    Testing mass ddos scenario, after clearing table we need to:
    - keep soft banned IPs in ip_table after clearing table.
    - join new good IPs in ip_table.
    """
    anti.num_softban = 2
    anti.log_time = 3
    anti.first_time_ban = 5
    for x in range(85000):
        check_ip_range(f"192.0.0.{x}", 1)
    assert ips_count() == 85000
    for y in range(10000):
        check_ip_range(f"192.1.1.{y}", 3)  # IP is now soft banned
    assert ips_count() == 95000
    for z in range(5000):
        check_ip_range(f"192.2.2.{z}", 1)
    assert ips_count() == 100000

    time.sleep(7)
    for k in range(15000):
        check_ip_range(f"192.3.3.{k}", 1)
    n = 0
    for key, value in anti.ip_filter_table.items():
        if value["STATUS"] == 1:
            n += 1
    assert n == 10000  # Soft banned IP are in table before keep_time expires
    assert ips_count() == 25000
    for y in range(10000):
        check_ip_range(f"192.1.1.{y}", 1)
    for y in range(10000):
        assert anti.ip_filter_table[f"192.1.1.{y}"]["STATUS"] == 0
    assert ips_count() == 25000
