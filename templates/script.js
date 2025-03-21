document.getElementById("summarizationForm").addEventListener("submit", async function(event) {
    event.preventDefault();  // Prevent default form submission

    let formData = new FormData(this);

    let response = await fetch("/process", {
        method: "POST",
        body: formData
    });

    let result = await response.text();
    document.getElementById("result").innerHTML = "<h3>Output:</h3><p>" + result + "</p>";
});
