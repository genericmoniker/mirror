function drawNumberLine(canvas, min, max, value) {
    var w = canvas.width;
    var h = canvas.height;
    var midX = w / 2;
    var midY = h / 2;
    var range = max - min;
    var step = w / (range + 1);
    var pad = step / 2;
    var ctx = canvas.getContext('2d');

    with (ctx) {

        strokeStyle = '#fff';
        fillStyle = '#fff';
        font = '20px Roboto';
        lineWidth = 2;
        moveTo(0, midY);
        lineTo(w, midY);
        stroke();

        for (var i = min; i <= max; i++) {
            var x = Math.round((i + Math.abs(min)) * step) + pad;
            if (i === value) {
                moveTo(x, midY);
                arc(x, midY, 8, 0, 2 * Math.PI);
                fill();
            } else {
                moveTo(x, midY - 5);
                lineTo(x, midY + 5);
                stroke();
            }
            var textX = x - measureText(i).width / 2;
            fillText(i, textX, midY + 30);
        }
    }
}
