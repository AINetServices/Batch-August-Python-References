const express = require('express');
const cors = require('cors');
const app = express();

// Configure CORS properly
app.use(cors({
  origin: 'http://localhost:5173', // Your Vite frontend
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Handle preflight requests
app.options('*', cors());

app.use(express.json());

app.post('/api/process-resume', async (req, res) => {
  try {
    const { resume_url, role_name, organization_name, user_id, application_id } = req.body;
    
    console.log('Processing resume request:', { 
      resume_url, 
      role_name, 
      organization_name,
      user_id,
      application_id 
    });
    
    // Add proper validation
    if (!resume_url || !role_name || !organization_name) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields' 
      });
    }
    
    // Simulate processing
    console.log('Simulating resume processing...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return success response
    res.json({ 
      success: true, 
      message: 'Resume processed successfully',
      data: {
        application_id: application_id,
        status: 'processing',
        extracted_data: {
          skills: ['JavaScript', 'React', 'Node.js'],
          experience: '5 years',
          references: 3
        }
      }
    });
    
  } catch (error) {
    console.error('Error processing resume:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    });
  }
});

// Add a health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Backend is running' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`âœ… Backend server running on http://localhost:${PORT}`);
  console.log(`í³‹ Health check: http://localhost:${PORT}/api/health`);
});
