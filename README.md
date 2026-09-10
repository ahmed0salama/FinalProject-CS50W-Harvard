# Pharmacy ERP and Management Dashboard

## Overview

This project is primarily a pharmacy Enterprise Resource Planning (ERP) system and management dashboard built with Django. Its main purpose is to help pharmacy employees and administrators manage inventory, vendors, purchasing, sales, payments, and customer credit. The customer-facing e-commerce storefront is an integrated supporting feature, not the main focus of the project.

The ERP dashboard is the central part of the application. It provides pharmacy staff with operational tools for monitoring stock, registering suppliers, recording purchase orders, adjusting inventory, and processing sales through a Point of Sale (POS) interface. The storefront allows customers to browse pharmaceutical and beauty products, search by product name, brand, or active ingredient, filter products by category, view alternative products, and reserve products using a shopping cart.

The project is designed to represent real pharmacy management workflows instead of being limited to a basic online product catalog. The e-commerce functionality gives customers a convenient way to interact with the pharmacy, while the ERP and dashboard provide the core business value and operational control.

The application uses Django, SQLite, Bootstrap, JavaScript, Django templates, Django authentication, and Django's internationalization features. The project supports both English and Arabic interfaces and automatically changes the page direction between left-to-right and right-to-left layouts.

## Main Features

### Customer Storefront

The homepage provides a searchable product catalog. Customers can search for products by:

- Product name
- Brand
- Active ingredient

Products can also be filtered by category. Every product card displays important information such as the product name, brand, category, price, image, active ingredient, and whether a prescription is required.

Customers can reserve products through the cart. The cart is connected to the visitor's Django session, which means that a customer does not necessarily need to create an account before adding products. Each cart item is stored in the database through the `CartReservation` model.

The cart allows the application to preserve a customer's selected products while they continue browsing. Products with the same active ingredient can also be displayed as alternatives. This is especially useful in a pharmacy because customers may need another brand containing the same medicine or active ingredient.

### User Accounts

The project uses a custom user model based on Django's `AbstractUser`. Each user has a role:

- Client
- Employee or pharmacist
- Administrator

Customers can register with a username, email address, name, phone number, and address. Password confirmation is validated during registration, and new public accounts are automatically assigned the client role.

Users can log in and log out using Django authentication. After login, clients are redirected to the storefront, while employees and administrators are redirected to the ERP dashboard.

The profile page allows authenticated users to update their personal information. It also displays their role, credit balance, and recent sales orders.

## Pharmacy ERP

The ERP section is restricted to employees, pharmacists, administrators, and Django superusers. This protection is implemented through the custom `employee_required` decorator. Unauthenticated users are redirected to the login page, while regular clients are denied access.

### Dashboard

The ERP dashboard provides a quick overview of pharmacy operations. It displays:

- Total number of products
- Number of low-stock products
- Total units in stock
- Number of vendors
- A list of products that need attention

The dashboard considers products with 20 or fewer sub-units to be low in stock. This gives employees an immediate warning when inventory needs to be replenished.

### Inventory Management

Employees can add new products and edit existing products. Each product can store:

- Name
- Brand
- Category
- Active ingredient
- Package unit
- Sub-unit
- Units per package
- Package price
- Sub-unit price
- Stock quantity
- Prescription requirement
- Description
- Image URL

Inventory is tracked using the smallest available unit. For example, a product may be sold as a box containing several strips or as an individual strip. The system stores the stock in sub-units while also calculating the equivalent number of packages.

Employees can search inventory by product name, brand, or active ingredient. They can also make quick stock adjustments using either packages or sub-units. The system converts packages into sub-units automatically and prevents the final inventory quantity from becoming negative.

### Vendors and Purchase Orders

The vendor module stores supplier information including contact names, company names, phone numbers, email addresses, and physical addresses.

Employees can create purchase orders by selecting a vendor and adding multiple products. Each order records:

- The vendor
- The employee who created it
- The products included
- Quantities purchased
- Purchase prices
- Individual subtotals
- The total invoice amount
- The creation date

When a purchase order is saved, the system automatically increases inventory. The workflow uses a database transaction so the order and stock changes are treated as one operation.

The purchase order history displays previous invoices and allows employees to expand each invoice to see its delivered products and purchase prices.

### Point of Sale

The POS screen is designed for pharmacy employees who need to process sales quickly. It provides a searchable product catalog and allows the cashier to add either a complete package or an individual sub-unit to the current sales ticket.

The POS supports:

- Package sales
- Sub-unit sales
- Quantity changes
- Walk-in customers
- Registered clients
- Partial payments
- Unpaid credit sales
- Automatic stock deduction
- Automatic remaining-balance calculation

