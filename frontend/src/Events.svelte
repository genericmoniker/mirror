<script context="module">
    let subscribers = [];
    let connected = false;

    export function subscribe(eventName, eventHandler) {
        if (connected) {
            throw "Attempt to `subscribe` after already connected to EventSource.";
        }
        subscribers.push({ eventName: eventName, eventHandler: eventHandler });
    }
</script>

<script>
    import { onMount } from "svelte";

    function eventHandlerWrapper(handler) {
        return (e) => {
            console.log("Event", e.type, ":", e.data);
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

        connected = true;
    });
</script>
