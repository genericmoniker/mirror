from threading import RLock


class Cache:
    """Data cache with automatic periodic update."""
    def __init__(self, scheduler, name, refresh_min, refresh):
        """Create a new instance.

        :param scheduler: scheduler to use for periodic updates.
        :param name: name of the update job (for logging).
        :param refresh_min: minutes between periodic updates.
        :param refresh: function to call to update the data.
        """
        self._data = None
        self._lock = RLock()
        self._do_refresh = refresh
        scheduler.add_job(
            self.refresh,
            'interval',
            name=name,
            minutes=refresh_min)

    def get(self):
        """Get the current cached data."""
        with self._lock:
            if not self._data:
                self.refresh()
            return self._data

    def refresh(self):
        """Refresh the cached data."""
        with self._lock:
            self._data = self._do_refresh()
