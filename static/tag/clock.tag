<clock>
    <div>
        <span class="large">{time}</span><br>
        <span>{date}</span>
    </div>


    <script>
        tick() {
            var now = moment()
            this.update({
                time: now.format("h:mm a"),
                date: now.format("dddd, MMMM Do YYYY")
            })
        }

        var timer = setInterval(this.tick, 1000)

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>

</clock>
