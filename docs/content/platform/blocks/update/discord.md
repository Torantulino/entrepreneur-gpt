
# Discord Integration Blocks

## Read Discord Messages

### What it is
A component that monitors and captures messages from Discord channels.

### What it does
Connects to Discord and reads incoming messages, including any text file attachments, providing the message content along with channel and sender information.

### How it works
Once activated, it connects to Discord using a bot account and listens for new messages. When a message is received, it captures the content, channel name, and username of the sender. If the message includes text file attachments, it will also read and include their contents.

### Inputs
- Discord Credentials: A bot token that allows the block to connect to Discord

### Outputs
- Message Content: The text content of the received message, including any attached text files
- Channel Name: The name of the Discord channel where the message was sent
- Username: The name of the user who sent the message

### Possible use case
Creating a customer support system that monitors support channels for questions and automatically logs all conversations for future reference.

## Send Discord Message

### What it is
A component that sends messages to specified Discord channels.

### What it does
Sends text messages to designated Discord channels and confirms the delivery status.

### How it works
The block connects to Discord using a bot account, locates the specified channel, and sends the message. If the message is longer than Discord's character limit, it automatically splits it into smaller chunks for proper delivery.

### Inputs
- Discord Credentials: A bot token that allows the block to connect to Discord
- Message Content: The text message you want to send
- Channel Name: The name of the channel where you want to send the message

### Outputs
- Status: Confirmation of whether the message was sent successfully or if any errors occurred

### Possible use case
Setting up an automated notification system that sends status updates or alerts to a Discord channel when certain events occur in your application.
