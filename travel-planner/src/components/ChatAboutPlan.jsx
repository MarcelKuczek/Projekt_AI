import { useState } from "react";
import "./ChatAboutPlan.css"

function ChatWithPlan({ plan }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const newHistory = [
      ...history,
      { role: "user", content: question }
    ];

    setHistory(newHistory);
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        plan: plan,
        history: newHistory,
        question: question
      })
    });

    const data = await res.json();

    setHistory([
      ...newHistory,
      { role: "assistant", content: data.answer }
    ]);

    setQuestion("");
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <h3>💬 Zapytaj o plan podróży</h3>

      <div className="chat-box">
        {history.map((msg, index) => (
          <div
            key={index}
            className={msg.role === "user" ? "chat-user" : "chat-bot"}
          >
            <strong>{msg.role === "user" ? "Ty" : "Bot"}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}

        {loading && <p>Bot pisze...</p>}
      </div>

      <form onSubmit={sendQuestion}>
        <textarea
          placeholder="Zadaj pytanie o plan..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit">Wyślij</button>
      </form>
    </div>
  );
}

export default ChatWithPlan;
