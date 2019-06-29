<countdown>
    <div class="small">
        <div each={items} class="item">
            {summary} {fromNow} ({fromNowDays} days)
        </div>
    </div>

    <script>
        updateCountdown(data) {
            var items = []
            console.log("countdown item count: " + data.items.length)
            for (var i = 0; i < data.items.length; i++) {
                var item = data.items[i]
                var start = moment(item.start.date)
                var fromNow = start.fromNow()
                var fromNowDays = start.diff(moment(), 'days')
                if (fromNow.indexOf("hour") != -1) {
                    fromNow = "tomorrow"
                }
                items.push({
                    fromNow: fromNow,
                    fromNowDays: fromNowDays,
                    summary: item.summary
                })
            }

            this.update({
                items: items
            })
        }

        tick() {
            $.getJSON("/countdown", function(json) {
                this.updateCountdown(json)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(10, 'minutes').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</countdown>
