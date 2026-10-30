# Round 2 Basic Trac

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Models and Relationships](#database-models-and-relationships)
- [Authentication and Authorization](#authentication-and-authorization)
- [Phase 1: Project Setup](#phase-1-project-setup)
- [Phase 2: Core Functionality](#phase-2-core-functionality)
- [Installation and Setup](#installation-and-setup)
- [Usage Guide](#usage-guide)
- [Transaction Safety](#transaction-safety)
- [Limitations and Future Improvements](#limitations-and-future-improvements)

## Features

### User Features

- Register and log in using a username and password.
- Browse available events.
- Add money to a wallet using a simulated deposit form.
- Book ticket-based events or reserve places in slot-based events.
- Select a slot when booking a slot-based event.
- View previous bookings and their details.
- View wallet transaction history, including deposits and event purchases.
- View booking status and identify tickets using their booking IDs.
- Access the user dashboard and wallet functionality.

### Organization Features

- Access a dedicated organization dashboard.
- Create and manage events belonging to the organization.
- Create ticket-based events with a price and available ticket inventory.
- Create slot-based events with individual start times, end times, and capacities.
- View bookings made for the organization's events.
- View booking IDs, user information, booking timestamps, quantities, and slot details where applicable.
- Mark purchased tickets as consumed.
- View event analytics, including bookings, revenue, and remaining inventory or slot capacity.

### Administrative Features

- Use a Django superuser account to access administrative functionality.
- Create organization accounts through the superuser workflow.
- Manage registered users, organizations, events, and bookings through the appropriate administrative interfaces.

## Technology Stack

- **Python** — Application programming language.
- **Django** — Web framework, authentication, ORM, routing, templates, and administrative interface.
- **PostgreSQL** — Relational database.
- **HTML, CSS, and JavaScript** — Frontend templates and interactive form behaviour.
- **Django ORM** — Database queries and model relationships.

## Project Structure

The project is organized into Django applications that separate account management from event-related functionality.

```text
task2_basic/
├── manage.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── events/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── ...
├── templates/
└── ...
```

The exact template and configuration locations depend on the project settings.

- **`accounts`** handles user accounts, organizations, wallets, transactions, and account-related dashboards.
- **`events`** handles events, slots, bookings, booking operations, and organization analytics.
- **`forms.py`** defines forms for event creation and booking-related input.
- **Django templates** provide the user, organization, and administrative interfaces.

## Database Models and Relationships

The data model separates account management, event management, and financial transactions. This avoids storing unrelated information in a single model and makes it easier to enforce relationships between users, organizations, events, and bookings.

### 1. User

The application uses Django's built-in user model for authentication.

**Purpose:**
- Store usernames and password hashes.
- Authenticate users.
- Associate accounts with organization profiles, wallets, and bookings.

Django's authentication system handles password hashing and login verification rather than storing plaintext passwords.

### 2. Organization

The `Organization` model represents an organization that can create and manage events.

**Relationship:**
- Each organization has a one-to-one relationship with a Django user account.
- An organization can own multiple events.

The one-to-one relationship ensures that an organization profile is associated with a single account. Organization permissions are checked on the server before allowing access to organization-specific functionality.

### 3. Wallet

The `Wallet` model stores a user's wallet balance.

**Relationship:**
- Each wallet belongs to one user through a one-to-one relationship.
- A user can access their wallet and its associated transaction history.

The one-to-one relationship ensures that each user has at most one wallet. The balance is stored using a decimal field to represent monetary amounts without relying on binary floating-point arithmetic.

### 4. Transaction

The `Transaction` model records wallet-related financial activity.

**Transaction types include:**
- `DEPOSIT` — Money added to the wallet through the simulated deposit form.
- `BOOKING` — Money deducted when an event is booked.

**Relationship:**
- Each transaction belongs to a wallet.
- A wallet can have multiple transactions.

Each transaction stores its type, amount, description, and creation timestamp. This provides a historical record of deposits and booking payments.

### 5. Event

The `Event` model represents an event offered by an organization.

Important fields include:
- Organization that owns the event.
- Event description.
- Price per ticket or place.
- Available ticket inventory for ticket-based events.
- Event type: ticket-based or slot-based.
- Creation timestamp.

**Relationship:**
- Each event belongs to one organization.
- An organization can create multiple events.
- An event can have multiple bookings.
- A slot-based event can have multiple time slots.

The `event_type` field distinguishes between ticket-based and slot-based booking. This allows both event types to use a shared event model while applying different inventory and capacity rules.

### 6. EventSlot

The `EventSlot` model represents an individual time slot for a slot-based event.

Important fields include:
- Associated event.
- Start time.
- End time.
- Capacity.

**Relationship:**
- Each slot belongs to one event.
- An event can have multiple slots.
- A slot can have multiple bookings.

Keeping slots in a separate model allows an organization to define multiple booking windows for the same event, each with its own capacity.

For example, a sports facility could offer a 10:00–11:00 slot and an 11:00–12:00 slot, with separate capacity limits.

### 7. Booking

The `Booking` model represents a user's purchase or reservation.

Important fields include:
- User who made the booking.
- Event being booked.
- Selected slot, where applicable.
- Quantity of tickets or places.
- Total price.
- Booking timestamp.
- Whether the booking has been consumed.
- Timestamp at which the booking was consumed.

**Relationships:**
- Each booking belongs to one user.
- Each booking belongs to one event.
- A booking can optionally reference an event slot.

The slot relationship is optional because ticket-based events do not require a time slot. It also allows the same booking model to represent both ticket purchases and slot reservations.

Each booking has a unique database ID, which can be used to identify it on the user's booking page and the organization's booking dashboard.

The `is_consumed` field tracks whether a booking has been used. The `consumed_at` field records when it was marked as consumed.

In the current implementation, consumption applies to the entire booking record, including all tickets or places represented by its quantity.

### Relationship Summary

### Model Relationships

- **User and Organization:** One-to-one. Each organization account is linked to one user account.
- **Organization and Event:** One-to-many. An organization can create multiple events, but each event belongs to one organization.
- **User and Wallet:** One-to-one. Each user has one wallet.
- **Wallet and Transaction:** One-to-many. A wallet can have multiple transactions, such as deposits and booking payments.
- **User and Booking:** One-to-many. A user can make multiple bookings, but each booking belongs to one user.
- **Event and Booking:** One-to-many. An event can have multiple bookings, but each booking is for one event.
- **Event and EventSlot:** One-to-many. An event can have multiple slots, but each slot belongs to one event.
- **EventSlot and Booking:** One-to-many. A slot can be linked to multiple bookings. The slot field in a booking is optional because ticket-based events do not require slots.

## Authentication and Authorization

The application uses Django's built-in authentication system and group-based authorization.

### Authentication

Users authenticate using a username and password. Django handles password hashing and authentication.

Login-protected views require users to be authenticated before accessing account-specific functionality.

### User and Organization Groups

Django groups distinguish ordinary users from organization accounts.

- **`Users`** — Regular user accounts.
- **`Organizations`** — Organization accounts.

The application checks group membership and, where necessary, the associated organization profile before allowing access to protected views.

### Server-Side Access Control

Authorization is enforced in the backend rather than relying only on which links are displayed in the interface.

Examples include:
- Ordinary users can access their own wallet and booking history.
- Organizations can manage only their own events.
- Organizations can view bookings associated with their own events.
- Organizations cannot consume bookings belonging to another organization.
- Organization-only functionality rejects accounts without the required organization access.
- Administrative account creation is restricted to the superuser workflow.

These checks help prevent users from accessing or modifying resources that do not belong to them.

## Phase 1: Project Setup

Phase 1 establishes the database structure, authentication system, and core user booking flow.

### Implementation

1. Set up the Django project and PostgreSQL database.
2. Create models for users' organization profiles, wallets, transactions, events, and bookings.
3. Implement username/password authentication.
4. Implement group-based access control for regular users and organizations.
5. Create pages for browsing events.
6. Implement simulated wallet deposits.
7. Implement event booking using wallet balances.
8. Record deposits and booking payments in the transaction history.
9. Provide a page for users to view their bookings.

### User Flow

1. A user registers and logs in.
2. The user browses available events.
3. The user adds money through the simulated deposit form.
4. The deposit updates the wallet balance and creates a transaction record.
5. The user books an event or selects an available slot.
6. The application checks the relevant inventory or slot capacity and the user's wallet balance.
7. If the booking succeeds, the wallet is debited and the booking and associated transaction are recorded.
8. The user can view the booking and transaction history.

During the initial stage, events can be created through the Django administrative interface. Phase 2 extends this functionality with an organization-facing dashboard.

## Phase 2: Core Functionality

Phase 2 adds organization account creation, event management, booking operations, and analytics.

### 1. Organization Account Creation

A Django superuser can create organization credentials through the administrative workflow.

Organization accounts are associated with organization profiles and assigned the appropriate group so that the application can distinguish them from ordinary users.

### 2. Organization Dashboard

Organization accounts have access to a dedicated dashboard for managing their events and viewing related information.

Organizations can:
- View their own events.
- Create new events.
- Edit or delete their own events.
- View bookings for their events.
- Mark bookings as consumed.
- Access event analytics.

### 3. Ticket-Based Events

Organizations can create events with a description, price, and available ticket inventory.

When a user books a ticket-based event, the application checks that sufficient tickets remain and that the user's wallet has enough money.

On successful booking, the ticket inventory and wallet balance are updated, and a booking record and wallet transaction are created.

### 4. Slot-Based Events

Organizations can create slot-based events and define individual slots.

Each slot includes:
- Start time.
- End time.
- Maximum capacity.

Users can select a slot and specify how many places they want to reserve.

The application checks the remaining capacity for the selected slot before accepting the booking. Different slots have independent capacity limits.

### 5. Booking Management and Ticket Consumption

Organizations can view bookings associated with their own events.

The booking list includes relevant information such as:
- Booking ID.
- User.
- Event.
- Quantity.
- Booking timestamp.
- Selected slot, where applicable.
- Consumption status.

An organization can mark a booking as consumed. The application records the consumption timestamp and updates the booking status.

This supports the event check-in flow: users can present their booking details, and the organization can identify and validate the corresponding booking.

### 6. Event Analytics

Organizations can access analytics for the events they own.

The analytics include:
- Total events.
- Total booking records.
- Total tickets or places booked.
- Total booking revenue.
- Consumed bookings.
- Pending, unconsumed bookings.
- Booking and revenue information for individual events.
- Remaining ticket inventory for ticket-based events.
- Slot-level bookings and remaining capacity for slot-based events.

The analytics are restricted to the relevant organization, so one organization cannot view another organization's event statistics.

## Installation and Setup

### Prerequisites

Ensure that the following are installed:
- Python.
- PostgreSQL.
- Git.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd task2_basic
```

Replace `<your-repository-url>` with the URL of your GitHub repository.

### 2. Create and Activate a Virtual Environment

On Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

If a `requirements.txt` file is included in the repository, install the dependencies using:

```bash
python -m pip install -r requirements.txt
```

If no dependency file is present, install the packages required by the project, including Django, PostgreSQL's Python database adapter, and any additional packages imported by the application.

### 4. Configure PostgreSQL

Create a PostgreSQL database for the application and configure the database connection in the Django settings.

Use the database name, username, password, host, and port appropriate for your local PostgreSQL installation.

If the project uses environment variables, configure the required values in the environment or `.env` file according to the settings implementation.

Do not commit database passwords or other secrets to the repository.

### 5. Apply Database Migrations

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

The migration commands create and update the database tables corresponding to the application's models.

If migrations are already included and up to date, running `makemigrations` may report that no changes are detected.

### 6. Create a Superuser

Run:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an administrative account.

This account can access Django's administrative interface and the application's superuser-only organization account creation workflow.

### 7. Start the Development Server

Run:

```bash
python manage.py runserver
```

Open the local development address shown in the terminal in your browser.

The Django administrative interface is available at:

```text
/admin/
```

Use the superuser credentials created earlier to log in.

## Usage Guide

### For Regular Users

1. Register for an account.
2. Log in using your username and password.
3. Browse the available events.
4. Open the wallet page and add money using the simulated deposit form.
5. Select an event to book.
6. For a slot-based event, select an available slot and enter the desired quantity.
7. Complete the booking using the wallet balance.
8. View your bookings and transaction history.
9. Use the booking ID to identify the booking when presenting it for check-in.

### For the Superuser

1. Log in using the superuser account.
2. Open the administrative interface or the application's superuser dashboard.
3. Create organization credentials through the available organization account creation workflow.
4. Ensure the organization account has the appropriate organization profile and group assignment.
5. Provide the credentials to the organization.

### For Organizations

1. Log in using the organization credentials.
2. Open the organization dashboard.
3. Create a ticket-based event or a slot-based event.
4. Specify the event's description, price, and relevant inventory or slot details.
5. View the organization's events and bookings.
6. Check booking IDs and user details when validating tickets.
7. Mark bookings as consumed after use.
8. Open the analytics page to review event performance.

## Transaction Safety

Wallet operations and event bookings modify related database records. These operations must remain consistent to prevent problems such as duplicate bookings, overselling, or wallet balances being updated without corresponding booking records.

The booking implementation uses Django database transactions and row-level locking where supported.

### Booking Flow

The booking operation follows this general sequence:

1. Start an atomic database transaction.
2. Lock and retrieve the relevant event record.
3. For slot-based bookings, lock the selected slot.
4. Check the available ticket inventory or remaining slot capacity.
5. Verify that the user has sufficient wallet funds.
6. Deduct the booking cost from the wallet.
7. Update ticket inventory when the event is ticket-based.
8. Create the booking record.
9. Create the corresponding wallet transaction.
10. Complete the transaction.

If an error occurs during the atomic operation, database changes made within that transaction are rolled back.

Using row-level locks helps coordinate concurrent booking attempts. The precise guarantees depend on the database backend and its locking behaviour; PostgreSQL is used for this project.

Wallet deposits are simulated. No real payment gateway or actual money transfer is involved.

## References

- [Django Documentation](https://docs.djangoproject.com/en/6.1/)
- [Django Authentication System](https://docs.djangoproject.com/en/6.1/topics/auth/default/)
- [Django Database Transactions](https://docs.djangoproject.com/en/6.1/topics/db/transactions/)
- [Django QuerySet API — `select_for_update()`](https://docs.djangoproject.com/en/6.1/ref/models/querysets/#select-for-update)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [OWASP Top 10](https://devguide.owasp.org/en/02-foundations/05-top-ten/)
