async function generateSuggestions(event) {
    event.preventDefault();

    const eventType = document.getElementById('event-type').value;
    const eventDate = document.getElementById('event-date').value;
    const eventTime = document.getElementById('event-time').value;
    const formality = document.getElementById('formality').value;
    const city = document.getElementById('city').value;
    const country = document.getElementById('country').value;
    const avoidDays = document.getElementById('avoid-days').value;
    const gender = document.getElementById('gender').value;

    const params = new URLSearchParams({
        event_type: eventType,
        event_date: eventDate,
        event_time: eventTime,
        formality: formality,
        city: city,
        country: country,
        avoid_days: avoidDays,
        gender: gender
    });

    document.getElementById('loading-state').style.display = 'block';
    document.getElementById('results-container').style.display = 'none';

    try {
        const response = await SmartStyle.apiRequest(`/api/outfit/suggest?${params.toString()}`);
        if (response.success) {
            displaySuggestions(response.suggestions);
        } else {
            SmartStyle.showAlert(response.message, 'error');
        }
    } catch (error) {
        SmartStyle.showAlert('Failed to generate suggestions: ' + error.message, 'error');
    } finally {
        document.getElementById('loading-state').style.display = 'none';
    }
}

function displaySuggestions(suggestionsText) {
    const container = document.getElementById('results-container');
    const display = document.getElementById('suggestions-text');
    display.textContent = suggestionsText;
    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    SmartStyle.showAlert('✨ Your outfit suggestions are ready!', 'success');
}

document.addEventListener('DOMContentLoaded', () => {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];
    document.getElementById('event-date').value = dateStr;
    document.getElementById('event-time').value = '18:00';
});
