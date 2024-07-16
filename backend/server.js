const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const csv = require('csv-parser');
const cors = require('cors'); // Import the cors package

const app = express();
const port = 8002;

// Use the cors middleware
app.use(cors());

const upload = multer({ dest: path.join(__dirname, 'uploads') });

app.post('/upload', upload.single('file'), (req, res) => {
    const uploadedFilePath = req.file.path;
    const outputFilePath = path.join(__dirname, 'employee_performance_ratings.csv');

    const pythonProcess = spawn('python3', ['script.py', uploadedFilePath, outputFilePath]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
        if (code === 0) {
            const results = [];
            fs.createReadStream(outputFilePath)
                .pipe(csv())
                .on('data', (data) => results.push(data))
                .on('end', () => {
                    res.json(results);
                });
        } else {
            res.status(500).send('An error occurred while processing the file.');
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
