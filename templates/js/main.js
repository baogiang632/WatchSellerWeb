// Get all "Add to Cart" buttons
var addToCartButtons = document.getElementsByClassName('add-to-cart');

// Loop through the buttons and add an event listener to each one
for (var i = 0; i < addToCartButtons.length; i++) {
    var button = addToCartButtons[i];
    button.addEventListener('click', addToCart);
}

// Function to handle adding an item to the cart
function addToCart(event) {
    // Get the product ID from the data-id attribute
    var productId = event.target.getAttribute('data-id');

    // Add the product to the cart
    // This will depend on how your cart is implemented
    // For example, you might add the product ID to an array or send a request to your server
    console.log('Adding product ' + productId + ' to cart');
}