const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors({
  origin: 'http://localhost:8000',
  credentials: true
}));

app.use(express.json());