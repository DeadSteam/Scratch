# ScratchLab Frontend Development Plan

## Project Overview
Scientific application for analyzing scratch resistance of polymer films.
Frontend: Pure React 18 + Webpack (no Vite/CRA)
Design: Innovative, minimalist, serious scientific aesthetic

---

## Phase 1: Project Setup & Configuration

### 1.1 Initialize React Project with Webpack
- [x] Configure webpack.config.js (dev/prod modes)
- [x] Setup Babel for JSX
- [x] Configure ESLint
- [x] Setup CSS modules
- [x] Configure path aliases
- [x] Setup hot reload (webpack-dev-server)

### 1.2 Project Structure (SOLID Architecture)
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── index.jsx                    # Entry point
│   ├── App.jsx                      # Main app component
│   ├── api/                         # API layer (Single Responsibility)
│   │   ├── HttpClient.js            # Base HTTP client
│   │   ├── AuthService.js           # Auth API calls
│   │   ├── ExperimentService.js     # Experiments API
│   │   ├── FilmService.js           # Films API
│   │   ├── ConfigService.js         # Equipment configs API
│   │   ├── ImageService.js          # Images API
│   │   └── AnalysisService.js       # Analysis API
│   ├── components/                  # Reusable UI components
│   │   ├── common/                  # Generic components
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Modal/
│   │   │   ├── Card/
│   │   │   ├── Spinner/
│   │   │   └── ErrorBoundary/
│   │   ├── layout/
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   └── Layout/
│   │   └── features/
│   │       ├── ImageCarousel/
│   │       ├── ROISelector/
│   │       ├── ScratchChart/
│   │       └── ExperimentCard/
│   ├── pages/                       # Page components
│   │   ├── LoginPage/
│   │   ├── ExperimentsPage/
│   │   ├── CreateExperimentPage/
│   │   ├── ExperimentDetailPage/
│   │   └── AdminPage/
│   │       ├── UsersManagement/
│   │       ├── FilmsManagement/
│   │       └── ConfigsManagement/
│   ├── context/                     # React Context (State)
│   │   ├── AuthContext.jsx
│   │   └── NotificationContext.jsx
│   ├── hooks/                       # Custom hooks
│   │   ├── useAuth.js
│   │   ├── useApi.js
│   │   └── useFetch.js
│   ├── utils/                       # Utility functions
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   └── constants.js
│   └── styles/                      # Global styles
│       ├── variables.css
│       ├── reset.css
│       └── global.css
├── package.json
├── webpack.config.js
├── babel.config.js
├── .eslintrc.js
├── .prettierrc
└── Dockerfile
```

---

## Phase 2: Core Infrastructure

### 2.1 API Layer
- [ ] HttpClient with interceptors (auth, error handling)
- [ ] Request/response transformers
- [ ] Session storage for tokens
- [ ] Auto-refresh token logic
- [ ] Error handling service

### 2.2 Authentication System
- [ ] AuthContext provider
- [ ] Login/logout flows
- [ ] Protected routes wrapper
- [ ] Role-based access control
- [ ] Session persistence

### 2.3 Routing
- [ ] React Router v6 setup
- [ ] Route guards (authenticated/admin)
- [ ] Lazy loading for pages
- [ ] 404 handling

---

## Phase 3: UI Components

### 3.1 Design System
- [ ] CSS Variables (colors, typography, spacing)
- [ ] Color palette: Deep navy (#0a1628), Cyan accent (#00d4ff), 
      Warm gray (#2d3748), Error red (#ff4757)
- [ ] Typography: Inter/Roboto Mono for scientific data
- [ ] Transitions: 200ms ease-out
- [ ] Shadows & borders

### 3.2 Common Components
- [ ] Button (primary, secondary, danger, ghost)
- [ ] Input (text, number, password)
- [ ] Select (dropdown with search)
- [ ] Checkbox
- [ ] Modal
- [ ] Card
- [ ] Spinner/Loader
- [ ] Toast notifications
- [ ] Empty state
- [ ] Error boundary

### 3.3 Layout Components
- [ ] Header (logo, nav, user menu)
- [ ] Sidebar (admin navigation)
- [ ] Page layout wrapper
- [ ] Responsive grid

---

## Phase 4: Pages Implementation

### 4.1 Login Page
- [ ] Login form (username, password)
- [ ] Validation
- [ ] Error handling
- [ ] Redirect to experiments

### 4.2 Experiments List Page
- [ ] Fetch user experiments
- [ ] Experiment cards grid
- [ ] Empty state
- [ ] "New Experiment" button
- [ ] Pagination/infinite scroll

### 4.3 Create Experiment Page (Multi-step Wizard)
- [ ] Step 1: Configuration
  - Film type selector
  - Equipment config selector
  - Weight input
  - Has fabric checkbox
- [ ] Step 2: Image Upload
  - Reference image upload
  - Image preview
- [ ] Step 3: ROI Selection
  - Canvas-based rectangle selector
  - Coordinates display
  - Clear/reset selection
- [ ] Submit and redirect

### 4.4 Experiment Detail Page
- [ ] Experiment info header
- [ ] Image carousel component
  - Reference image
  - Scratched images by passes
  - Navigation arrows
  - Thumbnails
- [ ] Scratch index chart (Line chart)
  - X-axis: passes count
  - Y-axis: scratch index
  - Interactive tooltips
- [ ] Add image modal
  - Image upload
  - Passes count input
- [ ] Run analysis button
- [ ] Results display

### 4.5 Admin Panel
- [ ] Admin dashboard
- [ ] Users management (CRUD)
- [ ] Films management (CRUD)
- [ ] Equipment configs management (CRUD)
- [ ] Tables with sorting/filtering

---

## Phase 5: Advanced Features

### 5.1 ROI Selector Component
- [ ] Canvas overlay on image
- [ ] Mouse drag to create rectangle
- [ ] Resize handles
- [ ] Display coordinates in real-time
- [ ] Save coordinates to state

### 5.2 Image Carousel
- [ ] Smooth transitions
- [ ] Keyboard navigation
- [ ] Touch/swipe support
- [ ] Zoom on click
- [ ] Image metadata display

### 5.3 Charts Integration
- [ ] Chart.js + react-chartjs-2
- [ ] Line chart for scratch index progression
- [ ] Custom styling to match theme
- [ ] Export chart as image

---

## Phase 6: Testing & Optimization

### 6.1 Quality Assurance
- [ ] ESLint error fixes
- [ ] Accessibility audit (ARIA)
- [ ] Cross-browser testing
- [ ] Responsive design testing

### 6.2 Performance
- [ ] Code splitting
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Lazy loading

### 6.3 Docker Integration
- [ ] Frontend Dockerfile
- [ ] Nginx config for SPA
- [ ] Environment variables

---

## API Endpoints Reference

### Auth
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

### Users (Admin)
- GET /api/v1/users
- GET /api/v1/users/{id}
- PATCH /api/v1/users/{id}
- DELETE /api/v1/users/{id}

### Films
- GET /api/v1/films
- POST /api/v1/films
- PATCH /api/v1/films/{id}
- DELETE /api/v1/films/{id}

### Equipment Configs
- GET /api/v1/equipment-configs
- POST /api/v1/equipment-configs
- PATCH /api/v1/equipment-configs/{id}
- DELETE /api/v1/equipment-configs/{id}

### Experiments
- GET /api/v1/experiments
- GET /api/v1/experiments/user/{user_id}
- GET /api/v1/experiments/{id}
- GET /api/v1/experiments/{id}/with-images
- POST /api/v1/experiments
- PATCH /api/v1/experiments/{id}
- DELETE /api/v1/experiments/{id}

### Images
- GET /api/v1/images/experiment/{experiment_id}
- POST /api/v1/images/upload (multipart)
- DELETE /api/v1/images/{id}

### Analysis
- POST /api/v1/analysis/scratch-resistance
- GET /api/v1/analysis/histogram/{image_id}

---

## Design Specifications

### Color Palette
- Background Primary: #0a1628 (Deep navy)
- Background Secondary: #111827 (Dark slate)
- Surface: #1e293b (Card background)
- Border: #334155 (Subtle borders)
- Accent Primary: #00d4ff (Cyan - actions)
- Accent Secondary: #06b6d4 (Teal)
- Text Primary: #f1f5f9 (Light gray)
- Text Secondary: #94a3b8 (Muted)
- Success: #10b981 (Green)
- Warning: #f59e0b (Amber)
- Error: #ef4444 (Red)

### Typography
- Font Family: 'Inter', -apple-system, sans-serif
- Monospace: 'JetBrains Mono', monospace (for data)
- Headings: 600 weight
- Body: 400 weight

### Spacing Scale
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

---

## Current Progress
- [x] Backend API ready
- [x] Docker configuration ready
- [x] Frontend development completed
- [x] ESLint configured and errors fixed
- [x] Production build successful (429 KiB)

