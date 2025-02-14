
## HubSpot Company Manager

### What it is
A tool that helps you manage company information in HubSpot's CRM system, allowing you to create, update, and retrieve company records.

### What it does
This component handles all basic operations related to company data in HubSpot, including:
- Creating new company profiles
- Updating existing company information
- Retrieving company details using domain names

### How it works
The tool connects to your HubSpot account and performs the requested operation:
1. When creating a company, it adds a new company record with your provided information
2. When retrieving company details, it searches using the company's domain name
3. When updating, it first finds the company by domain name, then applies your changes

### Inputs
- Credentials: Your HubSpot account authentication details
- Operation: The action you want to perform ("create", "update", or "get")
- Company Data: Information about the company (like name, industry, size, etc.) when creating or updating records
- Domain: The company's website domain (e.g., "example.com") for finding specific companies

### Outputs
- Company: The company information returned by HubSpot
- Status: The result of your requested operation (e.g., "created", "updated", "retrieved", or "company_not_found")

### Possible use cases
- Setting up a new customer database by creating multiple company records
- Updating company information after receiving new details from a sales team
- Automatically retrieving company details when a new lead comes in
- Synchronizing company data between HubSpot and other business systems
- Building automated workflows that need to access or modify company information
