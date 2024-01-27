import locale

def human_format(x):
    locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
    try:
        num = float(x)
        millions_only = num/1000000
        formatted = locale.currency(millions_only, grouping=True)
        return formatted
    except:
        return "N/A"

def color(x):
    try:
        num = float(x)
        if(num) <0:
            return 'red'
        else:
            return 'green'
    except:
        return ''

def format_2dp(val):
    return '{:.02f}'.format(val)