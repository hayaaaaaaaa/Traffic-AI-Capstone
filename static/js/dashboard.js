setInterval(() => {
    fetch('/telemetry')
        .then(r => r.json())
        .then(data => {
            // 1. Update Basic Metrics
            document.getElementById('decision').innerText = data.decision;
            document.getElementById('r1').innerText = data.r1;
            document.getElementById('r2').innerText = data.r2;
            document.getElementById('timer').innerText = data.time_index + "s / 54s";
            document.getElementById('sys-log').innerText = `> ${data.log}`;

            // 2. Update Technical Data with Color Coding
            const confBox = document.getElementById('conf');
            const confValue = parseFloat(data.conf); // Extract number
            confBox.innerText = data.conf;
            document.getElementById('latency').innerText = `Latency: ${data.latency}`;

            // REALISM: Change color based on confidence fluctuation
            if (confValue > 92.0) {
                confBox.style.color = "#57ce57ff"; // High Confidence
            } else {
                confBox.style.color = "#ffcc00"; // Medium Confidence (Realistic)
            }

            // 3. Visual Decisions
            const dBox = document.getElementById('decision');
            if (data.decision === "ROAD1") {
                dBox.style.color = "#00ff00"; // Green
            } else {
                dBox.style.color = "#00ccff"; // Blue
            }

            // 4. AMBULANCE LOGIC
            const alert = document.getElementById('amb-alert');
            const locBox = document.getElementById('amb-loc');

            if (data.amb) {
                alert.style.display = 'block';
                locBox.innerText = `TRACKING ID #A1: ${data.amb_loc}`;

                // Blink the border for effect
                alert.style.borderColor = (Date.now() % 1000 < 500) ? "red" : "yellow";
            } else {
                alert.style.display = 'none';
            }
        })
        .catch(e => console.log("Connection lost..."));
}, 200); // Poll faster (200ms) so the jittery numbers look smooth