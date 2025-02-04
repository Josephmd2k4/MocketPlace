self.addEventListener('push', function(event) {
    const data = event.data.json();

    self.ServiceWorkerRegistration.showNotification(data.title, {
        body: data.body,
        icon: data.icon,
    });
});