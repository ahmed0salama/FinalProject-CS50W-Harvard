# Pharmacy Management and E-Commerce System

## Overview

This project is a complete pharmacy management and online store system built with Django. It combines a customer-facing pharmacy storefront with an internal Enterprise Resource Planning (ERP) system for pharmacy employees and administrators.

The system allows customers to browse pharmaceutical and beauty products, search by product name, brand, or active ingredient, filter products by category, view alternative products, and reserve products using a shopping cart. Registered users can maintain their personal information and review their recent orders.

At the same time, authorized pharmacy employees can manage inventory, register vendors, create purchase orders, adjust stock quantities, monitor low-stock products, and complete sales through a Point of Sale (POS) interface. The project is designed to represent real pharmacy workflows instead of being limited to a basic online product catalog.

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

Employees can create purchase orders by selecting a vendor and adding multiple products. Each purchase order records:

- The vendor
- The employee who created it
- The products included
- Quantities purchased
- Purchase prices
- Individual subtotals
- The total invoice amount
- The creation date

When a purchase order is saved, the system automatically increases each product's inventory. The purchase workflow uses a database transaction so the purchase order and inventory changes are treated as one operation.

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

When a sale is completed, the system locks the selected products during processing, checks that sufficient stock is available, subtracts the correct number of sub-units, and creates a `SalesOrder` with related `SalesOrderItem` records.

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

Relationships between these models allow the project to connect inventory, purchasing, customers, sales, and credit balances into one integrated system.

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

### Distinctiveness and Complexity

This project is distinct because it combines two different but connected systems: an online pharmacy storefront for customers and an operational ERP platform for pharmacy staff. Many simple e-commerce projects only provide products, a shopping cart, and a checkout page. This project goes further by modeling the internal business processes required to operate a real pharmacy.

One important complexity is the multi-unit inventory design. Medicines are not always sold in one standard unit. A pharmacy may sell an entire box, a strip, a bottle, a tablet, or another smaller unit. The project solves this problem by storing inventory in the smallest unit while allowing employees to purchase and sell using either packages or sub-units. The conversion is calculated using the product's `units_per_package` value.

The project also connects purchasing and selling to inventory automatically. Creating a purchase order increases stock, while completing a POS sale decreases stock. Database transactions and row-level locking help protect inventory from inconsistent updates during important operations.

Another distinctive feature is active-ingredient intelligence. Customers can search for an active ingredient and view alternative products containing the same ingredient. This reflects a real pharmacy use case where different brands may contain equivalent medicines.

The payment system adds further complexity. A sale can be paid completely, paid partially, or recorded as credit. Any remaining balance can be added to a registered customer's account. This allows the system to represent real pharmacy credit transactions rather than assuming every sale is paid immediately.

Finally, the application includes role-based access control, bilingual support, responsive design, session-based reservations, inventory warnings, vendors, purchase orders, POS processing, and customer profiles. These features work together across the same database, making the project more than a collection of unrelated pages.

## Future Improvements

The project can be extended in several useful directions:

1. Add prescription verification so products marked as requiring a prescription cannot be reserved or sold without pharmacist approval.

2. Connect customer reservations to a formal pickup workflow. Employees could confirm, reject, or complete reservations from the ERP dashboard.

3. Add sales reports showing daily revenue, best-selling products, unpaid balances, and profit margins.

4. Add expiration dates and batch numbers because medication inventory often requires batch-level tracking.

5. Add automatic notifications for low-stock products, expiring medicines, and outstanding customer balances.

6. Improve automated testing for authentication, permissions, inventory conversion, stock deduction, purchase orders, payments, and cart behavior.

7. Replace external image URLs with secure local media storage or a managed cloud storage service.

8. Prepare the application for production by moving secrets into environment variables, setting `DEBUG` to `False`, configuring allowed hosts, and using a production database.

9. Add employee audit logs so managers can see who created purchases, changed stock, or processed sales.

10. Add a more complete customer checkout process, online payment integration, delivery tracking, and email confirmations.

## Conclusion

This pharmacy project demonstrates how Django can support both public e-commerce features and internal business management workflows. It models realistic pharmacy requirements including active ingredients, alternative products, package conversions, inventory control, supplier purchasing, POS sales, customer credit, role permissions, language support, and responsive design.

Its combination of customer convenience and pharmacy operations makes it a practical, distinctive, and expandable foundation for a complete digital pharmacy management platform.