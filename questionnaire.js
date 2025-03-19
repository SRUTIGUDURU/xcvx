document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    // Hobby and Topic Lists
    const hobbiesList = [
        "coding", "reading", "watching stuff", "crocheting", "drawing/painting",
        "singing", "writing", "musical instruments", "tennis", "football", "basketball", "badminton",
        "squash", "volleyball", "throwball"
    ];

    const topicsList = [
        "fashion", "clubs/departments", "politics", "pop culture", "world wars",
        "history", "cricket", "Football (as a topic)", "current affairs"
    ];

    const hobbiesContainer = document.getElementById('hobbies-container');
    const topicsContainer = document.getElementById('topics-container');

    if (!hobbiesContainer || !topicsContainer) {
        console.error('Checkbox container elements not found');
        return;
    }

    function createCheckboxes(container, items, name) {
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'checkbox-group';
            div.innerHTML = `
                <input type="checkbox" id="${item}" name="${name}" value="${item}">
                <label for="${item}">${item}</label>
            `;
            container.appendChild(div);
        });
        console.log(`Checkboxes created for ${name}`);
    }

    createCheckboxes(hobbiesContainer, hobbiesList, 'hobbies');
    createCheckboxes(topicsContainer, topicsList, 'topics');

    // Handle form submission
    document.getElementById('questionnaireForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            email: document.getElementById('name').value,
            gender: document.getElementById('gender').value,
            year: document.getElementById('year').value,
            purpose: document.getElementById('purpose').value,
            hobbies: Array.from(document.querySelectorAll('input[name="hobbies"]:checked'))
                .map(cb => cb.value)
                .join(','),
            topics: Array.from(document.querySelectorAll('input[name="topics"]:checked'))
                .map(cb => cb.value)
                .join(',')
        };

        try {
            const response = await fetch('/submit_questionnaire/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                // Store email in localStorage for future use
                localStorage.setItem('userEmail', formData.email);
                alert('Questionnaire submitted successfully! You will be matched with groups soon.');
                window.location.href = 'chat-groups.html';
            } else {
                throw new Error('Failed to submit questionnaire');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit questionnaire. Please try again.');
        }
    });
});
