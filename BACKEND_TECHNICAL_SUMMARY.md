# InGazo Backend - Technical Summary

> **Project:** Carpooling application for Hungarian commuters traveling to Austria (ingázó)
> **Backend Framework:** Django 5.0+ with Django REST Framework
> **Database:** PostgreSQL 15 with PostGIS 3.4 (geospatial)
> **Status:** Backend API structure complete, ready for frontend integration

---

## 🛠️ Technology Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime |
| Django | 5.0+ | Web framework |
| Django REST Framework | 3.14+ | REST API |
| djangorestframework-simplejwt | 5.3+ | JWT authentication |

### Database & Caching
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15 | Primary database |
| PostGIS | 3.4 | Geospatial queries (distance, radius search) |
| Redis | 7 | Caching, Celery broker, session storage |
| psycopg2-binary | 2.9+ | PostgreSQL adapter |

### Background Tasks
| Technology | Version | Purpose |
|------------|---------|---------|
| Celery | 5.3+ | Async task queue |
| Redis | 7 | Message broker for Celery |

### API & Documentation
| Technology | Version | Purpose |
|------------|---------|---------|
| drf-spectacular | 0.27+ | OpenAPI/Swagger documentation |
| django-filter | 23.5+ | Query filtering |
| django-cors-headers | 4.3+ | CORS handling |

### Development & Testing
| Technology | Version | Purpose |
|------------|---------|---------|
| pytest | 7.4+ | Testing framework |
| pytest-django | 4.7+ | Django test integration |
| factory-boy | 3.3+ | Test fixtures |
| flake8 | 6.1+ | Linting |
| black | 23.0+ | Code formatting |
| isort | 5.12+ | Import sorting |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Gunicorn | Production WSGI server |
| Nginx | Reverse proxy (production) |

---

## 📁 Project Structure

```
backend/
├── core/                          # Django project configuration
│   ├── settings/
│   │   ├── base.py               # Shared settings
│   │   ├── dev.py                # Development overrides
│   │   └── prod.py               # Production settings
│   ├── urls.py                   # Root URL configuration
│   ├── celery.py                 # Celery configuration
│   ├── wsgi.py                   # WSGI entry point
│   └── asgi.py                   # ASGI entry point
│
├── apps/                          # Django applications
│   ├── users/                    # User management
│   ├── drivers/                  # Driver profiles & documents
│   ├── vehicles/                 # Vehicle management
│   ├── rides/                    # Ride management & matching
│   ├── bookings/                 # Booking system
│   ├── notifications/            # Notification system
│   └── reviews/                  # Review/rating system
│
├── docker-compose.yml            # Development containers
├── docker-compose.prod.yml       # Production containers
├── Dockerfile                    # Multi-stage Docker build
├── Makefile                      # Development commands
├── requirements.txt              # Python dependencies
└── manage.py                     # Django CLI
```

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │───────│   Driver    │───────│   Vehicle   │
│  (UUID PK)  │ 1:1   │  (UUID PK)  │ 1:N   │  (UUID PK)  │
└─────────────┘       └─────────────┘       └─────────────┘
      │                     │                     │
      │                     │                     │
      │               ┌─────┴─────┐               │
      │               │           │               │
      │               ▼           ▼               │
      │        ┌───────────┐  ┌──────────────┐   │
      │        │   Ride    │  │RideRecurring │   │
      │        │(UUID PK)  │  │  (UUID PK)   │   │
      │        │ PostGIS   │  │   PostGIS    │   │
      │        └───────────┘  └──────────────┘   │
      │              │                           │
      │              │                           │
      ▼              ▼                           │
┌─────────────┐  ┌─────────────┐                 │
│  Booking    │  │  RideStop   │                 │
│ (UUID PK)   │  │  (UUID PK)  │                 │
└─────────────┘  │   PostGIS   │                 │
      │          └─────────────┘                 │
      │                                          │
      ▼                                          │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Review    │  │Notification │  │DriverDoc   │
│ (UUID PK)   │  │  (UUID PK)  │  │ (UUID PK)  │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Model Details

