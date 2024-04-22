"use client";
import { LoadingSpinner } from "@/app/(authenticated)/components";
import fetchRequest from "@/app/(authenticated)/utils";
import { _BACK_URL, apis, urls } from "@/app/urls";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useInView } from "react-intersection-observer";

export default function userPreview({ params }) {
  const [userData, setUserData] = useState({});
  const [page, setPage] = useState(1);
  const [posts, setPosts] = useState([]);
  const [reloadRequired, setReloadRequired] = useState(false);
  const [ref, inView] = useInView(0);
  const router = useRouter();

  const getData = async () => {
    const res = await fetchRequest(
      `${apis.userData}${params.username}/?page=${page}`,
      "GET"
    );
    const data = await res.json();
    if (res.ok) {
      setUserData(data);
      setPosts([...posts, ...data.posts]);
      setPage(page + 1);
    } else if (res.redirected) {
      router.push(urls.login);
      return;
    } else if (res.status === 404 && data.error === "emptyPage") {
      const button = document.getElementById("reload-button");
      const spinner = document.getElementById("ref");
      button && button.remove();
      spinner && spinner.remove();
    } else if (res.status === 404 && data.detail === "Not found.") {
      router.push(urls.dashboard);
      return;
    } else {
      setReloadRequired(true);
      document.getElementById("ref").classList.add("hidden");
    }
  };

  useEffect(() => {
    if (inView) {
      console.log(`fetching posts again, page number ${page}`);
      getData();
    }
  }, [inView, page, reloadRequired]);

  return (
    <div>
      <div className="flex flex-row mb-10 justify-center">
        <Image
          src={userData.profile ? userData.profile : apis.notFound}
          width={100}
          height={100}
          style={{ borderRadius: "50%", height: 100 }}
        ></Image>
        <div className="flex flex-col gap-5">
          <UserTextData userData={userData} />
        </div>
      </div>
      <UserPosts posts={posts} />
      <div className="ml-72">
        <div
          id="ref"
          ref={(e) => !reloadRequired && ref(e)}
          className="justify-center pt-2"
        >
          <LoadingSpinner />
        </div>
        <button
          className={`${
            reloadRequired ? "visible" : "hidden"
          } flex items-center px-4 py-2 font-medium tracking-wide text-white capitalize transition-colors duration-300 transform bg-indigo-600 rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring focus:ring-indigo-300 focus:ring-opacity-80`}
          onClick={() => {
            setReloadRequired(false);
            document.getElementById("ref").classList.remove("hidden");
          }}
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
      </div>
    </div>
  );
}

function UserTextData({ userData }) {
  const eachRowClass = "flex flex-col text-md gap-y-5 text-white";

  return (
    <>
      <div className="flex flex-row gap-5 mx-10">
        <div id="first-row" className={eachRowClass}>
          <span>{userData.userName}</span>
          <span>{userData.totalPosts} posts</span>
        </div>
        <div id="second-row" className={eachRowClass}>
          <span>Followings</span>
          <span>{userData.totalFollowings} Followings</span>
        </div>
        <div id="third-row" className={eachRowClass}>
          <span>Message</span>
          <span>{userData.totalFollowers} Followers</span>
        </div>
      </div>
      <div className="text-white ml-10">{userData.nickName}</div>
      <div className="text-white ml-10">{userData.biography}</div>
    </>
  );
}

function UserPosts({ posts }) {
  const postsData = posts?.map((post) => {
    return post.files[0].contentType !== "VID" ? (
      <Image
        src={`${_BACK_URL}${post?.files[0]?.content}`}
        width={200}
        height={200}
        style={{ position: "relative", width: "250px", height: "250px" }}
      />
    ) : (
      <video
        src={`${_BACK_URL}${post.files[0].content}`}
        className="hover:border-x-white hover:border"
        style={{ position: "relative", width: "250px", height: "250px" }}
      >
        <source src={`${_BACK_URL}${post.files[0].content}`} type="video/mp4" />
      </video>
    );
  });
  return (
    <div className="justify-center max-w-full grid grid-cols-3 gap-1 border-t border-borderDefault py-10">
      {postsData}
    </div>
  );
}
