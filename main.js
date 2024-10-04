const express = require('express');
const mongoose = require('mongoose');
const passport = require('passport');
const cookieParser = require('cookie-parser');
const authRoutes = require('./routes/auth.route');
const participantRoutes = require('./routes/participant.route');
const postRoutes = require('./routes/post.route');
const cors=require('cors');
require('dotenv').config();
require('./config/passport')(passport);

const app = express();

// Middleware
app.use(express.json());
app.use(cookieParser());
app.use(passport.initialize());
app.use(cors(
    {
        origin: '*',
        credentials: true
    }
));
// Routes
app.use('/auth', authRoutes);
app.use('/api/participant', participantRoutes);
app.use('/api/posts', postRoutes);
app.get('/', (req, res) => {
  res.send('Welcome to Lenscape API').status(200);
}
);


// MongoDB Connection
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => {
    console.log('Connected to MongoDB');
  })
  .catch((err) => {
    console.error('MongoDB connection error:', err);
  });

// Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
