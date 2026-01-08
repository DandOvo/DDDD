# Cloud Media Platform - Frontend

A modern, cloud-native multimedia sharing platform built with Angular and Tailwind CSS.

## Features

- **User Authentication** - Secure login and registration system
- **Media Upload** - Support for images and videos (up to 100MB)
- **Media Management** - View, edit, and delete media files
- **Search & Filter** - Find media by name, description, or tags
- **Responsive Design** - Mobile-friendly interface with Tailwind CSS
- **Cloud Integration** - Powered by Azure services

## Technology Stack

### Frontend
- **Angular 17** - Modern web application framework
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type-safe development
- **RxJS** - Reactive programming

### Backend (Azure Services)
- **Azure Blob Storage** - Media file storage
- **Azure Cosmos DB** - NoSQL database for metadata
- **Azure Logic Apps** - REST API implementation
- **Azure Static Web Apps** - Frontend hosting

## Prerequisites

- Node.js 18+ and npm
- Angular CLI (`npm install -g @angular/cli`)
- Azure subscription with access to required services

## Installation

1. Clone the repository:
```bash
cd 设计/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
   - Update `src/environments/environment.ts` with your Azure endpoints
   - Update `src/environments/environment.prod.ts` for production

## Development

Start the development server:
```bash
npm start
```

Navigate to `http://localhost:4200/`

## Build

Build for production:
```bash
npm run build
```

Build artifacts will be stored in the `dist/` directory.

## Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── auth/              # Authentication components
│   │   ├── media/             # Media management components
│   │   └── shared/            # Shared components (navbar, footer)
│   ├── guards/                # Route guards
│   ├── models/                # TypeScript interfaces
│   ├── services/              # API services and interceptors
│   ├── app-routing.module.ts  # Route configuration
│   ├── app.module.ts          # Main module
│   └── app.component.ts       # Root component
├── assets/                    # Static assets
├── environments/              # Environment configuration
├── styles.css                 # Global styles with Tailwind
└── index.html                 # Main HTML file
```

## Features Overview

### Authentication
- User registration with email validation
- Secure login with JWT tokens
- Protected routes with auth guards

### Media Upload
- Drag-and-drop file upload
- File type validation (images and videos)
- File size validation (max 100MB)
- Description and tags support
- Upload progress indicator

### Media Gallery
- Grid layout with responsive design
- Thumbnail previews
- Filter by media type (all/images/videos)
- Search functionality
- Pagination support

### Media Detail View
- Full-size media display
- Video player for video files
- Edit metadata (description and tags)
- Delete media with confirmation
- Detailed file information

## API Integration

The frontend integrates with Azure Logic Apps REST API. See the `/接口.md` file for complete API documentation.

Key endpoints:
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /media` - List user's media
- `POST /media` - Upload media file
- `GET /media/{id}` - Get media details
- `PUT /media/{id}` - Update media metadata
- `DELETE /media/{id}` - Delete media
- `GET /media/search` - Search media

## Azure Deployment

### Deploy to Azure Static Web Apps

1. Build the production version:
```bash
npm run build
```

2. Deploy using Azure CLI:
```bash
az staticwebapp create \
  --name cloud-media-platform \
  --resource-group your-resource-group \
  --source ./dist/cloud-media-platform \
  --location "UK South" \
  --branch main \
  --app-location "/" \
  --output-location "dist/cloud-media-platform"
```

3. Configure custom domain (optional)
4. Enable CI/CD with GitHub Actions

## Security

- JWT-based authentication
- HTTP-only token storage
- Protected routes with guards
- CORS configuration for API calls
- File type and size validation
- XSS protection through Angular sanitization

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