#### 1. User (`apps.users.models.User`)
Custom user model with UUID primary key.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | EmailField | Unique, nullable |
| phone_number | CharField | Unique, nullable, validated format |
| full_name | CharField | User's display name |
| profile_photo_url | URLField | Profile image URL |
| is_active | BooleanField | Account active status |
| is_staff | BooleanField | Admin access |
| is_verified | BooleanField | Account verification status |
| created_at | DateTimeField | Auto-set on creation |
| updated_at | DateTimeField | Auto-updated |
| last_login | DateTimeField | Last login timestamp |

**Authentication:** Email-based (`USERNAME_FIELD = 'email'`)

---

#### 2. Driver (`apps.drivers.models.Driver`)
Driver profile extending User.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | OneToOneField | Link to User |
| license_number | CharField | Unique driver's license |
| license_expiry | DateField | License expiration |
| license_photo_url | URLField | License image |
| rating | FloatField | Average rating (0-5) |
| total_trips | PositiveIntegerField | Completed trip count |
| total_reviews | PositiveIntegerField | Review count |
| is_verified | BooleanField | Admin-verified driver |
| is_active | BooleanField | Currently active |
| bio | TextField | Driver description |
| accepts_smoking | BooleanField | Preference |
| accepts_pets | BooleanField | Preference |
| accepts_luggage | BooleanField | Preference |

**Methods:**
- `update_rating(new_rating)` - Recalculates weighted average
- `increment_trips()` - Increments trip counter

---

#### 3. DriverDocument (`apps.drivers.models.DriverDocument`)
Verification documents for drivers.

| Field | Type | Choices |
|-------|------|---------|
| document_type | CharField | license, insurance, registration, id_card, other |
| status | CharField | pending, approved, rejected, expired |
| document_url | URLField | Document image/PDF |
| expiry_date | DateField | Document expiration |
| rejection_reason | TextField | If rejected |
| reviewed_by | ForeignKey | Admin who reviewed |

---

#### 4. Vehicle (`apps.vehicles.models.Vehicle`)
Vehicles registered by drivers.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| driver | ForeignKey | Owner driver |
| make | CharField | Manufacturer (Toyota, BMW) |
| model | CharField | Model name |
| year | PositiveIntegerField | Manufacturing year (1990-2026) |
| license_plate | CharField | Unique plate number |
| color | CharField | Choices: black, white, silver, etc. |
| seats | PositiveIntegerField | Passenger capacity (1-9) |
| photo_url | URLField | Vehicle photo |
| has_air_conditioning | BooleanField | Feature flag |
| has_wifi | BooleanField | Feature flag |
| has_usb_charger | BooleanField | Feature flag |
| trunk_space | CharField | small, medium, large |
| is_active | BooleanField | Available for rides |
| is_verified | BooleanField | Admin verified |

---

#### 5. Ride (`apps.rides.models.Ride`)
Single trip rides with **PostGIS geospatial data**.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| driver | ForeignKey | Driver offering ride |
| vehicle | ForeignKey | Vehicle used |
| departure_time | DateTimeField | When ride starts |
| seats_total | PositiveIntegerField | Total passenger seats (1-9) |
| seats_available | PositiveIntegerField | Currently available |
| **start_location** | **PointField** | **PostGIS geographic point (lat/lng)** |
| **end_location** | **PointField** | **PostGIS geographic point (lat/lng)** |
| start_city | CharField | Human-readable city name |
| start_address | CharField | Full address |
| end_city | CharField | Destination city |
| end_address | CharField | Destination address |
| price_per_seat | DecimalField | Price in EUR |
| estimated_duration_minutes | PositiveIntegerField | Trip duration |
| estimated_distance_km | DecimalField | Trip distance |
| status | CharField | scheduled, ongoing, finished, cancelled |
| notes | TextField | Additional info |
| allows_detours | BooleanField | Can make pickup detours |
| instant_booking | BooleanField | No approval needed |

**Methods:**
- `reserve_seats(count)` - Atomically reserve seats
- `release_seats(count)` - Release cancelled seats
- `is_full` (property) - Check if fully booked

