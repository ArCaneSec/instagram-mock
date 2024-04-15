"use client";
import { apis, urls } from "@/app/urls";
import { useRouter } from "next/navigation";
import Cookies from "universal-cookie";

export default function LoginForm() {
  const cookies = new Cookies();
  const router = useRouter();
  const login = async (form) => {
    form.preventDefault();
    const username = form.target.elements.username.value;
    const password = form.target.elements.password.value;

    try {
      const res = await fetch(apis.login, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "x-csrftoken": cookies.get("csrftoken"),
        },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        console.log(await res.json());
        return;
      }

      router.push(urls.dashboard);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div className="bg-white border border-gray-300 w-80 py-8 flex items-center flex-col mb-3">
        <h1 className="bg-no-repeat instagram-logo"></h1>
        <form className="mt-8 w-64 flex flex-col" onSubmit={login}>
          <input
            autoFocus
            className="text-xs w-full mb-2 rounded border bg-gray-100 border-gray-300 px-2 py-2 focus:outline-none focus:border-gray-400 active:outline-none text-black"
            id="username"
            placeholder="Username"
            type="text"
          />
          <input
            className="text-xs w-full mb-4 rounded border bg-gray-100 border-gray-300 px-2 py-2 focus:outline-none focus:border-gray-400 active:outline-none text-black"
            id="password"
            placeholder="Password"
            type="password"
          />
          <button
            className=" text-sm text-center bg-blue-300 text-white py-1 rounded font-medium"
            type="submit"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  );
}
