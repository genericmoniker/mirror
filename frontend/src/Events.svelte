<script context="module">
  let subscribers = [];

  export function subscribe(eventName, eventHandler) {
    // Note: If a component tries to subscribe after the EventSource
    // is created, it won't get any events!
    subscribers.push({ eventName: eventName, eventHandler: eventHandler });
  }
</script>

<script>
  import Icon from "svelte-awesome";
  import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
  import { onMount } from "svelte";

  let connected = false;

  function eventHandlerWrapper(handler) {
    return (e) => {
      console.log("Event", e.type, ":", e.data);
      return handler(e);
    };
  }

  function connectToEventSource() {
    const eventSource = new EventSource("http://localhost:5000/events");

    eventSource.onopen = () => {
      connected = true;
      console.log("Event source: connected");
    };

    eventSource.onerror = () => {
      connected = false;
      console.log("Event source: error");
    };

    for (let i = 0; i < subscribers.length; i++) {
      let subscriber = subscribers[i];
      eventSource.addEventListener(
        subscriber.eventName,
        eventHandlerWrapper(subscriber.eventHandler)
      );
    }
  }

  onMount(() => {
    connectToEventSource();
  });
</script>

{#if !connected}
  <div id="conn">
    <Icon data={faExclamationTriangle} scale="1.7" />
  </div>
{/if}

<style>
  #conn {
    display: block;
    height: 50px;
    position: fixed;
    bottom: 0;
    left: 0;
    z-index: 999;
    padding-left: 20px;
  }
</style>
