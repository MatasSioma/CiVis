# CiVis

Django REST API + Vue.js + PostgreSQL (pgvector) — fully dockerized.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

## Getting Started

```bash
# Build and start all services
docker compose up --build

# Run database migrations (first time or after model changes)
docker compose exec backend python manage.py migrate

# Create a Django superuser (optional, for /admin access)
docker compose exec backend python manage.py createsuperuser
```

| Service  | URL                         |
|----------|-----------------------------|
| Frontend | http://localhost:5173       |
| API      | http://localhost:8000/api/  |
| Admin    | http://localhost:8000/admin/ |

## Project Structure

```
├── docker-compose.yml
├── backend/                  # Django REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/               # Django project settings, urls, wsgi/asgi
│   └── api/                  # App: models, serializers, views, urls
│       └── migrations/
└── frontend/                 # Vue.js SPA
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/           # Vue Router config
        ├── views/            # Page-level components
        └── assets/scss/      # Bootstrap SCSS customization
            ├── main.scss         # Entry point — imports everything
            ├── _variables.scss   # Override Bootstrap variables BEFORE import
            └── _overrides.scss   # Custom styles AFTER Bootstrap
```

## Development Workflow

### Backend

All backend commands run inside the container:

```bash
# Start a shell inside the backend container
docker compose exec backend bash

# Run migrations after changing models
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Install a new Python package
# 1. Add it to backend/requirements.txt
# 2. Rebuild the container
docker compose up --build backend
```

Django auto-reloads on file changes — the `backend/` directory is mounted into the container.

### Frontend

The Vite dev server hot-reloads on save. The `frontend/` directory is mounted into the container.

```bash
# Install a new npm package
docker compose exec frontend npm install <package-name>

# Or run any npm command
docker compose exec frontend npm run <script>
```

API requests from the frontend are proxied: any fetch to `/api/...` is forwarded to the backend container automatically (configured in `vite.config.js`).

### Customizing Bootstrap

Edit the SCSS files in `frontend/src/assets/scss/`:

1. **`_variables.scss`** — Override Bootstrap variables (colors, fonts, spacing, etc.) *before* Bootstrap is imported. See all available variables in `node_modules/bootstrap/scss/_variables.scss`.
2. **`_overrides.scss`** — Write custom CSS rules that apply *after* Bootstrap, so they take precedence.
3. **`main.scss`** — The entry point that wires it all together. Normally you don't need to edit this.

### Database

PostgreSQL runs with the pgvector extension pre-installed. The `Document` model includes a `VectorField` (1536 dimensions) ready for storing embeddings.

```bash
# Connect to the database directly
docker compose exec db psql -U civis -d civis

# Stop everything and remove volumes (resets DB data)
docker compose down -v
```

### Stopping

```bash
# Stop containers (preserves data)
docker compose down

# Stop and delete all data
docker compose down -v
```

---

## Vue Router

Vue Router maps URL paths to Vue components. The config lives in `frontend/src/router/index.js`:

```js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/about", name: "about", component: AboutView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
```

**Adding a new page:**

1. Create a `.vue` file in `frontend/src/views/` (e.g. `SettingsView.vue`).
2. Add a route entry in `router/index.js`:
   ```js
   import SettingsView from "../views/SettingsView.vue";

   // add to the routes array:
   { path: "/settings", name: "settings", component: SettingsView }
   ```
3. Optionally add a `<router-link to="/settings">` in `App.vue` for navigation.

**Key concepts:**

- `<router-view />` in `App.vue` renders the matched component.
- `<router-link to="/path">` creates client-side navigation links (no page reload).
- **Views** (`src/views/`) are page-level components tied to routes.
- **Components** (`src/components/`) are reusable pieces used inside views.
- Route params: `{ path: "/docs/:id", component: DocDetail }` — access via `useRoute().params.id`.

---

## Django REST API

The API follows a consistent pattern: **Model → Serializer → ViewSet → URL**.

### 1. Define a Model

In `backend/api/models.py`:

```python
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Then generate and run the migration:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### 2. Create a Serializer

In `backend/api/serializers.py`:

```python
from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["created_at"]
```

The serializer converts model instances to/from JSON and handles validation.

### 3. Create a ViewSet

In `backend/api/views.py`:

```python
from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = ProjectSerializer
```

`ModelViewSet` provides list, create, retrieve, update, and delete out of the box.

### 4. Register the URL

In `backend/api/urls.py`:

```python
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
```

This generates the following endpoints automatically:

| Method | URL                    | Action          |
|--------|------------------------|-----------------|
| GET    | `/api/projects/`       | List all        |
| POST   | `/api/projects/`       | Create          |
| GET    | `/api/projects/:id/`   | Retrieve one    |
| PUT    | `/api/projects/:id/`   | Full update     |
| PATCH  | `/api/projects/:id/`   | Partial update  |
| DELETE | `/api/projects/:id/`   | Delete          |

### Quick Summary

To add a new API resource, repeat steps 1–4: model, serializer, viewset, router registration. Each new resource gets full CRUD with no extra wiring.
