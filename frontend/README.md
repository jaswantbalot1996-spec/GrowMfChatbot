# GrowMF Chatbot - Frontend (Next.js)

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local and set your API URL
   ```

3. **Start dev server**:
   ```bash
   npm run dev
   ```
   
   Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

### Deployment

#### Vercel (Recommended)
1. Push code to GitHub
2. Import repository in [Vercel](https://vercel.com)
3. Set environment variables
4. Deploy!

#### Docker
```bash
docker build -t growmf-frontend .
docker run -p 3000:3000 growmf-frontend
```

### Features
- ✅ Multi-language support (English/Hindi)
- ✅ Advanced filtering by risk, category, expense ratio
- ✅ Real-time chat interface
- ✅ Responsive design
- ✅ Dark mode
- ✅ Source citations

### Environment Variables

| Variable | Example | Required |
|----------|---------|----------|
| `NEXT_PUBLIC_API_URL` | `https://api.example.com` | ✅ |

### Troubleshooting

**"Cannot connect to API"**
- Verify `NEXT_PUBLIC_API_URL` starts with `http://` or `https://`
- Check backend is running and accessible
- Check browser console for CORS errors

**"Slow responses"**
- Could be backend latency
- Check network tab in DevTools
- Verify backend is scaling appropriately

### Support
See [DEPLOYMENT.md](../DEPLOYMENT.md) for full deployment guide
