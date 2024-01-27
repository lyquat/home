var chart = {}; var chart_x = []; var chart_y = []; var chart_min_x = 0;
var data = [];
{% for company in company_prices %}
    var symbol = "{{ company.symbol }}";
    var prices = [];
    {% for price in company.prices %}
        var xy = [];
        var date = new Date("{{ price.week_ending }}".replace(/-/g, "/"));
        var utc_date = dateToUTC(date);
        var x = utc_date;
        var y = parseFloat("{{ price.adjusted_close }}");
        xy.push(x);
        xy.push(y);
        prices.push(xy);
    {% endfor %}
    x = {symbol: symbol, prices: prices};
    data.push(x);
{% endfor %}
