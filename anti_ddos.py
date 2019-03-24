import time

# Config:

# 1 - We check ips. 0 - if we want to turn off checking ips
check_ip_switch = True
log_time = 20  # Number in seconds in which we check for number of logins
num_softban = 20  # Number of max acceptable logins for log_time seconds
threshold = 2
first_time_ban = 1800  # time is seconds (1800 = 30 minutes)
ban_time_coef = 1.5
max_ban_time = 21600  # time in seconds (21600 = 6 hours)

ip_filter_table = {}
num_ips = 0

OK = 0
SOFT_BAN = 1
NO_SPACE = 2


# FIXME
def clear_table():
    for ip in list(ip_filter_table):
        if ip_filter_table[ip][0]["STATUS"] == 0 \
                and time.time() - ip_filter_table[ip][0]["TIME"] > log_time:
            del ip_filter_table[ip]
        else:
            return NO_SPACE


def check_ip(our_ip):
    global ip_filter_table
    global num_ips

    # TODO: Add function metrics

    login_time = time.time()

    if not check_ip_switch:
        return OK, ""

    if num_ips >= threshold:
        clear_table()
        num_ips = len(ip_filter_table.keys())

    if num_ips >= threshold:
        return NO_SPACE, "IP filer is overfilled. Please try again late"

    if our_ip not in ip_filter_table.keys():
        ip_filter_table[our_ip] = [{"TIME": time.time(),
                                    "NUM_LOGINS": 1, "STATUS": 0, "BANNED_TIME": 0}]
        num_ips += 1
        return OK, ""

    if ip_filter_table[our_ip][0]["STATUS"] == 1:
        if ip_filter_table[our_ip][0]["BANNED_TIME"] == 0 and login_time - ip_filter_table[our_ip][0]["TIME"] > log_time:
            ip_filter_table[our_ip][0]["STATUS"] = 0
            ip_filter_table[our_ip][0]["TIME"] = login_time
            return OK, ""
        elif ip_filter_table[0]["BANNED_TIME"] > login_time - ip_filter_table[our_ip][0]["TIME"]:
            ip_filter_table[our_ip][0]["TIME"] = login_time
            ip_filter_table[our_ip][0]["BANNED_TIME"] = ban_time_coef * (ip_filter_table[0]["BANNED_TIME"] - login_time - ip_filter_table[our_ip][0]["TIME"])
            if ip_filter_table[our_ip][0]["BANNED_TIME"] > max_ban_time:
                ip_filter_table[our_ip][0]["BANNED_TIME"] = max_ban_time
            remaining_ban_time = time.strftime("%H hours, %M minutes and %S seconds. ", time.gmtime(ip_filter_table[our_ip][0]["BANNED_TIME"]))
            return SOFT_BAN, f"Your ban time was increased and now is {remaining_ban_time} seconds." \
                "Please try again later."
    elif ip_filter_table[our_ip][0]["NUM_LOGINS"] + 1 > num_softban:
        ip_filter_table[our_ip][0]["STATUS"] = 1
        ip_filter_table[our_ip][0]["TIME"] = login_time
        ip_filter_table[our_ip][0]["BANNED_TIME"] = first_time_ban
        remaining_ban_time = time.strftime("%H hours, %M minutes and %S seconds. ", time.gmtime(first_time_ban))
        return SOFT_BAN, f"You have been blocked for {remaining_ban_time}" \
            f"If you return before this time ends, your remaining ban time will be multiplied by {ban_time_coef}. " \
            "Please try again later."
    else:
        if login_time - ip_filter_table[our_ip][0]["TIME"] > log_time:
            ip_filter_table[our_ip][0]["NUM_LOGINS"] = 1
            ip_filter_table[our_ip][0]["TIME"] = login_time
            return OK, ""
        else:
            ip_filter_table[our_ip][0]["NUM_LOGINS"] += 1
            return OK, ""
