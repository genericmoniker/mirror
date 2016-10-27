ROTATE_COUNT = 0;
ROTATE_INDEX = 0;

$(document).ready(function() {
    updateTime();
    setInterval(updateTime, 1 * 1000);
    updateWeather();
    setInterval(updateWeather, 60 * 1000);
    updateForecast();
    setInterval(updateForecast, 60 * 60 * 1000);
    updateAgenda();
    setInterval(updateAgenda, 2 * 60 * 1000);
    initRotator();
    setInterval(updateRotator, 30 * 1000);
});

function updateTime() {
    var now = moment();
    $("#time").html(now.format("h:mm a"));
    $("#date").html(now.format("dddd, MMMM Do YYYY"));
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

function initRotator() {
    $.getJSON("/rotate_count", function(json) {
        ROTATE_COUNT = json.count;
        console.log('initRotator: count=' + ROTATE_COUNT);
        $("#rotator").empty();
        for (var i = 0; i < ROTATE_COUNT; i ++) {
            $("#rotator").append($('<iframe/>', {
                id: 'rotate_' + i,
                class: 'rotator_frame',
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