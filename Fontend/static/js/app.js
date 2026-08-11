const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const state = {
  children: false,
  elderly: false,
  currentTrip: null,
};

const form = $('#tripForm');
const emptyState = $('#emptyState');
const loadingState = $('#loadingState');
const errorState = $('#errorState');
const tripResults = $('#tripResults');
const generateButton = $('#generateButton');

function setDefaultDate() {
  const dateInput = $('#date');
  if (!dateInput.value) {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    dateInput.value = d.toISOString().slice(0, 10);
  }
}
setDefaultDate();

$$('.segmented').forEach(group => {
  group.addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (!button) return;
    $$('button', group).forEach(b => b.classList.remove('active'));
    button.classList.add('active');
    state[group.dataset.field] = button.dataset.value === 'true';
  });
});

const themeToggle = $('#themeToggle');
const themeIcon = $('#themeIcon');
const storedTheme = localStorage.getItem('wejhatna-theme');
if (storedTheme) document.documentElement.dataset.theme = storedTheme;
updateThemeIcon();

themeToggle.addEventListener('click', () => {
  const current = document.documentElement.dataset.theme;
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('wejhatna-theme', next);
  updateThemeIcon();
});

function updateThemeIcon() {
  themeIcon.textContent = document.documentElement.dataset.theme === 'dark' ? '☀' : '☾';
}

function showOnly(target) {
  [emptyState, loadingState, errorState, tripResults].forEach(el => el.classList.add('hidden'));
  target.classList.remove('hidden');
}

function getInterests() {
  return $$('#interestGrid input:checked').map(input => input.value).join(', ');
}

function buildPayload() {
  return {
    destination: 'Riyadh',
    date: $('#date').value,
    number_of_days: Number($('#number_of_days').value),
    number_of_people: Number($('#number_of_people').value),
    children: state.children,
    elderly: state.elderly,
    accessibility_requirements: $('#accessibility_requirements').value.trim() || 'none',
    budget: $('#budget').value,
    interests: getInterests() || 'general tourism',
    preferred_start_time: $('#preferred_start_time').value,
    preferred_end_time: $('#preferred_end_time').value,
  };
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = buildPayload();
  showOnly(loadingState);
  generateButton.disabled = true;
  generateButton.innerHTML = '<span class="button-spark">✦</span> Planning…';
  errorState.classList.add('hidden');
  tripResults.innerHTML = '';

  try {
    const response = await fetch('/api/plan-trip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || data.message || 'The agent returned an error.');
    state.currentTrip = data;
    renderTrip(data, payload);
    showOnly(tripResults);
    tripResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    $('#errorMessage').textContent = error.message || 'Please try again.';
    showOnly(errorState);
  } finally {
    generateButton.disabled = false;
    generateButton.innerHTML = '<span class="button-spark">✦</span> Generate my trip';
  }
});

