<countup>
    <div class="small">{opts.label} {daysNumber} {daysString}</div>

    <script>
        tick() {
            var now = moment()
            var then = moment(opts.date)
            var days = now.diff(then, 'days')
            this.update({
                daysNumber: days,
                daysString: days === 1 ? 'day' : 'days'
            })
        }

        var timer = setInterval(this.tick, moment.duration(1, 'hour').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</countup>
