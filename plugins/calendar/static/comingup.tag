<coming-up>

    <div class="small">
        <div each={items} class="item">
            {summary} {fromNow}
        </div>
    </div>

    <style>
        .item {
            padding: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: auto;
        }
    </style>
    <script>
        updateComingUp(data) {
            var items = []
            console.log("coming up item count: " + data.items.length)
            for (var i = 0; i < data.items.length; i++) {
                var item = data.items[i]
                var start = moment(item.start.date)
                var fromNow = start.fromNow()
                if (fromNow.indexOf("hour") != -1) {
                    fromNow = "tomorrow"
                }
                items.push({
                    fromNow: fromNow,
                    summary: item.summary
                })
            }

            this.update({
                items: items
            })
        }

        tick() {
            $.getJSON("/coming-up", function(json) {
                this.updateComingUp(json)
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
</coming-up>