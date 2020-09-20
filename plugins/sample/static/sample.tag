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
        tick() {
            $.getJSON(this.url, function(json) {
                this.update(json)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(1, 'minutes').asMilliseconds())

        this.on('mount', function() {

            // Plugin server-side resources are mounted
            // at the path matching the plugin name:
            this.url = '/sample/'

            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</sample>
