<countdown>
    <div class="small">
        <div each={items} class="item">
            {summary} {fromNow} {fromNowDays}
        </div>
    </div>

    <script>
        updateCountdown(data) {
            var items = []
            console.log("countdown item count: " + data.items.length)
            for (var i = 0; i < data.items.length; i++) {
                var item = data.items[i]
                var start = moment('dateTime' in item.start ?
                    item.start.dateTime : item.start.date)
                var fromNow = start.fromNow()
                var fromNowDays = ''
                if (fromNow.indexOf('days') === -1) {
                    fromNowDays = '(' + start.diff(moment(), 'days') + ' days)'
                }
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
            $.getJSON("/calendar/countdown", function(json) {
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