import time

# Config:

# 1 - We check ips. 0 - if we want to turn off checking ips
check_ip_switch = True
log_time = 3  # Number (seconds) in which number of logins is checked
num_softban = 1  # Number of max logins for log_time seconds
threshold = 2
first_time_ban = 1800  # time is seconds (1800 = 30 minutes)
ban_time_coef = 1.5
max_ban_time = 21600  # time in seconds (21600 = 6 hours)
keep_time = 172800  # max keep time for softbanned user (seconds)

ip_filter_table = {}
num_ips = 0

OK = 0
SOFT_BAN = 1
NO_SPACE = 2


# support functions
def get_time(ip):
    return ip_filter_table[ip]["TIME"]


def get_num_logins(ip):
    return ip_filter_table[ip]["NUM_LOGINS"]


def get_status(ip):
    return ip_filter_table[ip]["STATUS"]


def get_ban_time(ip):
    return ip_filter_table[ip]["BANNED_TIME"]


def get_time_diff(ip):
    return time.time() - ip_filter_table[ip]["TIME"]


def clear_table():
    global num_ips
    for ip in list(ip_filter_table):
        old_status_0 = get_status(ip) == 0 and get_time_diff(ip) > log_time
        old_status_1 = get_status(ip) == 1 and get_time_diff(ip) > keep_time
        if old_status_0 or old_status_1:
            del ip_filter_table[ip]
            num_ips -= 1


def check_ip(our_ip):
    global ip_filter_table
    global num_ips

    # TODO: Add function metrics

    current_time = time.time()

    if not check_ip_switch:
        return OK, "Website is currently disabled. "

    if num_ips >= threshold:
        clear_table()
        num_ips = len(ip_filter_table.keys())

    if num_ips >= threshold:
        return NO_SPACE, "IP filer is overfilled. Please try again late. "

    # New User
    if our_ip not in ip_filter_table.keys():
        ip_filter_table[our_ip] = {"TIME": time.time(),
                                   "NUM_LOGINS": 1,
                                   "STATUS": 0,
                                   "BANNED_TIME": 0}
        num_ips += 1
        return OK, "Welcome, new user. "

    if get_status(our_ip) == 1:
        # Soft banned User waited for ban_time ending
        if get_ban_time(our_ip) <= current_time - get_time(
                our_ip) and current_time - get_time(our_ip) > log_time:
            ip_filter_table[our_ip]["TIME"] = current_time
            ip_filter_table[our_ip]["NUM_LOGINS"] = 1
            ip_filter_table[our_ip]["STATUS"] = 0
            ip_filter_table[our_ip]["BANNED_TIME"] = 0
            return OK, "You are unbanned now. "
        # Soft banned User logged again before ban_time expired
        elif get_ban_time(our_ip) > current_time - get_time(our_ip):
            remaining_time = get_ban_time(our_ip) - get_time_diff(our_ip)
            rounded_ban_time = round(ban_time_coef * remaining_time)
            ip_filter_table[our_ip]["BANNED_TIME"] = rounded_ban_time
            ip_filter_table[our_ip]["TIME"] = current_time
            if get_ban_time(our_ip) > max_ban_time:
                ip_filter_table[our_ip]["BANNED_TIME"] = max_ban_time
            ban_time_text = "%H hours, %M minutes and %S seconds"
            ip_ban_time = time.gmtime(get_ban_time(our_ip))
            remaining_ban = time.strftime(ban_time_text, ip_ban_time)
            return SOFT_BAN, f"Ban time was increased by {ban_time_coef} " \
                f"and now is {remaining_ban}. Please try again later. "

    else:
        # Known User returned after log_time expired
        if current_time - get_time(our_ip) > log_time:
            ip_filter_table[our_ip]["NUM_LOGINS"] = 1
            ip_filter_table[our_ip]["TIME"] = current_time
            return OK, "Welcome. Haven't seen you for a while. "
        else:
            ip_filter_table[our_ip]["NUM_LOGINS"] += 1
            # First time banned user, now is soft banned
            if get_num_logins(our_ip) > num_softban:
                ip_filter_table[our_ip]["STATUS"] = 1
                ip_filter_table[our_ip]["TIME"] = current_time
                ip_filter_table[our_ip]["BANNED_TIME"] = first_time_ban
                ban_time_text = "%H hours, %M minutes and %S seconds"
                ip_ban_time = time.gmtime(first_time_ban)
                first_ban = time.strftime(ban_time_text, ip_ban_time)
                return SOFT_BAN, f"You are blocked for {first_ban}. " \
                    f"If you return before this time ends, your remaining " \
                    f"ban time will be multiplied by {ban_time_coef}. " \
                    "Please try again later. "
            # Known User returned in log_time
            else:
                return OK, "Hi again. "
