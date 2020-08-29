<!--
Plugins use Riot.js tags for the client-side implementation.
-->
<sample>
    <div class="small">{greeting}, {recipient}!</div>

    <style>
        div {
            font-weight: bold;
        }
    </style>

    <script>
        discovery() {
            $.getJSON("/discovery", function(json) {
                this.url = json["sample"]  // This is the root -- multiple tags could use the same root URL.
            }.bind(this))
        }

        tick() {
            $.getJSON(this.url, function(json) {
                this.update(json)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(1, 'minutes').asMilliseconds())

        this.on('mount', function() {
            this.discovery()
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</sample>
