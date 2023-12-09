document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('refresh').addEventListener('click', loadContainers);
    loadContainers(); // Initial load
    containerDropdown();
});

document.getElementById('startContainer').addEventListener('click', () => {
    const selectedImage = document.getElementById('containerSelect').value;
    fetch('http://localhost:3000/containers/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: selectedImage })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Chyba při spouštění kontejneru');
        } else {
            loadContainers();
        }
        return response.text();
    })
    .then(message => console.log(message))
    .catch(error => console.error('Chyba:', error));
});


function containerDropdown() {
    fetch('./config.json')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('containerSelect');
        data.forEach(container => {
            let option = document.createElement('option');
            option.value = container.image;
            option.text = container.name;
            select.appendChild(option);
        });
    });
}

function loadContainers() {
    fetch('http://localhost:3000/containers')
        .then(response => response.json())
        .then(containers => {
            const containersTable = document.getElementById('containersTable').getElementsByTagName('tbody')[0];
            containersTable.innerHTML = ''; // Clear existing rows
            const isRunningOnly = document.getElementById('runningOnly').checked;
            
            
            containers
            .filter(container => !isRunningOnly || container.State === 'running')
            .forEach(container => {
                let row = containersTable.insertRow();

                // Names
                row.insertCell(0).innerText = container.Names.join(', ');

                // Image
                row.insertCell(1).innerText = container.Image;

                // PublicPort:PrivatePort
                let ports = container.Ports.map(port => `${port.PublicPort}:${port.PrivatePort}`).join(', ');
                row.insertCell(2).innerText = ports;

                // State
                row.insertCell(3).innerText = container.State;

                // Status
                row.insertCell(4).innerText = container.Status;

                // Akce (Start/Stop/Restart buttons) - Přidáno podle potřeby
                let actionsCell = row.insertCell(5);
                let startButton = document.createElement('button');
                startButton.className = 'bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 m-2 rounded';
                startButton.innerText = 'Start';
                startButton.addEventListener('click', () => controlContainer(container.Id, 'start'));

                let stopButton = document.createElement('button');
                stopButton.innerText = 'Stop';
                stopButton.className = 'bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 m-2 rounded';
                stopButton.addEventListener('click', () => controlContainer(container.Id, 'stop'));

                let restartButton = document.createElement('button');
                restartButton.innerText = 'Restart';
                restartButton.className = 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 m-2 rounded';
                restartButton.addEventListener('click', () => controlContainer(container.Id, 'restart'));

                actionsCell.appendChild(startButton);
                actionsCell.appendChild(stopButton);
                actionsCell.appendChild(restartButton);

                let deleteButton = document.createElement('button');
                deleteButton.className = 'bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 m-2 rounded';
                deleteButton.innerText = 'X'
                deleteButton.addEventListener('click', () => {
                    if (confirm('Opravdu chcete smazat ' + container.Names[0] + '?')) {
                        deleteContainer(container.Id);
                    }
                });
                actionsCell.appendChild(deleteButton);

            });
        })
        .catch(error => console.error('Chyba při načítání kontejnerů:', error));
}
document.getElementById('runningOnly').addEventListener('change', loadContainers);


function controlContainer(containerId, action) {
    fetch(`http://localhost:3000/containers/${containerId}/${action}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                loadContainers();
                return response.text();
            } else {
                throw new Error('Chyba při provádění akce');
            }
        })
        .then(message => console.log(message))
        .catch(error => console.error('Chyba:', error));
}

function deleteContainer(containerId) {
    fetch(`http://localhost:3000/containers/${containerId}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                loadContainers();
                return response.text();
            } else {
                throw new Error('Chyba při mazání kontejneru');
            }
        })
        .then(message => console.log(message))
        .catch(error => console.error('Chyba:', error));
}
