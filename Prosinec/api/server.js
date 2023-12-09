const express = require('express');
const bodyParser = require('body-parser');
const Docker = require('dockerode');
const cors = require('cors');

const docker = new Docker({socketPath: '/var/run/docker.sock'});
const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

// Získání seznamu kontejnerů
app.get('/containers', async (req, res) => {
    try {
        const containers = await docker.listContainers({ all: true });
        res.json(containers);
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

// Start kontejneru
app.post('/containers/:id/start', async (req, res) => {
    try {
        const container = docker.getContainer(req.params.id);
        await container.start();
        res.send('Kontejner spuštěn');
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

// Stop kontejneru
app.post('/containers/:id/stop', async (req, res) => {
    try {
        const container = docker.getContainer(req.params.id);
        await container.stop();
        res.send('Kontejner zastaven');
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

// Restart kontejneru
app.post('/containers/:id/restart', async (req, res) => {
    try {
        const container = docker.getContainer(req.params.id);
        await container.restart();
        res.send('Kontejner restartován');
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

// Spustit kontejner
app.post('/containers/start', async (req, res) => {
    try {
        const { image, environment } = req.body;
        const container = await docker.createContainer({
            Image: image,
            Env: environment
        });
        await container.start();
        res.send('Kontejner spuštěn');
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

app.delete('/containers/:id', async (req, res) => {
    try {
        const container = docker.getContainer(req.params.id);
        await container.remove({ force: true }); // force: true zajistí, že kontejner bude odstraněn i když běží
        res.send('Kontejner odstraněn');
    } catch (error) {
        res.status(500).send(error.toString());
    }
});


app.listen(port, () => {
    console.log(`Server běží na portu ${port}`);
});


