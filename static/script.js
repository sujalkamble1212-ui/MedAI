function toggleTheme() {
    document.body.classList.toggle("dark-mode");
}

let allSymptoms = [];

async function loadSymptoms() {
    const response = await fetch("/symptoms");
    allSymptoms = await response.json();

    displaySymptoms(allSymptoms);
}

function displaySymptoms(symptoms) {
    const container = document.getElementById("symptoms-list");
    container.innerHTML = "";

    symptoms.forEach(symptom => {
        const wrapper = document.createElement("div");
        wrapper.className = "symptom-item";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = symptom;

        const label = document.createElement("label");
        label.htmlFor = symptom;
        label.innerText = " " + symptom.replace(/_/g, " ");

        wrapper.appendChild(checkbox);
        wrapper.appendChild(label);

        container.appendChild(wrapper);
    });
}

document.getElementById("searchInput").addEventListener("input", function () {
    const searchValue = this.value.toLowerCase();
    const filtered = allSymptoms.filter(symptom =>
        symptom.toLowerCase().includes(searchValue)
    );
    displaySymptoms(filtered);
});

async function predictDisease() {
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("result");

    loading.classList.remove("hidden");
    resultBox.innerText = "";

    const data = {};

    allSymptoms.forEach(symptom => {
        const checkbox = document.getElementById(symptom);
        data[symptom] = checkbox && checkbox.checked ? 1 : 0;
    });

    const response = await fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    loading.classList.add("hidden");
    resultBox.innerText = "Predicted Disease: " + result.predicted_disease;
}

window.onload = loadSymptoms;