function renderTrip(trip, request) {
  tripResults.innerHTML = '';

  const overview = document.createElement('section');
  overview.className = 'trip-overview card';
  overview.innerHTML = `
    <div>
      <span class="section-kicker">YOUR SMART TRIP</span>
      <h3>${escapeHtml(trip.destination || 'Riyadh')} · ${trip.number_of_days || request.number_of_days} ${pluralize(trip.number_of_days || request.number_of_days, 'day')}</h3>
    </div>
    <div class="trip-overview-meta">
      <span class="meta-chip">${request.number_of_people} ${pluralize(request.number_of_people, 'traveler')}</span>
      <span class="meta-chip">${capitalize(request.budget)} budget</span>
      <span class="meta-chip">${escapeHtml(request.interests)}</span>
    </div>`;
  tripResults.appendChild(overview);

  const days = Array.isArray(trip.days) ? trip.days : [];
  if (!days.length) {
    const fallback = document.createElement('section');
    fallback.className = 'error-state card';
    fallback.innerHTML = '<div class="error-icon">!</div><div><h3>No day plan returned</h3><p>The API response did not include a <code>days</code> array.</p></div>';
    tripResults.appendChild(fallback);
    return;
  }

  const tabs = document.createElement('nav');
  tabs.className = 'day-tabs';
  tabs.setAttribute('aria-label', 'Trip days');
  days.forEach((day, index) => {
    const button = document.createElement('button');
    button.className = `day-tab${index === 0 ? ' active' : ''}`;
    button.type = 'button';
    button.textContent = `Day ${index + 1} · ${formatShortDate(day.date)}`;
    button.addEventListener('click', () => {
      $$('.day-tab', tabs).forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      document.getElementById(`day-${index + 1}`).scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    tabs.appendChild(button);
  });
  tripResults.appendChild(tabs);

  days.forEach((day, index) => tripResults.appendChild(renderDay(day, index)));
}

function renderDay(day, index) {
  const template = $('#dayTemplate').content.cloneNode(true);
  const card = $('.day-card', template);
  card.id = `day-${index + 1}`;
  $('.day-number', template).textContent = `DAY ${index + 1}`;
  $('.day-date', template).textContent = formatLongDate(day.date);

  const weather = day.weather || {};
  $('.day-weather-badge', template).textContent = weather.forecast_type ? `${capitalize(weather.forecast_type)} weather` : 'Weather';

  $('.weather-insight', template).innerHTML = renderWeather(weather);
  $('.prayer-insight', template).innerHTML = renderPrayerTimes(day.prayer_times || {});
  $('.traffic-insight', template).innerHTML = renderTraffic(day.traffic_summary || {});

  const activities = Array.isArray(day.itinerary) ? day.itinerary : [];
  $('.timeline-count', template).textContent = `${activities.length} ${pluralize(activities.length, 'stop')}`;
  const timeline = $('.timeline', template);
  if (!activities.length) {
    timeline.innerHTML = '<p class="section-copy">No activities returned for this day.</p>';
  } else {
    activities.forEach(activity => timeline.appendChild(renderActivity(activity)));
  }
  return template;
}

function renderWeather(weather) {
  const min = valueOrDash(weather.temperature_min_c);
  const max = valueOrDash(weather.temperature_max_c);
  return `
    <div class="insight-title">☀ Weather <span style="color:var(--muted);font-weight:600">${escapeHtml(weather.forecast_type || '')}</span></div>
    <div class="insight-value">${min}° – ${max}°C</div>
    <div class="insight-sub"><strong>${escapeHtml(weather.summary || 'No summary')}</strong><br>${escapeHtml(weather.planning_note || '')}</div>`;
}

function renderPrayerTimes(prayers) {
  const names = [
    ['fajr', 'Fajr'], ['dhuhr', 'Dhuhr'], ['asr', 'Asr'], ['maghrib', 'Maghrib'], ['isha', 'Isha']
  ];
  return `
    <div class="insight-title">◐ Prayer times</div>
    <div class="prayer-grid">
      ${names.map(([key, label]) => `<div class="prayer-row"><span>${label}</span><span>${escapeHtml(prayers[key] || '—')}</span></div>`).join('')}
    </div>`;
}

function renderTraffic(traffic) {
  const probability = traffic.congestion_probability || 'unknown';
  const meterClass = probability.includes('high') ? 'high' : probability.includes('moderate') ? 'moderate' : 'low';
  return `
    <div class="insight-title">🚗 Traffic <span style="color:var(--muted);font-weight:600">${escapeHtml(traffic.traffic_type || '')}</span></div>
    <div class="insight-value" style="font-size:22px">${humanizeProbability(probability)}</div>
    <div class="insight-sub">${escapeHtml(traffic.summary || 'No traffic context available.')}</div>
    <div class="traffic-meter ${meterClass}"><i></i><i></i><i></i><i></i><i></i></div>`;
}

function renderActivity(activity) {
  const row = document.createElement('div');
  row.className = 'activity-row';
  const route = activity.route_to_activity || {};
  const traffic = activity.traffic_to_activity || {};
  row.innerHTML = `
    <div class="activity-time">
      <strong>${escapeHtml(activity.start_time || '—')}</strong>
      <span>to</span>
      <strong>${escapeHtml(activity.end_time || '—')}</strong>
    </div>
    <div class="activity-card">
      <div class="activity-main">
        <span class="activity-type">${escapeHtml(activity.activity_type || 'Activity')}</span>
        <h5 class="activity-name">${escapeHtml(activity.activity_name || 'Unnamed activity')}</h5>
        <p class="activity-reason">${escapeHtml(activity.reason || '')}</p>
      </div>
      <div class="route-panel">
        <div class="route-from">From<strong>${escapeHtml(route.from || 'Unknown origin')}</strong></div>
        <div class="route-stats">
          <span class="route-stat">↗ ${formatDistance(route.distance_km)}</span>
          <span class="route-stat">◷ ${formatMinutes(route.travel_time_minutes)}</span>
        </div>
        <div class="traffic-box">
          <strong>${escapeHtml(humanizeProbability(traffic.congestion_probability || traffic.traffic_level || 'unknown'))}</strong><br>
          ${escapeHtml(traffic.traffic_reason || 'Traffic information unavailable.')}
        </div>
      </div>
    </div>`;
  return row;
}

function formatLongDate(value) {
  if (!value) return 'Unknown date';
  const date = new Date(`${value}T12:00:00`);
  return new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(date);
}
function formatShortDate(value) {
  if (!value) return 'Date';
  const date = new Date(`${value}T12:00:00`);
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(date);
}
function formatDistance(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'Distance unknown';
  return `${Number(value).toFixed(1)} km`;
}
function formatMinutes(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'Time unknown';
  return `${Math.round(Number(value))} min`;
}
function humanizeProbability(value = '') {
  const v = String(value).toLowerCase();
  if (v.includes('high')) return 'High congestion probability';
  if (v.includes('moderate')) return 'Moderate congestion probability';
  if (v.includes('low')) return 'Low congestion probability';
  if (v === 'light') return 'Light traffic';
  if (v === 'heavy') return 'Heavy traffic';
  if (v === 'moderate') return 'Moderate traffic';
  return 'Traffic unknown';
}
function valueOrDash(value) {
  return value === null || value === undefined || value === '' ? '—' : value;
}
function capitalize(value = '') {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : '';
}
function pluralize(count, word) { return Number(count) === 1 ? word : `${word}s`; }
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','"':'&quot;'}[char]));
}
