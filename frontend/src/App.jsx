import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Chat from './pages/Chat';
import './App.css';
function App() {
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  useEffect(() => {
    if (token) localStorage.setItem('access_token', token);
    else localStorage.removeItem('access_token');
  }, [token]);
  if (!token) return <Login setToken={setToken} />;
  return <Chat token={token} />;
}
export default App;
