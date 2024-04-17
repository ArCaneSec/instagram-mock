"use client";
import Cookies from "universal-cookie";

const fetchRequest = async (url, method, body) => {
  const cookies = new Cookies();
  return await fetch(url, {
    method: method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "x-csrftoken": cookies.get("csrftoken"),
    },
    body: body ? body : null,
  });
};

export default fetchRequest;
