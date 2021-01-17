<script context="module">
    let subscribers = [];

    export function subscribe(eventName, eventHandler) {
        subscribers.push({ eventName: eventName, eventHandler: eventHandler });
    }
</script>

<script>
    import { onMount } from "svelte";

    function eventHandlerWrapper(handler) {
        return (e) => {
            console.log(e.type, ":", e.data);
            return handler(e);
        };
    }

    onMount(() => {
        const eventSource = new EventSource("http://localhost:5000/events");

        eventSource.onopen = () => {
            console.log("Connected to event stream.");
        };

        eventSource.onerror = () => {
            console.log("Event stream failed.");
        };

        for (let i = 0; i < subscribers.length; i++) {
            let subscriber = subscribers[i];
            eventSource.addEventListener(
                subscriber.eventName,
                eventHandlerWrapper(subscriber.eventHandler)
            );
        }
    });
</script>
