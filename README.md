# URL Shortener App

This is final project for the cloud technologies course. It's a simple URL shortener website where you can paste a long URL and get a short one back.

---

## What it does

- You paste a long URL
- You get a short link
- When someone opens the short link it redirects them to the original URL
- There is also a table that shows all the links you shortened

---

## Technologies used

- Angular (frontend)
- Python FastAPI (backend)
- PostgreSQL (database)
- Nginx (to route traffic)
- Docker and Docker Compose

---

## How to run it

You need to have Docker installed on your computer.

```bash
git clone https://github.com/yuuhenblxxm-KBTU/huaweicloudfinalapp.git
cd huaweicloudfinalapp
docker compose up --build
```

Then open http://localhost in your browser and it should work.

To stop it:
```bash
docker compose down
```

---

## Project structure

```
├── backend/        # python fastapi code
├── frontend/       # angular app
├── nginx/          # nginx config
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## Architecture

There are 3 containers running:

1. **frontend** - the angular app served by nginx, also handles routing to the backend
2. **backend** - fastapi handles the api requests and shortening logic
3. **db** - postgresql database where all the links are stored

Nginx is configured to send `/api/` requests to the backend and everything else just loads the angular app.

---

## Extra features implemented

- **Database container** - postgresql runs in its own docker container and data is saved even if you restart
- **CI/CD pipeline** - github actions runs automatically on every push, it checks the python code and builds the frontend to make sure nothing is broken
- **Nginx as reverse proxy** - nginx routes requests between the frontend and backend

---

## API

| Method | URL | What it does |
|---|---|---|
| POST | /api/shorten | takes a url and returns a short code |
| GET | /api/links | returns all saved links |
| GET | /{short_code} | redirects to original url |