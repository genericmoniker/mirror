<clock>
    <div>
        <span class="large">{time}</span><br>
        <span>{date}</span>
    </div>


    <script>
        export default {
            tick() {
                var now = DateTime.local();
                this.update({
                    time: now.toLocaleString(DateTime.TIME_SIMPLE),
                    date: now.toLocaleString(DateTime.DATE_HUGE)
                })
            },

            onBeforeMount(props, state) {
                state.timer = setInterval(this.tick, 1000)
                this.tick()
            },

            onUnmounted(props, state) {
                clearInterval(state.timer)
            }
        }
    </script>

</clock>
