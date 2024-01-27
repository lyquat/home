function info(x){
	console.log(x);
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function popCookieValue(cname, symbol){
	let cstring = getCookie(cname);
	let symbols = cstring.split(",");
	let index = symbols.indexOf(symbol);
	if(index >=0){
		let foo = symbols.filter(function(s){ return s !== symbol});
		let foostr = foo.toString();
		setCookie(cname, foostr, 365);
	}
}

function appendToCookie(cname, symbol){
	let cstring = getCookie(cname);
	let symbols = cstring.split(",");
	let v = symbols.push(symbol);
	value = symbols.toString();
	setCookie(cname, value, 365);
}

function cookieValueExists(cname, symbol){
	let cstring = getCookie(cname);
	let symbols = cstring.split(",");
	let index = symbols.indexOf(symbol);
	return symbols.indexOf(symbol) > -1;
}

function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function watch_or_ignore(e, symbol, cname){
	el = $(e);
	opacity = el.css("opacity");
	if(opacity < 1){
		el.css({ opacity: 1 });
	}else{
		el.css({ opacity: 0.3 });
	}
	let cookie_exists = getCookie(cname);
	if(cookie_exists === ""){
		setCookie(cname, symbol, 365);
		return;
	}
	let value_exists = cookieValueExists(cname, symbol);
	if(value_exists){
		popCookieValue(cname, symbol);
	}else{
		appendToCookie(cname, symbol);
	}
}

function numberWithCommas(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function replaceCommas(num){
	return num.toString().replace(',','');
}

function replaceNonNumeric(num){
	return num.toString().replace(/[^\d\.]/g,"");
}

function changePct(v1, v2){
	if(v1 <= v2){
		return (1-v1/v2) * 100
	}else{
		return -(1-(v2/v1)) * 100
	}
}

function dateToUTC(d){
  year = d.getFullYear();
  month = d.getMonth();
  day = d.getDate();
  d2 = Date.UTC(year, month, day);
  return d2;
}

function calculate(){

      valid = validate_inputs();
      if(!valid){
        return;
      }

      var cashflow_el = $("#cf");
      var cashflow = parseFloat(cashflow_el.val());

      var growth_el = $("#growth");
      var growth = parseFloat(growth_el.val());

      years = $(".year");
      
      var term_val = 0;
      term_multiple_el = $("#tm");
      var term_multiple = parseFloat(term_multiple_el.val());

      for(var i=0;i<years.length;i++){
        x = 0;
        foo = $(years[i]);
        if(i==0){
          x = cashflow * (1 + (growth/100));
        }else{
          y = $(years[i-1]);
          x = y.text() * (1 + (growth/100));
        }
        x_form = x.toFixed(2);
        foo.text(x_form);
        term_val = x_form * term_multiple;
      }
      term_value_el = $("#term")
      term_value_el.text(parseFloat(term_val).toFixed(3));

      var discount_rate_el = $("#discount");
      var discount_rate = parseFloat(discount_rate_el.val()/100);
      var dc = 1 + discount_rate;
      var period = dc ^ -years.length + 1;
      var intrinsic_value = term_val * (dc ** period);
      var iv_est = parseFloat(intrinsic_value).toFixed(2);
      info(iv_est);
      iv_ele = $("#intrinsic_value");
      iv_ele.text(numberWithCommas(iv_est));
      // info("iv_ele=" + iv_ele.text(numberWithCommas(iv_est)));
      mc = $('td[name="market_cap"]').text();
      info("mc=" + mc);
      market_cap = replaceNonNumeric(mc);
      market_cap_f = parseFloat(market_cap);
      // info("market_cap_f=" + market_cap_f);
      // info("iv_est=" + iv_est);
      change = changePct(market_cap_f, iv_est).toFixed(3);
      // info(change);
      change_pct = $("#change");
      change_pct.text(change);
      color = change >= 0 ? "green" : "red";
      change_pct.removeClass("red");
      change_pct.removeClass("green");
      change_pct.addClass(color);
    }

  function validate_inputs(){
    valid = true;
    $("#dcf input").each(function(idx, val){
      // info(val.value);
      if(isNaN(val.value)){ // not a valid number
        valid = false;
        return false; // break out of each in jquery
      }
    });
    return valid;
  }

