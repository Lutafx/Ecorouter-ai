require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { requestLogger } = require('./middleware/logger');
const { validateApiKey, DEMO_KEY } = require('./middleware/auth');
const chatRoutes = require('./routes/chat');
const dashboardRoutes = require('./routes/dashboard');
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(requestLogger);

// Serve static dashboard files
app.use(express.static(path.join(__dirname, 'public')));

// Public routes (no auth needed)
app.use('/api', dashboardRoutes);
app.use('/api', authRoutes);

// Demo route (no auth, no OpenAI key needed)
app.use('/v1', chatRoutes);

// API info
app.get('/v1', (req, res) => {
  res.json({
    name: 'EcoRouter AI API',
    version: '1.0.0',
    description: 'Smart AI proxy that reduces energy consumption by routing requests to optimal models',
    endpoints: {
      chat: 'POST /v1/chat/completions — OpenAI-compatible endpoint (needs OPENAI_API_KEY)',
      demo: 'POST /v1/chat/demo — Demo endpoint (no API key needed)',
      stats: 'GET /api/stats — Current statistics',
      daily: 'GET /api/stats/daily — Daily breakdown',
      hourly: 'GET /api/stats/hourly — Hourly breakdown',
      models: 'GET /api/models — Available models',
      report: 'GET /api/report — ESG report',
      health: 'GET /api/health — Health check',
      dashboard: 'GET / — Web dashboard'
    },
    demo_key: DEMO_KEY,
    docs: 'https://github.com/your-repo/ecorouter-ai'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: { message: `Route ${req.method} ${req.path} not found`, type: 'not_found' }
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('💥 Server error:', err.message);
  res.status(500).json({
    error: { message: 'Internal server error', type: 'server_error' }
  });
});

app.listen(PORT, () => {
  console.log('');
  console.log('==================================================');
  console.log('🌱 EcoRouter AI — Green AI Proxy');
  console.log('==================================================');
  console.log(`🚀 Server:     http://localhost:${PORT}`);
  console.log(`🏠 Landing:    http://localhost:${PORT}/`);
  console.log(`📊 Dashboard:  http://localhost:${PORT}/dashboard.html`);
  console.log(`📡 API Info:   http://localhost:${PORT}/v1`);
  console.log(`💚 Health:     http://localhost:${PORT}/api/health`);
  console.log(`🔑 Demo Key:   ${DEMO_KEY}`);
  console.log('==================================================');
  console.log('');
});

module.exports = app;