**PostGIS Features:**
- `PointField` with SRID 4326 (WGS 84 GPS coordinates)
- Spatial indexing enabled for fast queries
- Supports distance calculations and radius searches

---

#### 6. RideStop (`apps.rides.models.RideStop`)
Intermediate stops on a ride.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| ride | ForeignKey | Parent ride |
| name | CharField | Stop name |
| **location** | **PointField** | **PostGIS point** |
| address | CharField | Full address |
| order | PositiveIntegerField | Stop order (1, 2, 3...) |
| estimated_arrival | DateTimeField | ETA at this stop |
| price_from_start | DecimalField | Price to this stop |

---

#### 7. RideRecurring (`apps.rides.models.RideRecurring`)
Weekly recurring ride templates (for commuters).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| driver | ForeignKey | Driver |
| vehicle | ForeignKey | Vehicle |
| days_of_week | ArrayField | [0,1,2,3,4] = Mon-Fri |
| time_of_day | TimeField | Daily departure time |
| start_location | PointField | PostGIS point |
| end_location | PointField | PostGIS point |
| valid_from | DateField | Template start date |
| valid_until | DateField | Template end date (optional) |
| is_active | BooleanField | Currently active |

---

#### 8. Booking (`apps.bookings.models.Booking`)
Passenger reservations.

| Field | Type | Choices |
|-------|------|---------|
| id | UUID | Primary key |
| ride | ForeignKey | Booked ride |
| user | ForeignKey | Passenger |
| seats_reserved | PositiveIntegerField | Number of seats (1-9) |
| status | CharField | pending, confirmed, cancelled, completed, rejected, no_show |
| price | DecimalField | Total price |
| payment_status | CharField | pending, paid, refunded, failed |
| payment_reference | CharField | External payment ID |
| pickup_note | TextField | Pickup instructions |
| passenger_message | TextField | Message to driver |
| driver_message | TextField | Driver's response |
| confirmed_at | DateTimeField | When confirmed |
| cancelled_at | DateTimeField | When cancelled |
| cancellation_reason | TextField | Why cancelled |

**Methods:**
- `confirm()` - Confirm booking, reserve seats
- `cancel(cancelled_by, reason)` - Cancel and release seats
- `complete()` - Mark as completed
- `reject(reason)` - Driver rejects booking

**Constraints:**
- Unique constraint: One active booking per user per ride

---

#### 9. Review (`apps.reviews.models.Review`)
Rating system for drivers and passengers.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| ride | ForeignKey | Related ride |
| reviewer | ForeignKey | User giving review |
| target | ForeignKey | User being reviewed |
| review_type | CharField | driver (passenger→driver) or passenger (driver→passenger) |
| rating | PositiveIntegerField | 1-5 stars |
| comment | TextField | Review text |
| response | TextField | Target's response |
| is_visible | BooleanField | Publicly visible |
| is_flagged | BooleanField | Flagged for moderation |

**Auto-behavior:**
- Creating a driver review automatically updates driver's average rating

---

#### 10. Notification (`apps.notifications.models.Notification`)
Push/email notification system.

| Field | Type | Choices |
|-------|------|---------|
| id | UUID | Primary key |
| user | ForeignKey | Recipient |
| type | CharField | booking_request, booking_confirmed, ride_starting, new_review, etc. |
| title | CharField | Notification title |
| message | TextField | Notification body |
| priority | CharField | low, normal, high, urgent |
| is_read | BooleanField | Read status |
| push_sent | BooleanField | Push notification sent |
| email_sent | BooleanField | Email sent |
| reference_type | CharField | Related object type (ride, booking) |
| reference_id | UUIDField | Related object ID |
| action_url | CharField | Deep link URL |
| metadata | JSONField | Additional data |

---

#### 11. NotificationPreference (`apps.notifications.models.NotificationPreference`)
User notification settings.

