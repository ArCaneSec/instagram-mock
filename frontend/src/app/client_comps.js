"use client";
import { useEffect, useState } from "react";
import Cookies from "universal-cookie";
import { _BACK_URL, apis } from "./urls";

export default function Timeline() {
  const [timeLinePosts, setTimeLinePosts] = useState([]);
  const cookies = new Cookies();

  const fetchTimeline = async () => {
    try {
      const res = await fetch(apis.timeline, {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "x-csrftoken": cookies.get("csrftoken"),
        },
      });
      setTimeLinePosts(await res.json());
    } catch (e) {
      console.log(e);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, []);

  const posts = timeLinePosts.map((post) => {
    return (
      <li key={post.id}>
        <div>{post.user.username}</div>
        {post.files.map((file) => (
          <Image src={"http://localhost:8000/"+file.content} />
        ))}
        <div>{post.caption}</div>
      </li>
    );
  });

  return (
    <div id="timeline">
      <ul>{posts}</ul>
    </div>
  );
}
