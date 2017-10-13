<agenda>
    <table class="small">
        <tr each={items}>
            <td>{start}</td>
            <td>{summary}</td>
        </tr>
    </table>

    <style>
        table {
            width: auto;
            margin-right: 0px;
            margin-left: auto;
        }

        td {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 400px;
            text-align: left;
        }
    </style>

    <script>
        updateAgenda(data) {
            var items = []
            for (var i = 0; i < data.items.length; i++) {
                var item = data.items[i]
                if ('dateTime' in item.start) {
                    var startTime = moment(item.start.dateTime)
                    var start = startTime.format("h:mm a")
                } else {
                    var start = "All Day - "
                }
                items.push({
                    start: start,
                    summary: item.summary
                })
            }
            if (data.items.length == 0) {
                items.push({
                    start: "Nothing more today",
                    summary: ""
                })
            }

            this.update({
                items: items
            })
        }

        tick() {
            $.getJSON("/agenda", function(json) {
                this.updateAgenda(json)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(5, 'minutes').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</agenda>