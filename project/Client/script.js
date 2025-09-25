// Wrap all your JS code in this event
document.addEventListener('DOMContentLoaded', function() {
    const preview = document.getElementById('preview');
    const resultsDiv = document.getElementById('results');
    const imageInput = document.getElementById('imageInput');

    // Show image preview when a file is selected
    imageInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            preview.src = URL.createObjectURL(file);
            preview.style.display = 'block';
            resultsDiv.innerText = ""; // clear previous results
        }
    });

    // Upload image to backend and display predictions
    async function uploadImage() {
        const file = imageInput.files[0];
        if (!file) {
            alert("Please select an image first!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:5000/detectPest", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                resultsDiv.innerText = error.error;
                return;
            }

            const data = await response.json();

            // Display results
            if (Object.keys(data).length === 0) {
                resultsDiv.innerText = "No pests detected!";
            } else {
                let text = "Detected pests:\n";
                for (const [pest, count] of Object.entries(data)) {
                    text += `${pest}: ${count}\n`;
                }
                resultsDiv.innerText = text;
            }
        } catch (err) {
            resultsDiv.innerText = "Error detecting pests. Please try again.";
            console.error(err);
        }
    }

    // Optional: attach uploadImage to a button click if you have a button
    const uploadBtn = document.getElementById('uploadBtn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', uploadImage);
    }
});
