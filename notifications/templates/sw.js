// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
    // Retrieve the text payload from event.data
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'New Notification!!';
    const body = data.body || 'Message Empty, Default Content';

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        self.registration.showNotification(head, {
            body: body,
            icon: 'https://i.imgur.com/MZM3K5w.png'
        })
    );
});