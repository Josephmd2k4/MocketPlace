const pub_key = "BCxOqxj2UUqwurebsRzMQjaC4uyzRArgylqNiQyqd5LjaRe-46mYu0jNcnRokgN-lrS6He7LG5PZmAeJgjDwBFY";

navigator.serviceWorker.register('/static/serviceWorker.js').then(registration => {
    return registration.pushManager.getSubscription().then(subscription => {
        if (!subscription) {
            return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: pub_key
            });
        }
        return subscription;
    });
}).then(subscription => {
    fetch('/webpush/save_information/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        body: JSON.stringify({
            subscription: subscription.toJSON(),
            group: 'test_group'
        })
    });
});