"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useInView } from "react-intersection-observer";
import Cookies from "universal-cookie";
import { apis } from "./urls";

export default function Timeline() {
  const [timeLinePosts, setTimeLinePosts] = useState([]);
  const [ref, inView] = useInView(1);
  const cookies = new Cookies();

  const fetchRequest = async () => {
    return await fetch(apis.timeline, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "x-csrftoken": cookies.get("csrftoken"),
      },
    }).then(async (res) => await res.json());
  };

  const fetchTimeline = async () => {
    try {
      const responses = await Promise.all([fetchRequest(), fetchRequest()]);
      const packResponses = () => {
        const final = [];
        responses.map((res) => final.push(...res));
        return final;
      };
      setTimeLinePosts([...timeLinePosts, ...packResponses()]);
    } catch (e) {
      console.log(e);
    }
  };

  useEffect(() => {
    if (inView) {
      console.log("fetching time line once again");
      fetchTimeline();
    }
  }, [inView]);

  const posts = timeLinePosts.map((post) => {
    return <Post post={post} />;
  });

  return (
    <>
      <div id="timeline" className="flex flex-col">
        <ul className="flex flex-col gap-y-8">{posts}</ul>
        <div className="text-2xl text-red-500" ref={ref}>
          LOADING
        </div>
      </div>
    </>
  );
}

function Post({ post }) {
  return (
    <li key={post.id} className="text-white text-md border-b pb-2">
      <div className="flex flex-row gap-2 items-center">
        <span>
          <Image
            src={
              post.user.profile
                ? post.user.profile
                : "http://localhost:8000/static/not_found.png/"
            }
            width={50}
            height={50}
            className="rounded-full"
          ></Image>
        </span>
        <div className="flex flex-col mb-2">
        <span className="font-semibold">{post.user.username}</span>
        <span>{post.user.nickname}</span>
        </div>
      </div>
      {post.files.map((file) => (
        <Image
          src={"http://localhost:8000" + file.content}
          width={400}
          height={400}
          alt="test"
        />
      ))}
      <div>{post.caption}</div>
    </li>
  );
}