When a sale is completed, the system locks the selected products, checks stock, subtracts the correct number of sub-units, and creates a `SalesOrder` with related `SalesOrderItem` records.

The payment status is calculated automatically as fully paid, partially paid, or unpaid. If the customer does not pay the entire amount and is registered in the system, the remaining amount is added to the customer's credit balance.

## Data Model

The central database entities are:

- `User`: Stores customer, employee, and administrator accounts.
- `Category`: Organizes products and supports parent categories and subcategories.
- `ActiveIngredient`: Identifies the medicinal substance contained in a product.
- `Product`: Stores product information, packaging, pricing, stock, and prescription status.
- `Vendor`: Stores supplier details.
- `PurchaseOrder`: Represents an incoming supplier invoice.
- `PurchaseOrderItem`: Stores the products included in a purchase order.
- `SalesOrder`: Represents a completed or reserved customer transaction.
- `SalesOrderItem`: Stores each product sold and its unit type.
- `CartReservation`: Stores products reserved in a visitor's session cart.

These relationships connect inventory, purchasing, customers, sales, and credit balances into one integrated system.

## Mobile Responsiveness

The project is mobile responsive. Bootstrap 5 is used throughout the templates with responsive containers, rows, columns, navigation components, tables, forms, modals, and buttons.

The layout includes the responsive viewport setting and uses Bootstrap's responsive grid system. On smaller screens, the navigation collapses, product cards adjust their image height, and catalog columns stack vertically. Inventory and purchase-order tables use responsive wrappers so they can be viewed on narrow screens without breaking the page layout.

The custom stylesheet also includes media queries for mobile navigation, product images, cart controls, profile icons, and spacing. This allows customers and pharmacy employees to use the system from desktop computers, tablets, and mobile phones.

## Internationalization

The system supports English and Arabic. Django's translation framework is enabled through `LocaleMiddleware`, translation tags, and a dedicated Arabic translation file.

When Arabic is selected, the application:

- Displays Arabic translations where available.
- Changes the document direction to right-to-left.
- Loads Bootstrap's RTL stylesheet.
- Preserves the selected language while navigating between pages.

The language selector is available from the user menu, allowing users to change the interface without leaving the current workflow.

## Distinctiveness and Complexity

This project is distinct because its main focus is a pharmacy ERP and management dashboard, supported by an integrated online storefront. The e-commerce component is not the central idea; it is one customer-facing part of a larger operational system. The most important purpose of the project is to model and simplify the internal business processes required to operate a real pharmacy.

Unlike a basic e-commerce project, this system gives pharmacy employees a complete workspace for managing stock, suppliers, purchases, sales, payments, and customer credit. The dashboard is the operational center where staff can monitor the pharmacy and take action.

One important complexity is the multi-unit inventory design. Medicines may be sold as boxes, strips, bottles, tablets, or other units. The project stores inventory in the smallest unit while allowing employees to purchase and sell packages or sub-units. Conversion uses the product's `units_per_package` value.

The project also connects purchasing and selling to inventory automatically. Creating a purchase order increases stock, while completing a POS sale decreases stock. Database transactions and row-level locking help protect inventory from inconsistent updates during important operations.

Another distinctive feature is active-ingredient intelligence. Customers can search for an ingredient and view alternative products containing it, reflecting the real need to identify equivalent brands.

The payment system adds further complexity. A sale can be fully paid, partially paid, or recorded as credit. Any remaining balance can be added to a registered customer's account.

Together, role-based access, bilingual support, responsive design, reservations, inventory warnings, vendors, purchasing, POS processing, and profiles make this a connected pharmacy management platform rather than an e-commerce website with a few administrative pages.

## Future Improvements

The project can be extended in several useful directions:

1. Add prescription verification so restricted products require pharmacist approval.

2. Connect reservations to a pickup workflow managed from the ERP dashboard.

3. Add reports for revenue, best-selling products, unpaid balances, and profit margins.

4. Add expiration dates and batch numbers for medication tracking.

5. Add notifications for low stock, expiring medicines, and customer balances.

6. Expand automated tests for permissions, inventory, purchasing, payments, and carts.

7. Replace external image URLs with secure local or cloud media storage.

8. Prepare for production with environment variables, `DEBUG = False`, allowed hosts, and a production database.

9. Add audit logs for purchases, stock changes, and sales.

10. Add online payments, delivery tracking, and email confirmations.

## Conclusion

This pharmacy project demonstrates how Django can support a complete ERP and management dashboard for pharmacy operations, with e-commerce features as a secondary customer interface. It models active ingredients, alternatives, package conversions, inventory, purchasing, POS sales, credit, permissions, language support, and responsive design.

The ERP dashboard and its operational workflows are the main idea. The storefront adds customer convenience, but the central value is helping pharmacy staff control the business through one connected management system.