| Field | Type | Default |
|-------|------|---------|
| email_booking_updates | BooleanField | True |
| email_ride_reminders | BooleanField | True |
| email_promotional | BooleanField | False |
| push_booking_updates | BooleanField | True |
| push_ride_reminders | BooleanField | True |
| push_chat_messages | BooleanField | True |
| push_promotional | BooleanField | False |

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/token/` | Get JWT tokens (login) |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register/` | Create new user |
| GET | `/api/v1/users/me/` | Get current user profile |
| PATCH | `/api/v1/users/me/` | Update profile |
| POST | `/api/v1/users/change-password/` | Change password |

### Drivers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/drivers/` | List all drivers |
| POST | `/api/v1/drivers/` | Become a driver |
| GET | `/api/v1/drivers/{id}/` | Get driver details |
| GET | `/api/v1/drivers/me/` | Get own driver profile |
| PATCH | `/api/v1/drivers/me/` | Update driver profile |
| POST | `/api/v1/drivers/documents/` | Upload document |
| GET | `/api/v1/drivers/documents/` | List my documents |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/vehicles/` | List my vehicles |
| POST | `/api/v1/vehicles/` | Add vehicle |
| GET | `/api/v1/vehicles/{id}/` | Get vehicle details |
| PATCH | `/api/v1/vehicles/{id}/` | Update vehicle |
| DELETE | `/api/v1/vehicles/{id}/` | Remove vehicle |

### Rides
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rides/` | List rides (with filters) |
| POST | `/api/v1/rides/` | Create ride (drivers only) |
| GET | `/api/v1/rides/{id}/` | Get ride details |
| PATCH | `/api/v1/rides/{id}/` | Update ride |
| DELETE | `/api/v1/rides/{id}/` | Cancel ride |
| **POST** | **`/api/v1/rides/search/`** | **Geographic search** |
| GET | `/api/v1/rides/my_rides/` | Get driver's rides |
| POST | `/api/v1/rides/{id}/cancel/` | Cancel a ride |
| POST | `/api/v1/rides/{id}/start/` | Start a ride |
| POST | `/api/v1/rides/{id}/finish/` | Complete a ride |
| GET | `/api/v1/rides/{id}/stops/` | List ride stops |
| POST | `/api/v1/rides/{id}/stops/` | Add stop |

