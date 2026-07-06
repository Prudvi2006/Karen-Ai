import { useState } from "react";
import { Link ,useNavigate } from "react-router-dom";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async(e) => {
    e.preventDefault();

    console.log(form);

    const response = await fetch("http://localhost:8000/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: form.email,
      password: form.password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Invalid email or password");
    return;
  }

  // Save JWT token
  localStorage.setItem("token", data.access_token);

  // Save username (optional)
  localStorage.setItem("username", data.username);

  alert("Login successful!");

  navigate("/dashboard");

  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <h1>Welcome Back 👋</h1>
        <p>Sign in to continue to your AI Assistant</p>

        <form onSubmit={handleSubmit}>

          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
            />
          </div>

          <button className="auth-btn">
            Login
          </button>

        </form>

        <p className="bottom-text">
          Don't have an account?
          <Link to="/signup"> Sign Up</Link>
        </p>

      </div>
    </div>
  );
}
