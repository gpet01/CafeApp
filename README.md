# Café Aroma 55

Website for **Café Aroma 55** — a Greek family-owned café at 55 Wall St, Norwalk CT.  
Built with Flask, SQLite, and vanilla JS/CSS.

---

## Features

- Full menu display with category filter tabs (hot, iced, pastries, gelato, savory)
- Daily gelato flavors banner — updated from the admin panel
- Pre-order form (name, phone, item, pickup time)
- Newsletter subscription
- Admin dashboard: manage orders (pending → ready → done), view subscribers, update gelato flavors

---

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Clone & enter the project
git clone <repo-url>
cd "CafeAroma55 promax"

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD

# 5. Run
python main.py
```

The app will be available at `http://localhost:8000`.  
The database and admin account are created automatically on first run.

---

## Admin Panel

Go to `/admin/login` and sign in with the credentials from your `.env`.

From the dashboard you can:
- View and update order statuses (pending / ready / done)
- See newsletter subscribers
- Set today's gelato flavors (up to 4)

---

## Project Structure

```
├── main.py              # Flask app — routes, models, auth
├── data/
│   ├── menu.json        # Full menu (edit to update prices/items)
│   └── info.json        # Café details, hours, reviews, social links
├── templates/
│   ├── base.html
│   ├── index.html       # Public-facing page
│   ├── admin.html       # Admin dashboard
│   └── admin_login.html
├── static/
│   ├── styles.css
│   └── script.js
├── .env.example         # Environment variable template
└── requirements.txt
```

---

## Environment Variables

| Variable         | Description                              | Default              |
|------------------|------------------------------------------|----------------------|
| `SECRET_KEY`     | Flask session secret (use a long random string) | `dev-secret-key` |
| `FLASK_DEBUG`    | Enable debug mode (`true` / `false`)     | `false`              |
| `PORT`           | Port to listen on                        | `8000`               |
| `ADMIN_EMAIL`    | Admin login email                        | `admin@cafearoma55.com` |
| `ADMIN_PASSWORD` | Admin login password                     | `aroma2025`          |
| `DATABASE_URL`   | SQLAlchemy DB URL                        | `sqlite:///cafe_aroma.db` |

---

## Updating the Menu or Info

Edit [`data/menu.json`](data/menu.json) or [`data/info.json`](data/info.json) directly — no restart needed, files are read on every request.
