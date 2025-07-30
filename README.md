# Interactive Chatbot Resume Website - Frontend

An interactive resume website where visitors can engage with an AI chatbot to discover professional experience, skills, and qualifications. Built with modern web technologies and deployed seamlessly via GitHub Pages.

🌐 **Live Demo**: [https://azizjonkasimov.github.io](https://azizjonkasimov.github.io)

## Overview

This repository contains the frontend application for the Interactive Chatbot Resume project. The website provides an engaging way for visitors to learn about your background through natural conversation with an AI-powered chatbot, rather than browsing a traditional static resume.

## Architecture

- **Frontend**: This repository (Vite + Vanilla JavaScript)
- **Backend**: [Chatbot Resume Website Backend](https://github.com/AzizjonKasimov/chatbot_resume_website_backend) (Django + Gemini AI)

## Features

### Core Functionality
- **AI-Powered Conversations**: Interactive chatbot that answers questions about your professional background
- **Dynamic API Integration**: Real-time responses from custom Django backend with Gemini AI
- **User Feedback System**: Collect visitor feedback and automatically send via email
- **Responsive Design**: Optimized experience across desktop, tablet, and mobile devices

### Deployment & Analytics
- **GitHub Pages Hosting**: Automatic deployment with zero configuration
- **CI/CD Pipeline**: Automated builds and deployments via GitHub Actions
- **Google Analytics**: Track visitor engagement and popular questions
- **SEO Optimization**: Google Search Console integration for better discoverability

## Tech Stack

- **Build Tool**: Vite (fast development and optimized builds)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: GitHub Pages with GitHub Actions
- **Analytics**: Google Analytics, Google Search Console

## Quick Start

### Prerequisites
- Node.js (version 20 or higher)
- npm or yarn package manager

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AzizjonKasimov/AzizjonKasimov.github.io.git
   cd your-frontend-repo
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   VITE_API_BASE_URL=https://your-backend-domain.com/
   ```
   
   For local development with backend running locally:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

### Deployment

#### GitHub Pages (Recommended)

1. **Enable GitHub Pages**
   - Go to your repository settings
   - Navigate to "Pages" section
   - Set source to "GitHub Actions"

2. **Automatic Deployment**
   - The included `.github/workflows/deploy.yml` handles automatic deployment
   - Simply push to the `main` branch to trigger deployment
   - Your site will be available at `https://your-username.github.io/repository-name`

## Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

## Customization

### Backend Integration
- Update `VITE_API_BASE_URL` in your `.env` file to point to your deployed backend
- Ensure your backend is configured with the appropriate CORS settings for your frontend domain

### Analytics Setup
- Add your Google Analytics tracking ID to the HTML template
- Configure Google Search Console for your domain

### Styling & Branding
- Modify CSS files to match your personal brand colors and typography
- Update favicon and meta tags for proper social media sharing

## License

This project is open source and available under the [MIT License](LICENSE).