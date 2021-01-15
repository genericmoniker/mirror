var eventListeners = [];

function addEventListener(eventName, eventHandler) {
    eventListeners.push({
        eventName: eventName,
        eventHandler: eventHandler
    })
}



ROTATE_COUNT = 0;
ROTATE_INDEX = 0;

$(document).ready(function() {
    //updateCashFlow();
    initMessage();
    //initRotator();
    //setInterval(updateRotator, moment.duration(30, 'seconds').asMilliseconds());
});

function updateCashFlow() {
    drawNumberLine($("#cash_flow_canvas").get(0), -5, 15, 1);
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