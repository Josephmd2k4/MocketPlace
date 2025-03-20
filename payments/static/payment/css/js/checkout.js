// This is your test secret API key.
const stripe = Stripe("pk_test_51R4r9IQMpcz9rN0YkNDxUYJNSa0KWfAMoDsz79SjBCX8p1Ese5nnJRAjjaXedTjeARvk8CTIMVAVgpoH4loGiqJx00EY6soAy5");

initialize();

// Create a Checkout Session
async function initialize() {
  const fetchClientSecret = async () => {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}