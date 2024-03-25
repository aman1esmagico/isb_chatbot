import React, { useState } from 'react';
import './login.css'; // Add your CSS file

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');



  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch('http://ivi_isb_backend.esmagico.net/api/user/login/', { // Your API endpoint
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: username, password: password }),
      });

      if (response.ok) {
        const data = await response.json(); // Assuming the API returns data
        localStorage.setItem('name', data.name); // Example storage
        localStorage.setItem('userId', data.id); // Example storage
        // Redirect to a different page if successful
        window.location.href = '/chat'; // Update with your desired route
      } else {
        // Handle failed login (e.g., display an error message)
        console.error('Login failed:', response.status);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" >Login</button>
      </form>
    </div>
  );
}

export default Login;
