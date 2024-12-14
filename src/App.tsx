import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './routes/MainPage';
import Leaderboard from './routes/Leaderboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
      </Routes>
    </Router>
  )
}

export default App