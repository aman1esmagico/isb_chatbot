import React, {useEffect, useState} from 'react';
import './index.css'; // Assuming you have an App.css file
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Chat from './chat';
import Login from './login';

function App() {
    const [userName, setUserName] = useState<string>("")

  useEffect(() => {
    setUserName(localStorage.getItem("name") || "")
  }, [userName]);

  return (
      <div className={'flex flex-col h-screen relative overflow-hidden'}>
          {userName ? <Chat /> : <Login />}
      </div>
  );
}

export default App;