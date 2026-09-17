import { useState } from "react"

function Login({ onLoginSuccess }) {

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)


  const handleLogin = async (event) => {

    event.preventDefault()

    setMessage("")
    setLoading(true)

    console.log("LOGIN BUTTON CLICKED")

    try {

      console.log("Sending login request...")
      console.log("LOGIN EMAIL:", email)

      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            email: email,
            password: password
          })
        }
      )


      console.log(
        "Response status:",
        response.status
      )


      const data = await response.json()


      console.log(
        "Response data:",
        data
      )


      // Login failed
      if (!response.ok) {

        setMessage(
          data.detail || "Login failed"
        )

        return
      }


      // =========================
      // SAVE LOGIN INFORMATION
      // =========================

      localStorage.setItem(
        "access_token",
        data.access_token
      )

      localStorage.setItem(
        "user_id",
        data.user_id
      )

      localStorage.setItem(
        "username",
        data.username
      )

      localStorage.setItem(
        "email",
        data.email
      )


      console.log(
        "Login successful!"
      )


      // =========================
      // MOVE TO DASHBOARD
      // =========================

      if (onLoginSuccess) {

        onLoginSuccess(data)

      }

    }

    catch (error) {

      console.error(
        "LOGIN ERROR:",
        error
      )

      setMessage(
        "Cannot connect to RepoRescue backend."
      )

    }

    finally {

      setLoading(false)

    }

  }


  return (

    <div>

      <h1>
        RepoRescue Login
      </h1>


      <form onSubmit={handleLogin}>

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


        <button
          type="submit"
          disabled={loading}
        >

          {loading
            ? "Logging in..."
            : "Login"
          }

        </button>

      </form>


      {message && (

        <p>
          {message}
        </p>

      )}

    </div>

  )
}


export default Login