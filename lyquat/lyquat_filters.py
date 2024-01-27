import locale

def changepct(x, y):
    pct = 0
    try:
        xf = float(x)
        yf = float(y)
        if xf <= yf:
            pct = (1-xf/yf) * 100;
        else:
            pct = -(1-(yf/xf)) * 100;
        return pct
    except:
        # noop
        return pct

def date_string(x):
    fmt = "%A, %-d %B %Y"
    return x.strftime(fmt)

def human_format(x):
    #locale.setlocale( locale.LC_ALL, '' )
    locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8')
    try:
        num = float(x)
        millions_only = num/1000000
        formatted = locale.currency(millions_only, grouping=True)
        return formatted
    except Exception as e: 
        print(e)
        return "N/A"

def escape_backslash(x):
    tmp  = ""
    foo = list(x)
    for x in foo:
        if x == "/":
            tmp += "\\" + x
        else:
            tmp += x
    print(tmp)
    return tmp

def thousands(x):
    try:
        num = float(x)
        thousands_only = num/1000
        return "{:,}".format(thousands_only)
    except:
        return "N/A"

def millions(x):
    try:
        num = float(x)
        thousands_only = num/1000000
        return "{:,.02f}".format(thousands_only)
    except:
        return "N/A"

def format_2dp(val):
    return '{:.02f}'.format(val)

def swap_sort(val):
    if(val == "asc"):
        return "desc"
    if(val == "desc"):
        return "asc"

def from_camelcase(string):
    tmp  = ""
    foo = list(string)
    for x in foo:
        if x.isupper():
            tmp += " " + x
        else:
            tmp += x
    return tmp

def pad_cik(x):
    tmp = x
    while len(tmp) < 10:
        tmp = "0" + tmp
    return tmp

def color(x):
    try:
        num = float(x)
        if(num) <0:
            return 'red'
        else:
            return 'green'
    except:
        return ''

def country(currency):
    return {
        'ARS':'argentina',
        'AUD':'australia',  
        'BRL':'brazil',
        'CAD':'canada',
        'CHF':'switzerland',
        'CLP':'chile',
        'CNY':'china',
        'COP':'colombia',
        'DKK':'denmark',
        'EUR':'european-union',
        'GBP':'united-kingdom',
        'IDR':'indonesia',
        'ILS':'israel',
        'INR':'india',
        'JPY':'japan',
        'KRW':'south-korea',
        'MXN':'mexico',
        'NOK':'norway',
        'PEN':'peru',
        'RUB':'russia',
        'SAR':'saudi-arabia',
        'SEK':'sweden',
        'SGD':'singapore',
        'TRY':'turkey',
        'TWD':'taiwan',
        'INR':'india',
        'USD':'united-states',
        'ZAR':'south-africa'
    }.get(currency, 'none')