function drawProgress(canvas_id, percent) {
    console.log("Drawing activity progress: " + canvas_id + " " + percent);
    let canvas = document.getElementById(canvas_id);
    if (!canvas) {
        console.error("Canvas not found: " + canvas_id);
        return;
    }

    // Off-screen canvas for double-buffering to prevent flickering.
    var offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = canvas.width;
    offscreenCanvas.height = canvas.height;
    var offscreenCtx = offscreenCanvas.getContext('2d');
    offscreenCtx.clearRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);
    drawProgressRing(offscreenCtx, percent, offscreenCanvas.width, offscreenCanvas.height);

    // Draw off-screen canvas to visible canvas.
    const ctx = canvas.getContext("2d");
    ctx.drawImage(offscreenCanvas, 0, 0);
}

function drawProgressRing(ctx, percent, width, height) {
    let thinLineWidth = 1;
    let thickLineWidth = 6;
    let x = width / 2;
    let y = height / 2;
    let radius = height / 2 - thickLineWidth / 2;
    let rotation = Math.PI / 2; // amount to subtract to start with 0 at north
    let startAngle = 0 - rotation;
    let endAngleCircle = 2 * Math.PI - rotation;
    let endAnglePercent = 2 * Math.PI * percent - rotation;
    // Thin, full circle:
    drawArc(ctx, x, y, radius, startAngle, endAngleCircle, thinLineWidth);
    // Thick, progress:
    drawArc(ctx, x, y, radius, startAngle, endAnglePercent, thickLineWidth);
}

function drawArc(ctx, x, y, radius, start, end, lineWidth) {
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = lineWidth;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.arc(x, y, radius, start, end);
    ctx.stroke();
}
