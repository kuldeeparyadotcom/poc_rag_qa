import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [threshold, setThreshold] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Not a good practice to hardcode the URL, it is just for quick  poc purpose
      const uploadResponse = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log(uploadResponse.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAsk = async () => {
    try {
      // Not a good practice to hardcode the URL, it is just for quick  poc purpose
      const response = await axios.post("http://localhost:8000/ask", { question, threshold });
      if (response.data.answer) {
        setAnswer(response.data.answer);
        setError("");
      } else {
        setError("This question is outside the scope of the document.");
        setAnswer("");
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-5">PDF Question Answering System</h1>
      <div className="mb-5">
        <input type="file" onChange={handleFileUpload} className="mb-2" />
        <button onClick={handleSubmit} className="bg-blue-500 text-white p-2 rounded">
          Upload PDF
        </button>
      </div>
      <div className="mb-5">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
          className="p-2 border rounded"
        />
        <input
          type="text"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          placeholder="Set similarity threshold"
          className="p-2 border rounded"
        />
        <button onClick={handleAsk} className="bg-green-500 text-white p-2 rounded ml-2">
          Ask
        </button>
      </div>
      {answer && <div className="mt-5"><strong>Answer:</strong> {answer}</div>}
      {error && <div className="mt-5 text-red-500">{error}</div>}
    </div>
  );
}

export default App;