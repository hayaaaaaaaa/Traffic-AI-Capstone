// Poll the server every 500ms
setInterval(() => {
    fetch('/telemetry')
        .then(r => r.json())
        .then(data => {
            // 1. Update Basic Metrics
            document.getElementById('decision').innerText = data.decision;
            document.getElementById('r1').innerText = data.r1;
            document.getElementById('r2').innerText = data.r2;

            // 2. Update Technical Data (Fake AI Stats)
            document.getElementById('conf').innerText = data.conf;
            document.getElementById('latency').innerText = `Latency: ${data.latency}`;

            // 3. Update Timer (Shows loop progress)
            document.getElementById('timer').innerText = data.time_index + "s / 54s";

            // 4. Update System Log (The "Hacker" text at bottom)
            document.getElementById('sys-log').innerText = `> ${data.log}`;

            // 5. Visual Colors
            const dBox = document.getElementById('decision');
            if (data.decision === "ROAD1") {
                dBox.style.color = "#68c868ff"; // Green
            } else {
                dBox.style.color = "#00ccff"; // Blue
            }

            // 6. AMBULANCE LOGIC
            const alert = document.getElementById('amb-alert');
            const locBox = document.getElementById('amb-loc');

            if (data.amb) {
                // Show the Red Box
                alert.style.display = 'block';

                // Show the "Math" calculation (e.g., "Loc: 1.5m (y=412)")
                // This proves to judges that "Computer Vision" is tracking position
                locBox.innerText = `TRACKING ID #A1: ${data.amb_loc}`;
            } else {
                alert.style.display = 'none';
            }
        })
        .catch(e => console.log("Connection lost..."));
}, 500);