import { useState } from "react"

function Signup({ onLogin }) {
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSignup = async (event) => {
    event.preventDefault()

    setMessage("")
    setLoading(true)

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            username: username,
            email: email,
            password: password
          })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.detail || "Signup failed")
        return
      }

      setMessage("Account created successfully! Please login.")

      setUsername("")
      setEmail("")
      setPassword("")

    } catch (error) {
      setMessage(
        "Cannot connect to RepoRescue backend."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>RepoRescue Signup</h1>

      <form onSubmit={handleSignup}>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(event) =>
            setUsername(event.target.value)
          }
          required
        />

        <br />
        <br />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) =>
            setEmail(event.target.value)
          }
          required
        />

        <br />
        <br />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) =>
            setPassword(event.target.value)
          }
          required
        />

        <br />
        <br />

        <button type="submit" disabled={loading}>
          {loading ? "Creating Account..." : "Create Account"}
        </button>

      </form>

      {message && (
        <p>{message}</p>
      )}

      <p>
        Already have an account?{" "}
        <button onClick={onLogin}>
          Login
        </button>
      </p>
    </div>
  )
}

export default Signup