<connectivity>
    <div id="conn" class="small" hide={connected}>
        <img src="static/img/network-error.svg"/>
    </div>

    <style>
        div {
            display: block;
            height: 75px;
            position: fixed;
            bottom: 0;
            right: 0;
            z-index: 999;
            padding-right: 20px;
        }

        img {
            height: 100%;
        }
    </style>

    <script>
        updateConnectivity(data) {
            this.update({
                connected: data.connected,
                error: data.error
            })
        }

        tick() {
            $.getJSON("/connectivity", function(json) {
                this.updateConnectivity(json)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(1, 'minutes').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</connectivity>