import React, { useState } from "react";
import ResumeForm from "./components/ResumeForm";
import ResultsDisplay from "./components/ResultsDisplay";

function App() {
  const [result, setResult] = useState("");

  const handleGenerate = async (experience, tone, job) => {
    const res = await fetch("http://localhost:5000/bullets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ experience, tone, job }),
    });
    const data = await res.json();
    setResult(data.result);
  };

  return (
    <div>
      <h1>AI Resume Assistant</h1>
      <ResumeForm onGenerate={handleGenerate} />
      <ResultsDisplay result={result} />
    </div>
  );
}

export default App;