### Recurring Rides
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rides/recurring/` | List my recurring rides |
| POST | `/api/v1/rides/recurring/` | Create recurring template |
| PATCH | `/api/v1/rides/recurring/{id}/` | Update template |
| DELETE | `/api/v1/rides/recurring/{id}/` | Delete template |
| POST | `/api/v1/rides/recurring/{id}/toggle_active/` | Activate/deactivate |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/bookings/` | List my bookings |
| POST | `/api/v1/bookings/` | Create booking |
| GET | `/api/v1/bookings/{id}/` | Get booking details |
| POST | `/api/v1/bookings/{id}/confirm/` | Confirm booking (driver) |
| POST | `/api/v1/bookings/{id}/cancel/` | Cancel booking |
| POST | `/api/v1/bookings/{id}/reject/` | Reject booking (driver) |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reviews/` | List reviews |
| POST | `/api/v1/reviews/` | Create review |
| GET | `/api/v1/reviews/{id}/` | Get review |
| POST | `/api/v1/reviews/{id}/respond/` | Add response |
| POST | `/api/v1/reviews/{id}/flag/` | Flag for moderation |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | List my notifications |
| POST | `/api/v1/notifications/{id}/read/` | Mark as read |
| POST | `/api/v1/notifications/read_all/` | Mark all as read |
| GET | `/api/v1/notifications/preferences/` | Get preferences |
| PATCH | `/api/v1/notifications/preferences/` | Update preferences |

---

## 🔍 Geographic Search (PostGIS)

### Search API Request
```json
POST /api/v1/rides/search/
{
  "start_lat": 47.6816,
  "start_lng": 16.5908,
  "end_lat": 48.2082,
  "end_lng": 16.3738,
  "date": "2025-12-15",
  "min_seats": 1,
  "max_price": 15.00,
  "radius_km": 10.0
}
```

### How It Works
1. Creates PostGIS `Point` objects from coordinates
2. Uses `__distance_lte` filter with `D(km=radius)` for radius search
3. Annotates results with actual distances using `Distance()` function
4. Orders by closest match first

### PostGIS Query Example (internally)
```python
Ride.objects.filter(
    start_location__distance_lte=(start_point, D(km=10)),
    end_location__distance_lte=(end_point, D(km=10))
).annotate(
    start_distance=Distance('start_location', start_point)
).order_by('start_distance')
```

### Matching Utilities (`apps.rides.utils.matching`)
- `find_matching_rides()` - Main search function
- `calculate_route_compatibility()` - Returns 0-100 compatibility score
- `find_rides_along_route()` - Find rides passing through multiple points
- `suggest_pickup_point()` - Suggest best pickup for a passenger

---

## 🔐 Authentication Flow

### JWT Token Flow
1. User logs in: `POST /api/v1/auth/token/` with email/password
2. Receives: `{ "access": "...", "refresh": "..." }`
3. Access token expires in 60 minutes
4. Refresh token expires in 7 days
5. Use `POST /api/v1/auth/token/refresh/` with refresh token to get new access token

### Token Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Request Header
```
Authorization: Bearer <access_token>
```

---

## 🐳 Docker Setup

### Services (docker-compose.yml)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| db | postgis/postgis:15-3.4 | 5432 | Database with PostGIS |
| redis | redis:7-alpine | 6379 | Cache & Celery broker |
| backend | Custom Dockerfile | 8000 | Django API |
| celery_worker | Custom Dockerfile | - | Async task processing |
| celery_beat | Custom Dockerfile | - | Scheduled tasks |

### Quick Start
```bash
cd backend
make build      # Build images (first time)
make up         # Start all containers
make superuser  # Create admin user
make down       # Stop containers
```

### URLs (Development)
- API: http://localhost:8000/api/v1/
- Swagger Docs: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Admin Panel: http://localhost:8000/admin/

---

## 📋 What's Implemented vs TODO

### ✅ Fully Implemented
- [x] Custom User model with UUID and phone/email auth
- [x] JWT authentication with token refresh
- [x] Driver registration and document verification workflow
- [x] Vehicle management with features
- [x] Ride CRUD with PostGIS locations
- [x] Geographic ride search with radius
- [x] Ride stops (intermediate pickups)
- [x] Recurring ride templates
- [x] Booking system with seat management
- [x] Review/rating system with moderation
- [x] Notification model with preferences
- [x] Docker development environment
- [x] Swagger/OpenAPI documentation
- [x] Basic permission system

### 🚧 TODO / Future Enhancements
- [ ] SMS verification (Twilio/MessageBird integration)
- [ ] Push notification delivery (Firebase/OneSignal)
- [ ] Email sending (transactional emails)
- [ ] Payment integration (Stripe/Barion)
- [ ] Real-time location tracking (WebSockets)
- [ ] Chat/messaging between users
- [ ] Route polyline storage (full route, not just start/end)
- [ ] Traffic-aware matching
- [ ] Machine learning compatibility scoring
- [ ] Admin dashboard for document verification
- [ ] Celery tasks for ride reminders
- [ ] Rate limiting per endpoint
- [ ] Caching optimization

---

## 🧪 Testing

### Run Tests
```bash
make test           # Run in Docker
make test-local     # Run locally (needs DB)
```

### Test Configuration
- pytest with pytest-django
- factory-boy for fixtures
- Separate test database

---

## 📝 Code Style

### Formatting
```bash
make format    # Run black + isort
make lint      # Check with flake8
```

### Conventions
- Black formatter (line length 88)
- isort for imports
- Type hints encouraged
- Docstrings on all public methods

---

## 🔗 Related Documentation

- Django REST Framework: https://www.django-rest-framework.org/
- PostGIS: https://postgis.net/documentation/
- GeoDjango: https://docs.djangoproject.com/en/5.0/ref/contrib/gis/
- Simple JWT: https://django-rest-framework-simplejwt.readthedocs.io/
- Celery: https://docs.celeryq.dev/

---

*Generated for InGazo project - December 2025*

