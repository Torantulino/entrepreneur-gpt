
## HubSpot Contact Manager

### What it is
A powerful tool that helps you manage contact information in your HubSpot CRM system. It serves as a bridge between your application and HubSpot's contact database.

### What it does
This component allows you to perform three essential contact management operations:
- Create new contacts in HubSpot
- Update existing contact information
- Retrieve contact details using email addresses

### How it works
The tool connects to your HubSpot account using secure credentials and performs the requested operation:
1. When creating contacts, it adds new contact information to your HubSpot database
2. When updating, it first looks up the contact by email, then modifies their information
3. When retrieving contacts, it searches using the provided email address and returns the matching contact's details

### Inputs
- Credentials: Your HubSpot account access information
- Operation: The action you want to perform ("create", "update", or "get")
- Contact Data: The information you want to store or update for a contact
- Email: The contact's email address (required for updating or retrieving contacts)

### Outputs
- Contact: The contact's information, including any fields stored in HubSpot
- Status: The result of your operation (such as "created", "updated", "retrieved", or "contact_not_found")

### Possible use cases
1. Customer Registration: Automatically create new HubSpot contacts when customers sign up on your website
2. Profile Updates: Update contact information when customers modify their profiles
3. Contact Lookup: Retrieve customer details for personalized service interactions
4. Data Synchronization: Keep your local database in sync with HubSpot contacts
5. Lead Management: Create and update leads in your CRM system automatically
