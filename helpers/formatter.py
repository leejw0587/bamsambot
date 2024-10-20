def numtostr(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def remove_wings(name: str):
    try:
        return name.strip("༺ৡۣۜ͜ ৡ ""ৡۣۜ͜ ৡ༻ ")
    except:
        return name
