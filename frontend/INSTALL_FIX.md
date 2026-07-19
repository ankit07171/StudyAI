# 🔧 Fix: Missing autoprefixer

## Error
```
Error: Cannot find module 'autoprefixer'
```

## Solution

Run this command in the `frontend` folder:

```powershell
cd frontend
npm install autoprefixer --save-dev
```

Or install all PostCSS dependencies together:

```powershell
npm install -D autoprefixer postcss tailwindcss
```

## Alternative: Use yarn

If npm is not working:

```powershell
yarn add -D autoprefixer
```

## Verify Installation

After installation, check that it's installed:

```powershell
npm list autoprefixer
```

You should see something like:
```
studyai-frontend@0.1.0
└── autoprefixer@10.4.20
```

## Then Restart Dev Server

```powershell
npm run dev
```

The frontend should now work at http://localhost:3000

---

## Why This Happened

The `package.json` was missing `autoprefixer` in devDependencies. I've updated it now, but you need to run `npm install` to actually download the package.
