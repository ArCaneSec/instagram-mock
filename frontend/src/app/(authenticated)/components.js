"use client";
import { _BACK_URL, apis, urls } from "@/app/urls";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useInView } from "react-intersection-observer";
import fetchRequest from "./utils";

export default function Timeline() {
  const [timeLinePosts, setTimeLinePosts] = useState([]);
  const [ref, inView] = useInView(1);
  const [reloadRequired, setReloadRequired] = useState(false);
  const router = useRouter();

  const fetchRequests = async () => {
    try {
      const res = await fetchRequest(apis.timeline, "GET");
      if (!res.ok) {
        router.push(urls.login);
        return;
      }
      return await res.json();
    } catch (e) {
      setReloadRequired(true);
      console.log("request timed out");
    }
  };

  const fetchTimeline = async () => {
    try {
      const responses = await Promise.all([fetchRequests(), fetchRequests()]);
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

  const refresh = () => {
    console.log("refresh called");
    setReloadRequired(false);
    fetchTimeline();
  };

  useEffect(() => {
    if (inView) {
      console.log("fetching time line once again");
      fetchTimeline();
    }
  }, [inView]);

  return (
    <main id="timeline" className="flex flex-col items-center">
      <TimelinePosts posts={timeLinePosts} />
      <div ref={ref} className="justify-center pt-2">
        {reloadRequired ? (
          <RefreshButton refresh={refresh} />
        ) : (
          <LoadingSpinner />
        )}
      </div>
    </main>
  );
}

function Post({ post }) {
  const [currentFile, setCurrentFile] = useState(0);
  const setFile = (currentFile, totalFiles) => {
    if (currentFile >= totalFiles) {
      setCurrentFile(totalFiles - 1);
      return;
    } else if (currentFile <= 0) {
      setCurrentFile(0);
      return;
    }
    setCurrentFile(currentFile);
  };

  return (
    <li
      key={post.id}
      className="text-white text-md border-b border-borderDefault pb-2"
    >
      <div className="flex flex-row gap-2 items-center mb-2">
        <span>
          <Image
            src={post.user.profile ? post.user.profile : apis.notFound}
            width={50}
            height={50}
            alt={post.user.username}
            className="rounded-full"
          ></Image>
        </span>
        <div className="flex flex-col">
          <Link
            className="font-semibold"
            href={`${_BACK_URL}/users/${post.user.username}/`}
          >
            {post.user.username}{" "}
          </Link>
          <span>{post.user.nickname}</span>
        </div>
      </div>
      <div className="relative flex flex-col justify-center">
        {post.files[currentFile].contentType != "VID" ? (
          <Image
            src={`${_BACK_URL}${post.files[currentFile].content}`}
            width={400}
            height={400}
            alt={post.files[currentFile].content}
          />
        ) : (
          <video
            src={`${_BACK_URL}${post.files[currentFile].content}`}
            width={400}
            height={400}
            controls
          >
            <source
              src={`${_BACK_URL}${post.files[currentFile].content}`}
              type="video/mp4"
            />
          </video>
        )}
        <Image
          src={"left-arrow.svg"}
          width={30}
          height={30}
          className={
            currentFile ? "absolute left-3 dark:invert opacity-25" : "hidden"
          }
          onClick={() => setFile(currentFile - 1, post.files.length)}
        ></Image>
        <Image
          src={"right-arrow.svg"}
          width={30}
          height={30}
          className={
            currentFile + 1 < post.files.length
              ? "absolute right-3 dark:invert opacity-25"
              : "hidden"
          }
          onClick={() => setFile(currentFile + 1, post.files.length)}
        ></Image>
      </div>
      <div>{post.caption}</div>
    </li>
  );
}

function TimelinePosts({ posts }) {
  const timelinePosts = posts.map((post) => {
    return <Post post={post} />;
  });

  return <ul className="flex flex-col gap-y-2">{timelinePosts}</ul>;
}

export function LoadingSpinner() {
  return (
    <div role="status">
      <svg
        aria-hidden="true"
        className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-gray-400"
        viewBox="0 0 100 101"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
          fill="currentColor"
        />
        <path
          d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
          fill="currentFill"
        />
      </svg>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export function RefreshButton({ refresh }) {
  return (
    <button
      className={
        "flex items-center px-4 py-2 font-medium tracking-wide text-white capitalize transition-colors duration-300 transform bg-indigo-600 rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring focus:ring-indigo-300 focus:ring-opacity-80"
      }
      onClick={refresh}
      id="reload-button"
    >
      <svg
        className="w-5 h-5 mx-1"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
          clip-rule="evenodd"
        />
      </svg>

      <span class="mx-1">Refresh</span>
    </button>
  );
}
