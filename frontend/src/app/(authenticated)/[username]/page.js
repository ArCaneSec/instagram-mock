"use client";
import {
  LoadingSpinner,
  RefreshButton,
} from "@/app/(authenticated)/components";
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
    try {
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
        const button = document.getElementById("loading");
        button && button.remove();
      } else if (res.status === 404 && data.detail === "Not found.") {
        router.push(urls.dashboard);
        return;
      } else {
        setReloadRequired(true);
      }
    } catch (e) {
      console.log(e);
      setReloadRequired(true);
    }
  };

  const refresh = () => {
    setReloadRequired(false);
    getData();
  };

  useEffect(() => {
    if (inView) {
      console.log(`fetching posts again, page number ${page}`);
      getData();
    }
  }, [inView, page]);

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
      <div className="relative flex justify-center" ref={ref} id="loading">
        {reloadRequired ? (
          <RefreshButton refresh={refresh} />
        ) : (
          <LoadingSpinner />
        )}
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
