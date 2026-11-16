# Razorpay Integration (React + FastAPI)

A production-ready Razorpay payment integration with:
- **FastAPI Backend**: Orders creation, payment signature verification, webhook processing (with idempotency), and SQLite database for persistent order records.
- **React (Vite) Frontend**: Clean checkout UI with Razorpay Checkout modal, support for Test & Live mode payments.

---

## 📁 Project Structure

```
razorpay-integration/
├── backend/
│   ├── app/
│   │   ├── catalog.py       # Products (includes ₹1 Live Test Item)
│   │   ├── config.py        # Settings with flexible CORS & env loading
│   │   ├── database.py      # SQLite DB (order saving & idempotent webhook updates)
│   │   ├── main.py          # FastAPI app & CORS middleware
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routers/
│   │   │   └── payments.py  # /orders, /verify, /webhook, /orders endpoints
│   │   └── services/
│   │       └── razorpay_service.py # Razorpay client & signature utilities
│   ├── .env.example
│   ├── Dockerfile           # Multi-cloud Docker deployment (Render, Railway, AWS)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.js           # API client with VITE_API_BASE_URL
│   │   ├── App.jsx          # Main store view
│   │   ├── components/      # UI components
│   │   └── hooks/           # Razorpay checkout hook
│   ├── .env.example
│   ├── vercel.json          # Vercel SPA routing
│   └── package.json
└── README.md
```

---

## 🚀 1. Local Development Setup

### Backend Setup:
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxxx
RAZORPAY_KEY_SECRET=xxxxxx
RAZORPAY_WEBHOOK_SECRET=your_test_secret
CORS_ORIGINS=["http://localhost:5173"]
```

Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. In dev mode, `/api` is proxied to `http://localhost:8000`.

---

## ⚙️ 2. Database & Idempotent Webhook Implementation

- **Order Creation (`POST /api/payments/orders`)**:
  Creates Razorpay order and saves order record in SQLite with status `created`.
- **Payment Verification (`POST /api/payments/verify`)**:
  Verifies payment signature using SHA-256 HMAC and updates status to `paid`.
- **Webhook Handling (`POST /api/payments/webhook`)**:
  - Verifies `X-Razorpay-Signature` with raw payload and `RAZORPAY_WEBHOOK_SECRET`.
  - Handles `payment.captured`: Idempotently marks order as `paid`. If Razorpay retries the webhook, duplicate updates are safely skipped.
  - Handles `refund.processed`: Marks order as `refunded` with `refund_id`.
- **Orders Inspection**:
  - `GET /api/payments/orders`: View all saved orders and their payment status.
  - `GET /api/payments/orders/{order_id}`: View a single order by ID.

---

## 🌐 3. Production Deployment Guide (HTTPS Mandatory)

### A. Deploy Backend (Render / Railway / AWS)

#### Option 1: Render
1. Push this repository to GitHub.
2. In Render Dashboard, click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3` or `Docker`
   - If Python:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `RAZORPAY_KEY_ID`: Your `rzp_live_...` or test key
   - `RAZORPAY_KEY_SECRET`: Your key secret
   - `RAZORPAY_WEBHOOK_SECRET`: Your webhook secret
   - `CORS_ORIGINS`: Your frontend URL, e.g. `https://your-frontend.vercel.app`
6. Deploy and note your backend URL (e.g. `https://your-backend.onrender.com`).

#### Option 2: Railway
1. Click **New Project** -> **Deploy from GitHub repo**.
2. Set root directory to `/backend`.
3. Add the same Environment Variables (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `CORS_ORIGINS`).

---

### B. Deploy Frontend (Vercel / Netlify)

#### Option 1: Vercel
1. In Vercel Dashboard, click **Add New...** -> **Project**.
2. Select your repository.
3. In **Root Directory**, click edit and select `frontend`.
4. Framework Preset: `Vite`.
5. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com` (no trailing slash)
6. Click **Deploy**.
7. Copy your deployed frontend URL (e.g. `https://your-store.vercel.app`) and add it to `CORS_ORIGINS` in your backend environment variables!

---

## 🔐 4. Live Mode Webhook Setup (Crucial!)

> ⚠️ **Important**: Razorpay Test mode and Live mode data are completely separate. A webhook configured in Test mode will **NOT** receive Live payments!

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/).
2. Switch toggle in header from **Test Mode** to **Live Mode**.
3. Navigate to **Account & Settings** -> **Webhooks** -> **Add New Webhook**.
4. Configure:
   - **Webhook URL**: `https://<your-backend-domain>/api/payments/webhook`
   - **Secret**: Enter a strong secret string (and paste this exact string in backend `RAZORPAY_WEBHOOK_SECRET`).
   - **Alert Email**: Your email.
   - **Active Events**:
     - `payment.captured` (mandatory for order confirmation)
     - `refund.processed` (for refund tracking)
5. Save Webhook.

---

## 🧪 5. Live Mode ₹1 Verification & Refund Testing

Before taking full customer transactions:
1. Ensure your backend has `RAZORPAY_KEY_ID` set to `rzp_live_...`.
2. Open your deployed store.
3. Select the **Live Test Item (₹1)**.
4. Pay ₹1 using any real UPI app (GPay, PhonePe, Paytm) or card.
5. Verify:
   - Checkout modal shows success.
   - Check `GET https://<your-backend-domain>/api/payments/orders` -> Order is marked `status: paid` with real `payment_id`.
   - In Razorpay Dashboard (Live Mode) -> **Transactions** -> **Payments**, the payment shows as **Captured**.
6. **Refund Test**:
   - In Razorpay Dashboard, open the ₹1 transaction.
   - Click **Issue Refund** -> Full refund.
   - Check backend logs / `/api/payments/orders`: Webhook captures `refund.processed` and updates status to `refunded`.
