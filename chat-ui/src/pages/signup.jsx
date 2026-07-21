import { useState } from "react";
import { Link , useNavigate } from "react-router-dom";
import "./Login.css";

export default function Signup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    
  });
const API_URL = "https://karen-ai-multimodal-rag-chatbot.onrender.com";
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async(e) => {
    e.preventDefault();

    if (form.password !== form.confirmPassword) {
    alert("Passwords do not match");
    return;
    }
    const response= await fetch(`${API_URL}/signup`, {
     method: "POST",
     headers: {
     "Content-Type": "application/json",
    },
    body: JSON.stringify(form),
    });
   const data = await response.json();
   console.log(data);

    if (!response.ok) {
  alert(data.detail);
  return;
}

    alert("Signup successful!");
navigate("/login");
    
  }

    
  


  return (
    <div className="auth-page">
      <div className="auth-card">

        <h1>Create Account 🚀</h1>
        <p>Join your personal AI Assistant</p>

        <form onSubmit={handleSubmit}>

          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              placeholder="Enter your username"
              value={form.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm your password"
              value={form.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button className="auth-btn">
            Create Account
          </button>

        </form>

        <p className="bottom-text">
          Already have an account?
          <Link to="/login"> Login</Link>
        </p>

      </div>
    </div>
  );
}