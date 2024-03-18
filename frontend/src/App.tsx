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
      <>
          {userName ? <Chat /> : <Login />}
      </>
  );
}

export default App;