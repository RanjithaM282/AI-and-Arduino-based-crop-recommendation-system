// Fix for missing /sensor route
// Add this to your existing backend file

const express = require('express');
const app = express();

// ADD THIS ROUTE TO YOUR BACKEND
app.get('/sensor', (req, res) => {
    res.json({
        temp: 33.5,
        hum: 35.7,
        soil: 100
    });
});

// Keep your existing routes below this line
// ... your other app routes ...

app.listen(5000, () => {
    console.log('Backend server running on http://localhost:5000');
});
