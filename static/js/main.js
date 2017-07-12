ROTATE_COUNT = 0;
ROTATE_INDEX = 0;

$(document).ready(function() {
    updateTime();
    setInterval(updateTime, moment.duration(1, 'seconds').asMilliseconds());

    updateCountdown();
    setInterval(updateCountdown, moment.duration(1, 'hours').asMilliseconds());

    updateWeather();
    setInterval(updateWeather, moment.duration(60, 'seconds').asMilliseconds());
    updateWeatherAlerts();
    setInterval(updateWeatherAlerts, moment.duration(60, 'seconds').asMilliseconds());
    updateForecast();
    setInterval(updateForecast, moment.duration(1, 'hour').asMilliseconds());

    //updateCashFlow();

    updateAgenda();
    setInterval(updateAgenda, moment.duration(2, 'minutes').asMilliseconds());
    updateComingUp();
    setInterval(updateComingUp, moment.duration(10, 'minutes').asMilliseconds());

    initMessage();
    //initRotator();
    //setInterval(updateRotator, moment.duration(30, 'seconds').asMilliseconds());
});

function updateTime() {
    var now = moment();
    $("#time").html(now.format("h:mm a"));
    $("#date").html(now.format("dddd, MMMM Do YYYY"));
}

function updateCountdown() {
    var now = moment();
    var then = moment("2017-11-08");
    var days = then.diff(now, 'days');
    var days_string = days === 1 ? ' day' : ' days';
    $("#countdown").html('MTC in ' + days + days_string);
}

function updateWeather() {
    $.getJSON("/weather", function(json) {
        $("#weather_icon").removeClass();
        $("#weather_icon").addClass('large ' + iconClass(json.icon));
        $("#weather_temp").html(Math.round(json.temperature));
        $("#weather_summary").html(json.summary);
        $("#weather_feels").html(Math.round(json.apparentTemperature));
        $("#weather_wind").html(Math.round(json.windSpeed));
    });
}

function updateWeatherAlerts() {
    $.getJSON("/weather_alerts", function(json) {
        if (json.length > 0) {
            $("#weather_alert").css('display', 'block');
            $("#weather_alert_title").html(json[0].title);
        } else {
            $("#weather_alert").css('display', 'none');
            $("#weather_alert_title").html('');
        }
    });
}

function updateForecast() {
    $.getJSON("/forecast", function(json) {
        var limit = Math.min(5, json.data.length);
        var today = json.data[0];
        var sunrise = moment.unix(today.sunriseTime).local();
        $("#weather_sunrise").html(sunrise.format("h:mm a"));
        var sunset = moment.unix(today.sunsetTime).local();
        $("#weather_sunset").html(sunset.format("h:mm a"));
        $("#forecast_0").html(
            "<td>Today</td>" +
            forecastCells(today)
        );
        for (var i = 1; i < limit; i++) {
            var day = json.data[i];
            var date = moment.unix(day.time).local();
            $("#forecast_" + i).html(
                "<td>" + date.format("ddd") + "</td>" +
                forecastCells(day)
            );
        }
    });
}

function forecastCells(day) {
    var rain = Math.round(day.precipProbability * 100);
    return (
        "<td><i class='" + iconClass(day.icon) + "'></i></td>" +
        "<td>↑ <b>" + Math.round(day.temperatureMax) + "°</b></td>" +
        "<td>↓ " + Math.round(day.temperatureMin) + "°</td>" +
        "<td><i class='wi wi-umbrella'></i> " + rain +
        "<sup class='tiny'>%</sup></td>"
     );
}

function iconClass(icon) {
    return 'wi wi-forecast-io-' + icon;
}

function updateCashFlow() {
    drawNumberLine($("#cash_flow_canvas").get(0), -5, 15, 1);
}

function updateAgenda() {
    $.getJSON("/agenda", function(json) {
        var rows = "";
        for (var i = 0; i < json.items.length; i++) {
            var row = "<tr>";
            var item = json.items[i];
            if ('dateTime' in item.start) {
                var start = moment(item.start.dateTime);
                row += "<td>" + start.format("h:mm a") + "</td>";
            } else {
                // all day event
                row += "<td>All Day -</td>";
            }
            row += "<td>" + item.summary + "</td>";
            rows += row;
        }
        if (json.items.length == 0) {
            rows += "<tr><td colspan='2'>Nothing more today</td></tr>";
        }
        $("#agenda_items").html(rows);
    });
}

function updateComingUp() {
    $.getJSON("/coming-up", function(json) {
        console.log("coming up item count: " + json.items.length)
        var rows = "";
        for (var i = 0; i < json.items.length; i++) {
            var row = "<tr>";
            var item = json.items[i];
            row += "<td>" + item.summary + "</td>";
            var start = moment(item.start.date);
            var fromNow = start.fromNow();
            if (fromNow.indexOf("hour") != -1) {
                fromNow = "tomorrow";
            }
            row += "<td>" + fromNow + "</td>"
            rows += row;
        }
        $("#coming_up_items").html(rows);
    });
}

function initMessage() {
    $("#message").append($('<iframe/>', {
        class: 'message_frame',
        style: 'display: block',
        src: '/message',
    }));
}

function initRotator() {
    $.getJSON("/rotate_count", function(json) {
        ROTATE_COUNT = json.count;
        console.log('initRotator: count=' + ROTATE_COUNT);
        $("#message").empty();
        for (var i = 0; i < ROTATE_COUNT; i ++) {
            $("#message").append($('<iframe/>', {
                id: 'rotate_' + i,
                class: 'message_frame',
                style: 'display: none',
                src: '/rotate?counter=' + i,
            }));
        }
        updateRotator();
    });
}

function updateRotator() {
    console.log('updateRotator: index=' + ROTATE_INDEX);
    for (var i = 0; i < ROTATE_COUNT; i ++) {
        var id = "#rotate_" + i;
        if (i == ROTATE_INDEX) {
            $(id).css('display', 'block');
        } else {
            $(id).css('display', 'none');
        }
    }
    ROTATE_INDEX = (ROTATE_INDEX < ROTATE_COUNT - 1) ? ROTATE_INDEX + 1 : 0;
}