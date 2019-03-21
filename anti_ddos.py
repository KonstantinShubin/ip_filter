import time

# Config:
check_ip_switch = 1  # 1 - We check ips. 0 - if we want to turn off checking ips
log_time = 20  # Number in seconds in which we check for number of logins
num_softban = 20  # Number of max acceptable logins for log_time seconds
threshold = 2

ip_filter_table = {}
num_ips = 0


def check_ip(our_ip):
    global ip_filter_table
    global num_ips
    if check_ip_switch:
        if num_ips == threshold:
            clear_table()
        elif our_ip not in ip_filter_table.keys():
            ip_filter_table[our_ip] = [{"TIME": time.time(), "NUM_LOGINS": 1, "STATUS": 0}, ]
            num_ips += 1
            return 0  # LEGIT
        else:
            if ip_filter_table[our_ip][0]["STATUS"] == 1:
                return 1  # SOFTBAN
                # TODO: return 1, time - где time это время бана, которое мы можем увеличивать
            elif ip_filter_table[our_ip][0]["NUM_LOGINS"] + 1 > num_softban:
                ip_filter_table[our_ip][0]["STATUS"] = 1
                return 1  # SOFTBAN
            else:
                login_time = time.time()
                if login_time - ip_filter_table[our_ip][0]["TIME"] > log_time:
                    ip_filter_table[our_ip][0]["TIME"] = login_time
                    ip_filter_table[our_ip][0]["NUM_LOGINS"] = 1
                    return 0  # LEGIT
                else:
                    ip_filter_table[our_ip][0]["NUM_LOGINS"] += 1
                    return 0  # LEGIT


def clear_table():
    for ip in list(ip_filter_table):
        if ip_filter_table[ip][0]["STATUS"] == 1 and time.time() - ip_filter_table[ip][0]["TIME"] > log_time:
            del ip_filter_table[ip]
        else:
            return 2


check_ip("192.0.0.0")
check_ip("192.0.0.1")
check_ip("192.0.0.2")
