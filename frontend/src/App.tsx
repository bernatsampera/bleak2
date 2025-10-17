import {useState} from "react";
import "./App.css";
import Chat from "./components/Chat";
import { ThreadProvider } from "./contexts/ThreadContext";

function App() {
  return (
    <ThreadProvider>
      <div className="bg-yellow-400">
        <Chat />
      </div>
    </ThreadProvider>
  );
}

export default App;
