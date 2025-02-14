
# Slant3D Order Management Blocks

## Create Order

### What it is
A tool for creating new 3D printing orders in the Slant3D system.

### What it does
Creates a new manufacturing order with specified items and shipping details.

### How it works
Takes your order details, including customer information and items to be printed, and submits them to create a new order in the system.

### Inputs
- Credentials: Your Slant3D account authentication details
- Order Number: Your custom reference number (optional)
- Customer Details: Shipping information including name, address, and contact details
- Items: List of items to be printed, including file locations, quantities, colors, and material types

### Outputs
- Order ID: Your unique Slant3D order identifier
- Error: Any error message if the order creation fails

### Possible use case
A business owner needs to create a bulk order for custom 3D printed parts with specific shipping requirements.

## Order Cost Estimator

### What it is
A calculator for determining the total cost of a potential order.

### What it does
Provides a detailed cost breakdown including printing and shipping expenses.

### How it works
Analyzes your order details and calculates various cost components before you commit to placing the order.

### Inputs
- Credentials: Your Slant3D account authentication details
- Order Number: Your custom reference number (optional)
- Customer Details: Shipping information for accurate cost calculation
- Items: List of items to be printed

### Outputs
- Total Price: Complete cost in USD
- Shipping Cost: Estimated shipping expenses
- Printing Cost: Cost of printing services
- Error: Any error message if estimation fails

### Possible use case
A customer wants to compare costs for different printing options before placing an order.

## Shipping Cost Estimator

### What it is
A specialized tool for calculating shipping costs only.

### What it does
Provides shipping cost estimates based on delivery location and order details.

### How it works
Evaluates shipping requirements based on delivery address and order specifications to calculate shipping costs.

### Inputs
- Credentials: Your Slant3D account authentication details
- Order Number: Your custom reference number (optional)
- Customer Details: Shipping address information
- Items: List of items for shipping calculation

### Outputs
- Shipping Cost: Estimated shipping expense
- Currency Code: Currency type (e.g., 'usd')
- Error: Any error message if estimation fails

### Possible use case
A customer needs to compare shipping costs to different delivery addresses.

## Order List Viewer

### What it is
A tool for viewing all orders associated with your account.

### What it does
Retrieves and displays a complete list of your orders.

### How it works
Fetches all order information from your account history and presents it in an organized format.

### Inputs
- Credentials: Your Slant3D account authentication details

### Outputs
- Orders: List of all orders with their details
- Error: Any error message if retrieval fails

### Possible use case
A business manager needs to review all past orders for accounting purposes.

## Order Tracker

### What it is
A tracking system for monitoring order status and shipping progress.

### What it does
Provides real-time information about order status and shipping details.

### How it works
Connects to the shipping system to retrieve current status and tracking information for specific orders.

### Inputs
- Credentials: Your Slant3D account authentication details
- Order ID: The specific order you want to track

### Outputs
- Status: Current order status
- Tracking Numbers: List of shipping tracking numbers
- Error: Any error message if tracking fails

### Possible use case
A customer wants to monitor the progress of their order from printing to delivery.

## Order Cancellation

### What it is
A tool for canceling existing orders.

### What it does
Allows you to cancel orders that haven't yet been processed.

### How it works
Submits a cancellation request for the specified order and confirms the cancellation status.

### Inputs
- Credentials: Your Slant3D account authentication details
- Order ID: The order you want to cancel

### Outputs
- Status: Confirmation of cancellation
- Error: Any error message if cancellation fails

### Possible use case
A customer needs to cancel an order due to changed requirements or specifications.
