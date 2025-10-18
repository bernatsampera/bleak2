import "./App.css";
import Chat from "./components/Chat2";
import {ThreadProvider} from "./contexts/ThreadContext";

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
