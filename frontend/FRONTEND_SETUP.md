# 🎨 Frontend Setup Guide

## 📦 Installation

```powershell
cd frontend

# Install dependencies
npm install

# Or if you prefer yarn
yarn install
```

## 🚀 Running the Frontend

```powershell
# Development mode (with hot reload)
npm run dev

# Build for production
npm run build

# Run production build
npm run start
```

The frontend will be available at: **http://localhost:3000**

---

## ✅ What's Included

### Pages
- ✅ `/` - Landing page with features
- ✅ `/auth/login` - Login page
- ⏳ `/auth/register` - Register page (create next)
- ⏳ `/dashboard` - Main dashboard (create next)
- ⏳ `/subjects/[id]` - Subject detail page (create next)

### Components
- ✅ Providers - React Query provider
- ✅ API utilities - Axios setup with interceptors
- ✅ Utils - Tailwind merge utilities

### Features
- ✅ Dark mode theme (default)
- ✅ Framer Motion animations
- ✅ Lucide React icons
- ✅ Toast notifications (Sonner)
- ✅ React Query for data fetching
- ✅ Axios with auth interceptors
- ✅ TypeScript support
- ✅ Tailwind CSS styling

---

## 🔧 Configuration

### Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### API Connection

The frontend is configured to connect to your FastAPI backend at `http://localhost:8000/api/v1`

---

## 📋 Next Steps

1. Install dependencies:
   ```powershell
   npm install
   ```

2. Run the development server:
   ```powershell
   npm run dev
   ```

3. Open http://localhost:3000

4. Test the login page with a user created via backend API

---

## 🎨 UI Theme

The frontend uses a modern dark theme with:
- Gradient backgrounds (slate-950 to blue-950)
- Glass-morphism effects
- Blue to purple gradient accents
- Smooth animations
- Responsive design

---

## 📦 Dependencies

All dependencies are in `package.json`:
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- React Query
- Axios
- React Hook Form
- Zod
- Lucide React
- Sonner (toasts)

---

## 🐛 Troubleshooting

### Port already in use
```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <process-id> /F

# Or use a different port
npm run dev -- -p 3001
```

### Module not found
```powershell
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

---

## ✨ Features to Add

The following pages need to be created:
- [ ] Register page
- [ ] Dashboard with subjects list
- [ ] Subject detail page with chat
- [ ] PDF upload interface
- [ ] Notes viewer
- [ ] Quiz interface
- [ ] Flashcards
- [ ] Profile settings

---

**Ready to go! Start the backend first, then the frontend.** 🚀
