import React, { useState } from 'react';
import QuantumSynth from './components/QuantumSynth';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🎹 Quantum Synth</h1>
        <p>Audio synthesis powered by quantum circuits</p>
      </header>
      <main>
        <QuantumSynth />
      </main>
      <footer>
        <p>Built with quantumaudio + Qiskit + Django + React</p>
      </footer>
    </div>
  );
}

export default App;
