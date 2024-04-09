"use client";

export default function LoginForm() {
  const login = async () => {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    let res = await fetch("http://localhost:8000/users/login/", {
      method: "POST",
      headers: {
        "Content-Type": "Application/json",
      },
      body: JSON.stringify({ username:username, password:password }),
    });
    console.log(res);
  };

  return (
    <div class="h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div class="bg-white border border-gray-300 w-80 py-8 flex items-center flex-col mb-3">
        <h1 class="bg-no-repeat instagram-logo"></h1>
        <form class="mt-8 w-64 flex flex-col">
          <input
            autofocus
            class="text-xs w-full mb-2 rounded border bg-gray-100 border-gray-300 px-2 py-2 focus:outline-none focus:border-gray-400 active:outline-none text-black"
            id="username"
            placeholder="Username"
            type="text"
          />
          <input
            autofocus
            class="text-xs w-full mb-4 rounded border bg-gray-100 border-gray-300 px-2 py-2 focus:outline-none focus:border-gray-400 active:outline-none text-black"
            id="password"
            placeholder="Password"
            type="password"
          />
          <a
            class=" text-sm text-center bg-blue-300 text-white py-1 rounded font-medium"
            onClick={() => login()}
          >
            Log In
          </a>
        </form>
      </div>
    </div>
  );
}
