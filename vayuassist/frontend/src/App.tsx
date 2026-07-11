import { useState, useEffect } from 'react';
import './App.css';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [userProfile, setUserProfile] = useState<any>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
      loadUserProfile(storedToken);
    }
  }, []);

  const loadUserProfile = async (authToken: string) => {
    try {
      const response = await fetch('http://localhost:8001/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (response.ok) {
        const profile = await response.json();
        setUserProfile(profile);
        setUserId(profile.id);
      } else {
        handleLogout();
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleLoginSuccess = (loginToken: string, userId: string) => {
    localStorage.setItem('token', loginToken);
    setToken(loginToken);
    setUserId(userId);
    setIsAuthenticated(true);
    loadUserProfile(loginToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUserId(null);
    setUserProfile(null);
    setIsAuthenticated(false);
  };

  return (
    <div className="app-container">
      {!isAuthenticated ? (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      ) : (
        <ChatPage 
          token={token!} 
          userId={userId}
          userProfile={userProfile}
          onLogout={handleLogout}
          onProfileUpdate={setUserProfile}
        />
      )}
    </div>
  );
}

export default App;
