var chart = {}; var chart_x = []; var chart_y = []; var chart_min_x = 0;
var earnings_estimates = [];
var earnings_actuals = [];
var earnings_forecasts = [];
var shares = [];
var ytd = [];
var balance_sheet = {};
var income_statement = [];

{% for row in weeklies %}
    var date = new Date("{{ row.week_ending }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    chart_x.push(utc_date);
    v = parseFloat("{{ row.adjusted_close }}");
	chart_y.push(v);
{% endfor %}

chart_min_x = Math.min(...chart_x);
chart.x = chart_x; chart.y = chart_y; chart.min_x = chart_min_x;

{% for row in earnings_history %}
    var date = new Date("{{ row.reportedDate }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var eps = "{{row.reportedEPS}}";
    var reportedEPS = parseFloat(eps);
    var x = [];
    x.push(utc_date);
    x.push(reportedEPS);
    earnings_actuals.push(x);

    var est = "{{row.estimatedEPS}}";
    var estimatedEPS = parseFloat(est);
    var y = [];
    y.push(utc_date);
    y.push(estimatedEPS);
    earnings_estimates.push(y);
{% endfor %}

{% for row in earnings_forecast %}
    var date = new Date("{{ row.report_date }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var forecast = "{{row.forecastEPS}}";
    var forecastEPS = parseFloat(forecast);
    var z = [];
    z.push(utc_date);
    z.push(forecastEPS);
    earnings_forecasts.push(z);
{% endfor %}

{% for row in shares %}
    var date = new Date("{{ row.period }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var shares_outstanding = parseFloat("{{ row.shares_outstanding }}");
    var a = [];
    a.push(utc_date);
    a.push(shares_outstanding);
    shares.push(a);
{% endfor %}

{% for row in ytd %}
    var date = new Date("{{ row.date }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var min = parseFloat("{{ row.min }}");
    var max = parseFloat("{{ row.max }}");
    var b = [];
    b.push(utc_date);
    b.push(min);
    b.push(max);
    ytd.push(b);
{% endfor %}

var periods = [];
var total_cash = [];
var total_assets = [];
var total_liabilities = [];
var total_long_term_debt = [];

{% for row in balance_sheet %}
    var date = new Date("{{ row.period }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var assets = parseFloat("{{ row.totalAssets }}");
    var cash = parseFloat("{{ row.cash }}");
    var liabilities = parseFloat("{{ row.totalLiabilities }}");
    var long_term_debt = parseFloat("{{ row.longTermDebt }}");

    var w = []; w.push(utc_date); w.push(assets); total_assets.push(w);
    var x = []; x.push(utc_date); x.push(cash); total_cash.push(x);
    var y = []; y.push(utc_date); y.push(liabilities); total_liabilities.push(y);
    var z = []; z.push(utc_date); z.push(long_term_debt); total_long_term_debt.push(z);
{% endfor %}
balance_sheet = {"total_assets": total_assets, "total_cash": total_cash, "total_liabilities": total_liabilities, "total_long_term_debt": total_long_term_debt};

var total_revenues = [];
var total_cost_of_revenues = [];
var total_gross_profit = [];
var total_sga = [];
var total_income_taxes = [];
var total_depreciation = [];
var total_net_income = [];

{% for row in income_statement %}
    var date = new Date("{{ row.period }}".replace(/-/g, "/"));
    var utc_date = dateToUTC(date);
    var revenues = parseFloat("{{ row.totalrevenue }}");
    var cost_of_revenues = parseFloat("{{ row.costofrevenue }}");
    var gross_profit = parseFloat("{{ row.grossprofit }}");
    var sga = parseFloat("{{ row.sellinggeneralandadministrative }}");
    var income_taxes = parseFloat("{{ row.incometaxexpense }}");
    var depreciation = parseFloat("{{ row.depreciationandamortization }}");
    var net_income = parseFloat("{{ row.netincome }}");

    var a = [], b = [], c = [], d = [], e = [], f = [], g = [];
    a.push(utc_date); a.push(revenues); total_revenues.push(a);
    b.push(utc_date); b.push(cost_of_revenues); total_cost_of_revenues.push(b);
    c.push(utc_date); c.push(gross_profit); total_gross_profit.push(c);
    d.push(utc_date); d.push(sga); total_sga.push(d);
    e.push(utc_date); e.push(income_taxes); total_income_taxes.push(e);
    f.push(utc_date); f.push(depreciation); total_depreciation.push(f);
    g.push(utc_date); g.push(net_income); total_net_income.push(g);

{% endfor %}
income_statement = {"total_revenues": total_revenues, "total_cost_of_revenues": total_cost_of_revenues, "total_gross_profit": total_gross_profit, "total_sga": total_sga, "total_income_taxes": total_income_taxes, "total_depreciation": total_depreciation, "total_net_income": total_net_income};



