import React, { useState } from 'react';

function App() {
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('');
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState('');

  const fetchWeather = async () => {
    if (!city.trim() || !country.trim()) {
      setError('Please enter both city and country');
      setWeather(null);
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/weather?city=${encodeURIComponent(city)}&country=${encodeURIComponent(country)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch');
      }

      const data = await response.json();
      setWeather(data);
      setError('');
    } catch (err) {
      setWeather(null);
      setError('Could not retrieve weather data.');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Weather App 🌤️</h1>
      <input
        type="text"
        placeholder="City"
        value={city}
        onChange={e => setCity(e.target.value)}
      />
      <input
        type="text"
        placeholder="Country"
        value={country}
        onChange={e => setCountry(e.target.value)}
      />
      <button onClick={fetchWeather}>Get Weather</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {weather && (
        <div style={{ marginTop: 20 }}>
          <p>🌡️ Temperature: {weather.temperature_today}°C</p>
          <p>💧 Humidity: {weather.humidity_today}%</p>
          <p>🌅 Morning Temp: {weather.temperature_today_morning}°C</p>
          <p>🌇 Evening Temp: {weather.temperature_today_evening}°C</p>
          <p>🌫️ Morning Humidity: {weather.humidity_today_morning}%</p>
          <p>🌫️ Evening Humidity: {weather.humidity_today_evening}%</p>
          <h3>📅 Weekly Forecast:</h3>
          <ul>
            {weather.weekly_forecast.map((dayData, idx) => (
              <li key={idx}>
                <strong>{dayData.day}</strong>: 🌅 {dayData.temp_morning}°C, 🌇 {dayData.temp_evening}°C, 💧 Morning Humidity: {dayData.humidity_morning}%, 💧 Evening Humidity: {dayData.humidity_evening}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
